import argparse
from pathlib import Path
import shutil
import struct
import subprocess
import tempfile
import wave

from sohpacker import _make_resource


BASE_DIR = Path(__file__).resolve().parent
NAVI_FILES = {
    "hello.wav": "Navi - Hello!_META",
    "hey.wav": "Navi - Hey!_META",
    "listen.wav": "Navi - Listen!_META",
    "look.wav": "Navi - Look!_META",
    "watchout.wav": "Navi - Watch Out!_META",
}
_TYPE_AUDIO_SAMPLE = 0x4F534D50  # OSMP


def read_navi_wav(path: Path) -> tuple[bytes, int]:
    with wave.open(str(path), "rb") as wav:
        if (wav.getnchannels(), wav.getsampwidth(), wav.getframerate()) != (1, 2, 16000):
            raise ValueError(f"{path.name}: kräver mono, PCM16, 16000 Hz för Navis befintliga tuning")
        frames = wav.getnframes()
        pcm = wav.readframes(frames)
    if not frames or len(pcm) != frames * 2:
        raise ValueError(f"{path.name}: tom eller avklippt WAV-data")
    return pcm, frames


def parse_aifc(data: bytes, expected_frames: int) -> tuple[bytes, int, int, tuple[int, ...]]:
    """Läs ADP9 och dess egen predictor-book från sampleconvs AIFC."""
    if len(data) < 12 or data[:4] != b"FORM" or data[8:12] != b"AIFC":
        raise ValueError("sampleconv-resultatet är inte en AIFC-fil")
    if struct.unpack_from(">I", data, 4)[0] + 8 != len(data):
        raise ValueError("Felaktig AIFC-längd")

    comm = sound = book = None
    pos = 12
    while pos < len(data):
        if pos + 8 > len(data):
            raise ValueError("Avklippt AIFC-chunkheader")
        tag = data[pos:pos + 4]
        size = struct.unpack_from(">I", data, pos + 4)[0]
        end = pos + 8 + size
        if end + (size & 1) > len(data):
            raise ValueError(f"Avklippt AIFC-chunk: {tag!r}")
        payload = data[pos + 8:end]
        pos = end + (size & 1)

        if tag == b"COMM":
            if comm is not None or len(payload) < 22:
                raise ValueError("Felaktig COMM-chunk")
            channels, frames, bits = struct.unpack_from(">HIH", payload)
            # 16000 Hz som AIFF:s 80-bitars flyttal.
            if (channels, frames, bits) != (1, expected_frames, 16) or payload[8:18] != bytes.fromhex("400cfa00000000000000"):
                raise ValueError("AIFC-format/längd stämmer inte med WAV-filen")
            if payload[18:22] != b"ADP9":
                raise ValueError("AIFC måste innehålla 9-byte VADPCM (ADP9)")
            comm = payload
        elif tag == b"SSND":
            if sound is not None or len(payload) < 8:
                raise ValueError("Felaktig SSND-chunk")
            offset, block_size = struct.unpack_from(">II", payload)
            if block_size != 0 or 8 + offset > len(payload):
                raise ValueError("Felaktig SSND-offset/blockstorlek")
            sound = payload[8 + offset:]
        elif tag == b"APPL" and payload.startswith(b"stoc\x0bVADPCMCODES"):
            if book is not None or len(payload) < 22:
                raise ValueError("Felaktig VADPCMCODES-chunk")
            version, order, predictors = struct.unpack_from(">HHH", payload, 16)
            count = order * predictors * 8
            # SoH:s N64 ADPCM-avkodare använder order 2 och högst 16 predictors.
            if version != 1 or order != 2 or not 1 <= predictors <= 16 or len(payload) != 22 + count * 2:
                raise ValueError("Ogiltig ADPCM predictor-book")
            coefficients = struct.unpack_from(f">{count}h", payload, 22)
            book = order, predictors, coefficients

    if comm is None or sound is None or book is None:
        raise ValueError("AIFC saknar COMM, SSND eller VADPCMCODES")
    size = ((expected_frames + 15) // 16) * 9
    # sampleconv kan räkna med en avslutande nollbyte för jämn chunklängd.
    if len(sound) not in (size, size + (size & 1)) or any(sound[size:]):
        raise ValueError("ADPCM-datalängden stämmer inte med antalet PCM-samples")
    sound = sound[:size]
    order, predictors, coefficients = book
    if any(sound[i] & 0x0F >= predictors for i in range(0, size, 9)):
        raise ValueError("ADPCM-data refererar till en predictor som saknas")
    return sound, order, predictors, coefficients


def make_audio_resource(aifc: bytes, frames: int) -> bytes:
    sound, order, predictors, coefficients = parse_aifc(aifc, frames)
    # AudioSampleFactoryV2: codec/medium/flags, storlek, ADPCM, loop, book.
    payload = struct.pack("<4BI", 0, 0, 0, 0, len(sound)) + sound
    # Engångsljud: slutet är exklusivt, utan loop eller loop-state.
    payload += struct.pack("<4I", 0, frames, 0, 0)
    payload += struct.pack("<iiI", order, predictors, len(coefficients))
    payload += struct.pack(f"<{len(coefficients)}h", *coefficients)
    return _make_resource(_TYPE_AUDIO_SAMPLE, 2, payload)


def find_sampleconv(explicit: Path | None) -> Path:
    if explicit is not None:
        candidates = [explicit]
    else:
        candidates = [BASE_DIR / "sampleconv.exe", BASE_DIR.parent / "navi-replace" / "sampleconv.exe"]
        if found := shutil.which("sampleconv"):
            candidates.append(Path(found))
    for candidate in candidates:
        if candidate.is_file():
            return candidate.resolve()
    raise FileNotFoundError("Hittar inte sampleconv. Ange --sampleconv SÖKVÄG")


def prepare_audio(audio_dir: Path, output_dir: Path, sampleconv: Path) -> None:
    resources = {}
    with tempfile.TemporaryDirectory(prefix="soh-audio-") as temp_dir:
        for source_name, target_name in NAVI_FILES.items():
            pcm, frames = read_navi_wav(audio_dir / source_name)
            wav_path = Path(temp_dir) / source_name
            # En ren PCM-WAV hindrar gammal book/loop-metadata från att följa med.
            with wave.open(str(wav_path), "wb") as wav:
                wav.setparams((1, 2, 16000, frames, "NONE", "not compressed"))
                wav.writeframes(pcm)
            aifc_path = wav_path.with_suffix(".aifc")
            result = subprocess.run(
                [str(sampleconv), "vadpcm", str(wav_path), str(aifc_path)],
                capture_output=True, text=True, errors="replace",
            )
            if result.returncode != 0:
                raise RuntimeError(f"sampleconv misslyckades för {source_name}:\n{result.stdout}\n{result.stderr}")
            resources[target_name] = make_audio_resource(aifc_path.read_bytes(), frames)
            print(f"  {source_name} -> {target_name} ({frames} samples, {len(resources[target_name])} byte)")

    # Alla fem konverteringar ska lyckas innan tidigare färdiga resurser ersätts.
    output_dir.mkdir(parents=True, exist_ok=True)
    for name, resource in resources.items():
        destination = output_dir / name
        with tempfile.NamedTemporaryFile(dir=output_dir, delete=False) as tmp:
            temp_path = Path(tmp.name)
            tmp.write(resource)
        try:
            temp_path.replace(destination)
        finally:
            temp_path.unlink(missing_ok=True)
    print(f"Klart! Färdiga ljudresurser: {output_dir}")
    print("Kör sohpacker.py för att packa dem. Konvertera igen bara när WAV-filerna ändras.")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--sampleconv", type=Path, help="Sökväg till ZeldaRET sampleconv")
    parser.add_argument("--audio-dir", type=Path, default=BASE_DIR / "audio")
    parser.add_argument("--output-dir", type=Path, default=BASE_DIR / "audio" / "soh")
    args = parser.parse_args()
    try:
        prepare_audio(args.audio_dir.resolve(), args.output_dir.resolve(), find_sampleconv(args.sampleconv))
    except (OSError, ValueError, RuntimeError, wave.Error, EOFError) as error:
        print(f"FEL: {error}")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
