import struct
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Optional, Sequence, Tuple

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")

# Kataloger som används av skriptet. Sökvägarna är relativa till projektmappen.
INPUT_DIR = Path("extract")
ROMS_DIR = Path("roms")

FONT_LOAD_ORDERED_FONT_PROLOG = bytes([0x27, 0xBD, 0xFF, 0xC0, 0xAF, 0xB3, 0x00, 0x24])
DEFAULT_FONT_ORDER_DATA = (
    b"0123456789\x01"
    b"ABCDEFGHIJKLMN\x01"
    b"OPQRSTUVWXYZ\x01"
    b"abcdefghijklmn\x01"
    b"opqrstuvwxyz\x01"
    b" -.\x01"
    b"\x02"
)

PAL_LANGUAGE_ROM_VERSIONS = {
    "PAL_MasterQuest_Debug",
    "PAL_MasterQuest",
    "PAL_GC",
    "PAL_1_0",
    "PAL_1_1",
    "PAL_OTR",
}

@dataclass(frozen=True)
class RomOffsets:
    table: int
    credits_table: int
    messages: int
    credits_messages: int
    table_max: int
    credits_table_max: int
    messages_max: int
    credits_messages_max: int

@dataclass(frozen=True)
class Patch:
    """En ändring av bytes på en fast ROM-adress."""
    offset: int
    data: bytes
    description: str = ""

def byte_patch(offset: int, value: int, description: str = "") -> Patch:
    """Skapar en vanlig patch för ett enda byte."""
    return Patch(offset, bytes([value]), description)

@dataclass(frozen=True)
class RomVersion:
    """Metadata och patchar för en identifierad ROM-version."""
    region: str
    build_date: bytes
    build_offset: int
    offsets: RomOffsets
    inject_credits: bool
    patch_fffc_pointer: bool = False
    preserve_fffc_offset: Optional[int] = None
    patches: Tuple[Patch, ...] = ()

ROM_VERSIONS = {
    'NTSC_1_0': RomVersion(
        region='NTSC',
        build_date=b'26-05-18 10:00:04',
        build_offset=0x0000740C,
        offsets=RomOffsets(
            table=0x00B84A4C,
            credits_table=0x00B88C6C,
            messages=0x0092D000,
            credits_messages=0x00966000,
            table_max=16928,
            credits_table_max=392,
            messages_max=229680,
            credits_messages_max=3952,
        ),
        inject_credits=True,
        patches=(
            byte_patch(0x00E6C34F, 0x79, 'Flytta TRYCK START 7A är default'),
            byte_patch(0x00E6C39F, 0x5C, 'Flytta KONTROLL SAKNAS 5C är default'),
            byte_patch(0x00E79629, 0xEF, 'Ganon gate: bnel t7,at blir bnel t7,t7. t7==t7 är alltid sant, bnel hoppar aldrig, faller igenom till barriär-logiken.'),
            byte_patch(0x00DBECD9, 0x20, 'Fiskedamm: sb v0 blir sb zero. sReelLock skrivs alltid som 0 oavsett CIC-chip.'),
            byte_patch(0x00C8CB08, 0x10, 'Zeldas hår (1/2): opcode beq blir b. Instruktionen blir ovillkorlig branch.'),
            byte_patch(0x00C8CB09, 0x00, 'Zeldas hår (2/2): register t9,at blir zero,zero. Hoppar alltid förbi Matrix_Scale oavsett CIC-chip.'),
        ),
    ),
    'NTSC_1_1': RomVersion(
        region='NTSC',
        build_date=b'26-05-18 10:00:05',
        build_offset=0x0000740C,
        offsets=RomOffsets(
            table=0x00B84C2C,
            credits_table=0x00B88E4C,
            messages=0x0092D000,
            credits_messages=0x00966000,
            table_max=16928,
            credits_table_max=392,
            messages_max=229632,
            credits_messages_max=3952,
        ),
        inject_credits=True,
        patches=(
            byte_patch(0x00E6C6AF, 0x79, 'Flytta TRYCK START 7A är default'),
            byte_patch(0x00E6C6FF, 0x5C, 'Flytta KONTROLL SAKNAS 5C är default'),
            byte_patch(0x00E79989, 0xEF, 'Ganon gate: bnel t7,at blir bnel t7,t7. t7==t7 är alltid sant, bnel hoppar aldrig, faller igenom till barriär-logiken.'),
            byte_patch(0x00DBEFF9, 0x20, 'Fiskedamm: sb v0 blir sb zero. sReelLock skrivs alltid som 0 oavsett CIC-chip.'),
            byte_patch(0x00C8CDF8, 0x10, 'Zeldas hår (1/2): opcode beq blir b. Instruktionen blir ovillkorlig branch.'),
            byte_patch(0x00C8CDF9, 0x00, 'Zeldas hår (2/2): register t9,at blir zero,zero. Hoppar alltid förbi Matrix_Scale oavsett CIC-chip.'),
        ),
    ),
    'NTSC_1_2': RomVersion(
        region='NTSC',
        build_date=b'26-05-18 10:00:06',
        build_offset=0x0000793C,
        offsets=RomOffsets(
            table=0x00B84ABC,
            credits_table=0x00B88CDC,
            messages=0x0092D000,
            credits_messages=0x00966000,
            table_max=16928,
            credits_table_max=392,
            messages_max=229600,
            credits_messages_max=3952,
        ),
        inject_credits=True,
        patches=(
            byte_patch(0x00E6C88F, 0x79, 'Flytta TRYCK START 7A är default'),
            byte_patch(0x00E6C8DF, 0x5C, 'Flytta KONTROLL SAKNAS 5C är default'),
            byte_patch(0x00E79B69, 0xEF, 'Ganon gate: bnel t7,at blir bnel t7,t7. t7==t7 är alltid sant, bnel hoppar aldrig, faller igenom till barriär-logiken.'),
            byte_patch(0x00DBF139, 0x20, 'Fiskedamm: sb v0 blir sb zero. sReelLock skrivs alltid som 0 oavsett CIC-chip.'),
            byte_patch(0x00C8CE58, 0x10, 'Zeldas hår (1/2): opcode beq blir b. Instruktionen blir ovillkorlig branch.'),
            byte_patch(0x00C8CE59, 0x00, 'Zeldas hår (2/2): register t9,at blir zero,zero. Hoppar alltid förbi Matrix_Scale oavsett CIC-chip.'),
        ),
    ),
    'NTSC_MasterQuest': RomVersion(
        region='NTSC',
        build_date=b'26-05-18 10:00:08',
        build_offset=0x00007150,
        offsets=RomOffsets(
            table=0x00B8308C,
            credits_table=0x00B872AC,
            messages=0x0092C000,
            credits_messages=0x00965000,
            table_max=16928,
            credits_table_max=392,
            messages_max=229600,
            credits_messages_max=3952,
        ),
        inject_credits=True,
        patches=(
            byte_patch(0x00DFA0B7, 0x79, 'Flytta TRYCK START 7A är default'),
            byte_patch(0x00DFA107, 0x5C, 'Flytta KONTROLL SAKNAS 5C är default'),
        ),
    ),
    'NTSC_GameCube': RomVersion(
        region='NTSC',
        build_date=b'26-05-18 10:00:07',
        build_offset=0x000071D0,
        offsets=RomOffsets(
            table=0x00B8411C,
            credits_table=0x00B8833C,
            messages=0x0092D000,
            credits_messages=0x00966000,
            table_max=16928,
            credits_table_max=392,
            messages_max=229600,
            credits_messages_max=3952,
        ),
        inject_credits=True,
        patches=(
            byte_patch(0x00DFB1C7, 0x79, 'Flytta TRYCK START 7A är default'),
            byte_patch(0x00DFB217, 0x5C, 'Flytta KONTROLL SAKNAS 5C är default'),
        ),
    ),
    'PAL_MasterQuest': RomVersion(
        region='PAL',
        build_date=b'26-05-18 10:00:12',
        build_offset=0x000071D0,
        offsets=RomOffsets(
            table=0x00B7E8F0,
            credits_table=0x00B86D38,
            messages=0x008BA000,
            credits_messages=0x00967000,
            table_max=16928,
            credits_table_max=392,
            messages_max=229600,
            credits_messages_max=3952,
        ),
        inject_credits=True,
        patch_fffc_pointer=True,
        patches=(
            byte_patch(0x00DF87F7, 0x7B, 'Flytta TRYCK START 7A är default'),
            byte_patch(0x00DF8847, 0x5D, 'Flytta KONTROLL SAKNAS 5C är default'),
        ),
    ),
    'PAL_MasterQuest_Debug': RomVersion(
        region='PAL',
        build_date=b'03-02-21 00:16:31',
        build_offset=0x00012F50,
        offsets=RomOffsets(
            table=0x00BC24C0,
            credits_table=0x00BCA908,
            messages=0x008C6000,
            credits_messages=0x00973000,
            table_max=16928,
            credits_table_max=392,
            messages_max=229664,
            credits_messages_max=3920,
        ),
        inject_credits=True,
        preserve_fffc_offset=0x000380D4,
        patches=(
            byte_patch(0x00BCAD0C, 0x41, 'Å: 7.0 (40 E0 00 00) -> 12.0 (41 40 00 00), första byten'),
            byte_patch(0x00BCAD0D, 0x40, 'Å: andra byten'),
            byte_patch(0x00BCAD14, 0x41, 'å: 7.0 (40 E0 00 00) -> 8.0 (41 00 00 00), första byten'),
            byte_patch(0x00BCAD15, 0x00, 'å: andra byten'),
            byte_patch(0x00E59BAF, 0x7B, 'X-position för TRYCK START'),
            byte_patch(0x00E59C1B, 0x5D, 'X-position för KONTROLL SAKNAS'),
            byte_patch(0x00E5BA5B, 0xCE, 'Pekare för NO CONTROLLER (5ED0 -> 5ECE)'),
            byte_patch(0x00E5BAA7, 0x07, 'Mellanslag efter KONTROLL (första ritloopen)'),
            byte_patch(0x00E5BB5B, 0x07, 'Mellanslag efter KONTROLL (andra ritloopen)'),
            byte_patch(0x00E5BACB, 0x0E, '14 svenska tecken (första ritloopen)'),
            byte_patch(0x00E5BB7F, 0x0E, '14 svenska tecken (andra ritloopen)'),
            byte_patch(0x00B34020, 0x00, 'Stäng av den GameCube-specifika FMV-hoppningen till 0x81000000'),
            byte_patch(0x00B34021, 0x00, 'Stäng av den GameCube-specifika FMV-hoppningen till 0x81000000'),
            byte_patch(0x00B34022, 0x00, 'Stäng av den GameCube-specifika FMV-hoppningen till 0x81000000'),
            byte_patch(0x00B34023, 0x00, 'Stäng av den GameCube-specifika FMV-hoppningen till 0x81000000'),
            # Copyright-bilden: (78, 198)-(238, 214) -> (176, 222)-(336, 238).
            byte_patch(0x00E5B95F, 0x54),
            byte_patch(0x00E5B963, 0x2C),
            byte_patch(0x00E5B96E, 0x03),
            byte_patch(0x00E5B96F, 0x78),
            byte_patch(0x00E5B972, 0x03),
            byte_patch(0x00E5B973, 0xB8),
            Patch(0x00E5BF3E, bytes.fromhex("14 18 17 1D 1B 18 15 15 1C 0A 14 17 0A 1C"), description="KONTROLLSAKNAS"),
            Patch(0x00E5BF4C, bytes.fromhex("1D 1B 22 0C 14 1C 1D 0A 1B 1D 00 00"), description="TRYCKSTART  "),
        ),
    ),
    'PAL_GC': RomVersion(
        region='PAL',
        build_date=b'26-05-18 10:00:11',
        build_offset=0x000071D0,
        offsets=RomOffsets(
            table=0x00B7E910,
            credits_table=0x00B86D58,
            messages=0x008BA000,
            credits_messages=0x00967000,
            table_max=16928,
            credits_table_max=392,
            messages_max=229600,
            credits_messages_max=3952,
        ),
        inject_credits=True,
        patch_fffc_pointer=True,
        patches=(
            byte_patch(0x00DF8897, 0x7B, 'Flytta TRYCK START 7A är default'),
            byte_patch(0x00DF88E7, 0x5D, 'Flytta KONTROLL SAKNAS 5C är default'),
        ),
    ),
    'PAL_1_0': RomVersion(
        region='PAL',
        build_date=b'26-05-18 10:00:09',
        build_offset=0x0000792C,
        offsets=RomOffsets(
            table=0x00B801DC,
            credits_table=0x00B88624,
            messages=0x008BB000,
            credits_messages=0x00968000,
            table_max=16928,
            credits_table_max=392,
            messages_max=229600,
            credits_messages_max=3920,
        ),
        inject_credits=True,
        patch_fffc_pointer=True,
        patches=(
            byte_patch(0x00E6C94F, 0x7B, 'Flytta TRYCK START 7A är default'),
            byte_patch(0x00E6C99F, 0x5D, 'Flytta KONTROLL SAKNAS 5C är default'),
            byte_patch(0x00E79879, 0xEF, 'Ganon gate: bnel t7,at blir bnel t7,t7. t7==t7 är alltid sant, bnel hoppar aldrig, faller igenom till barriär-logiken.'),
            byte_patch(0x00DBF1F9, 0x20, 'Fiskedamm: sb v0 blir sb zero. sReelLock skrivs alltid som 0 oavsett CIC-chip.'),
            byte_patch(0x00C8CF68, 0x10, 'Zeldas hår (1/2): opcode beq blir b. Instruktionen blir ovillkorlig branch.'),
            byte_patch(0x00C8CF69, 0x00, 'Zeldas hår (2/2): register t9,at blir zero,zero. Hoppar alltid förbi Matrix_Scale oavsett CIC-chip.'),
        ),
    ),
    'PAL_1_1': RomVersion(
        region='PAL',
        build_date=b'26-05-18 10:00:10',
        build_offset=0x0000794C,
        offsets=RomOffsets(
            table=0x00B8027C,
            credits_table=0x00B886C4,
            messages=0x008BB000,
            credits_messages=0x00968000,
            table_max=16928,
            credits_table_max=392,
            messages_max=229600,
            credits_messages_max=3920,
        ),
        inject_credits=True,
        patch_fffc_pointer=True,
        patches=(
            byte_patch(0x00E6CB6F, 0x7B, 'Flytta TRYCK START 7A är default'),
            byte_patch(0x00E6CBBF, 0x5D, 'Flytta KONTROLL SAKNAS 5C är default'),
            byte_patch(0x00E79A99, 0xEF, 'Ganon gate: bnel t7,at blir bnel t7,t7. t7==t7 är alltid sant, bnel hoppar aldrig, faller igenom till barriär-logiken.'),
            byte_patch(0x00DBF419, 0x20, 'Fiskedamm: sb v0 blir sb zero. sReelLock skrivs alltid som 0 oavsett CIC-chip.'),
            byte_patch(0x00C8D128, 0x10, 'Zeldas hår (1/2): opcode beq blir b. Instruktionen blir ovillkorlig branch.'),
            byte_patch(0x00C8D129, 0x00, 'Zeldas hår (2/2): register t9,at blir zero,zero. Hoppar alltid förbi Matrix_Scale oavsett CIC-chip.'),
        ),
    ),
    'PAL_OTR': RomVersion(
        region='PAL',
        build_date=b'98-11-10 11:11:11',
        build_offset=0x0000792C,
        offsets=RomOffsets(
            table=0x00B801DC,
            credits_table=0x00B88624,
            messages=0x008BB000,
            credits_messages=0x00968000,
            table_max=16928,
            credits_table_max=392,
            messages_max=229600,
            credits_messages_max=3920,
        ),
        inject_credits=True,
        patch_fffc_pointer=True,
        patches=(
            byte_patch(0x00E6C94F, 0x7B, 'Flytta TRYCK START 7A är default'),
            byte_patch(0x00E6C99F, 0x5D, 'Flytta KONTROLL SAKNAS 5C är default'),
        ),
    ),
    'IQUENTSC': RomVersion(
        region='NTSC',
        build_date=b'26-05-18 10:00:02',
        build_offset=0x0000B75C,
        offsets=RomOffsets(
            table=0x00B8B8E8,
            credits_table=0x00B8FB08,
            messages=0x00931000,
            credits_messages=0x0096A000,
            table_max=16928,
            credits_table_max=392,
            messages_max=229632,
            credits_messages_max=3952,
        ),
        inject_credits=True,
        patches=(
            byte_patch(0x00E62777, 0x7A, 'Flytta TRYCK START 77 är default'),
            byte_patch(0x00E627D7, 0x5C, 'Flytta KONTROLL SAKNAS 5A är default'),
        ),
    ),
    'IQUEPAL': RomVersion(
        region='PAL',
        build_date=b'26-05-18 10:00:03',
        build_offset=0x0000B75C,
        offsets=RomOffsets(
            table=0x00B8B8E8,
            credits_table=0x00B8FB08,
            messages=0x00931000,
            credits_messages=0x0096A000,
            table_max=16928,
            credits_table_max=392,
            messages_max=229632,
            credits_messages_max=3952,
        ),
        inject_credits=True,
        patches=(
            byte_patch(0x00E62777, 0x7A, 'Flytta TRYCK START 77 är default'),
            byte_patch(0x00E627D7, 0x5C, 'Flytta KONTROLL SAKNAS 5A är default'),
        ),
    ),
    'IQUENTSCMQ': RomVersion(
        region='NTSC',
        build_date=b'26-05-18 10:00:00',
        build_offset=0x0000B75C,
        offsets=RomOffsets(
            table=0x00B8B8C8,
            credits_table=0x00B8FAE8,
            messages=0x00931000,
            credits_messages=0x0096A000,
            table_max=16928,
            credits_table_max=392,
            messages_max=229632,
            credits_messages_max=3952,
        ),
        inject_credits=True,
        patches=(
            byte_patch(0x00E626D3, 0x7A, 'Flytta TRYCK START 77 är default'),
            byte_patch(0x00E62733, 0x5C, 'Flytta KONTROLL SAKNAS 5A är default'),
        ),
    ),
    'IQUEPALMQ': RomVersion(
        region='PAL',
        build_date=b'26-05-18 10:00:01',
        build_offset=0x0000B75C,
        offsets=RomOffsets(
            table=0x00B8B8C8,
            credits_table=0x00B8FAE8,
            messages=0x00931000,
            credits_messages=0x0096A000,
            table_max=16928,
            credits_table_max=392,
            messages_max=229632,
            credits_messages_max=3952,
        ),
        inject_credits=True,
        patches=(
            byte_patch(0x00E626D3, 0x7A, 'Flytta TRYCK START 77 är default'),
            byte_patch(0x00E62733, 0x5C, 'Flytta KONTROLL SAKNAS 5A är default'),
        ),
    ),
}

def detect_rom_version(rom_path: Path) -> Optional[Tuple[str, RomVersion]]:
    """Identifierar ROM-versionen med build date-strängen."""
    with rom_path.open("rb") as rom_file:
        for version_name, version in ROM_VERSIONS.items():
            rom_file.seek(version.build_offset)
            if rom_file.read(17) == version.build_date:
                return version_name, version
    return None

def inject_file(rom_path: Path, file_path: Path, offset: int, max_size: int, description: str) -> bool:
    """Skriver en fil till ROM:en och fyller resten av området med nollor."""
    if not file_path.exists():
        print(f"  ✗ Varning: Kunde inte hitta '{file_path}' - hoppar över")
        return True

    data = file_path.read_bytes()
    if len(data) > max_size:
        print(f"  ✗ ERROR: {description}")
        print(f"    Filstorlek: {len(data)} bytes")
        print(f"    Max storlek: {max_size} bytes")
        print(f"    Överskridning: {len(data) - max_size} bytes")
        return False

    with rom_path.open("r+b") as rom_file:
        rom_file.seek(offset)
        rom_file.write(data)
        rom_file.write(b"\x00" * (max_size - len(data)))
    print(f"  ✓ {description}: {len(data)}/{max_size} bytes vid 0x{offset:08X}")
    return True

def inject_data(rom_path: Path, data: bytes, offset: int, max_size: int, description: str) -> bool:
    """Skriver bytes till ROM:en och fyller resten av området med nollor."""
    if len(data) > max_size:
        print(f"  ✗ ERROR: {description}")
        print(f"    Datastorlek: {len(data)} bytes")
        print(f"    Max storlek: {max_size} bytes")
        print(f"    Överskridning: {len(data) - max_size} bytes")
        return False

    with rom_path.open("r+b") as rom_file:
        rom_file.seek(offset)
        rom_file.write(data)
        rom_file.write(b"\x00" * (max_size - len(data)))
    print(f"  ✓ {description}: {len(data)}/{max_size} bytes vid 0x{offset:08X}")
    return True

def apply_patches(rom_path: Path, patches: Sequence[Patch]) -> bool:
    """Applicerar alla ROM-patchar efter kontroll av deklarerade originalbytes."""
    if not patches:
        return True

    try:
        rom_data = bytearray(rom_path.read_bytes())
        applied = []

        for patch in patches:
            end = patch.offset + len(patch.data)
            rom_data[patch.offset:end] = patch.data
            applied.append(patch)

        if applied:
            rom_path.write_bytes(rom_data)
            for patch in applied:
                label = patch.description or f"Patch vid 0x{patch.offset:08X}"
                print(f"  ✓ {label} vid 0x{patch.offset:08X}")
        return True
    except Exception as error:
        print(f"  ✗ ERROR vid patchning: {error}")
        return False

def build_pal_font_order_table(
    table_data: bytes,
    message_data_size: int,
    max_size: int,
    font_order_offset: Optional[int] = None,
) -> Optional[bytes]:
    """Lägger till 0xfffc-posten i PAL-texttabellen."""
    fffd_index = table_data.find(b"\xff\xfd")
    if fffd_index < 0 or fffd_index % 8 != 0 or fffd_index + 8 > len(table_data):
        print("  ✗ ERROR: Kunde inte hitta en giltig 0xfffd-post i texttabellen")
        return None

    original_fffd = bytearray(table_data[fffd_index:fffd_index + 8])
    bank = original_fffd[4]
    if font_order_offset is None:
        font_order_offset = message_data_size
    font_order_end = font_order_offset + len(DEFAULT_FONT_ORDER_DATA)

    font_entry = bytearray(8)
    font_entry[0:2] = b"\xff\xfc"
    font_entry[4] = bank
    font_entry[5] = (font_order_offset >> 16) & 0xff
    font_entry[6] = (font_order_offset >> 8) & 0xff
    font_entry[7] = font_order_offset & 0xff
    original_fffd[5] = (font_order_end >> 16) & 0xff
    original_fffd[6] = (font_order_end >> 8) & 0xff
    original_fffd[7] = font_order_end & 0xff

    patched = table_data[:fffd_index] + bytes(font_entry) + bytes(original_fffd) + table_data[fffd_index + 8:]
    if len(patched) > max_size:
        print("  ✗ ERROR: Texttabellen får inte plats efter att 0xfffc lagts till")
        print(f"    Tabellstorlek: {len(patched)} bytes")
        print(f"    Max storlek: {max_size} bytes")
        return None
    return patched

def sign_extend_16(value: int) -> int:
    return value - 0x10000 if value >= 0x8000 else value

def read_lui_addiu_address(data: bytearray, lui_offset: int, addiu_offset: int) -> int:
    hi = struct.unpack_from(">H", data, lui_offset + 2)[0]
    lo = struct.unpack_from(">H", data, addiu_offset + 2)[0]
    return (hi << 16) + sign_extend_16(lo)

def write_lui_addiu_address(data: bytearray, lui_offset: int, addiu_offset: int, address: int) -> None:
    lo = address & 0xFFFF
    hi = (address >> 16) & 0xFFFF
    if lo >= 0x8000:
        hi = (hi + 1) & 0xFFFF
    struct.pack_into(">H", data, lui_offset + 2, hi)
    struct.pack_into(">H", data, addiu_offset + 2, lo)

def patch_pal_fffc_pointer(rom_path: Path, data_path: Path, message_offset: int, max_size: int) -> bool:
    """Skriver standardordningen och uppdaterar PAL-ROM:ens pekare."""
    try:
        message_data = data_path.read_bytes()
        font_order_offset = len(message_data)
        font_order_length = len(DEFAULT_FONT_ORDER_DATA)
        if font_order_offset + font_order_length > max_size:
            print("  ✗ ERROR: Standard 0xfffc-fontordning får inte plats i meddelandebanken")
            print(f"    Datastorlek: {font_order_offset} bytes")
            print(f"    Fontordning: {font_order_length} bytes")
            print(f"    Max storlek: {max_size} bytes")
            return False

        rom_data = bytearray(rom_path.read_bytes())
        function_offset = rom_data.find(FONT_LOAD_ORDERED_FONT_PROLOG)
        if function_offset < 0:
            print("  ✗ ERROR: Kunde inte hitta Font_LoadOrderedFont")
            return False

        segment_start = read_lui_addiu_address(rom_data, function_offset + 0x38, function_offset + 0x40)
        fffc_address = segment_start + font_order_offset
        fffd_address = fffc_address + font_order_length
        rom_data[message_offset + font_order_offset:message_offset + font_order_offset + font_order_length] = DEFAULT_FONT_ORDER_DATA
        write_lui_addiu_address(rom_data, function_offset + 0x08, function_offset + 0x0C, fffc_address)
        write_lui_addiu_address(rom_data, function_offset + 0x3C, function_offset + 0x44, fffd_address)
        rom_path.write_bytes(rom_data)
        print(f"  ✓ Patchade PAL 0xfffc-pekare: offset 0x{font_order_offset:05X}, längd {font_order_length} bytes")
        return True
    except Exception as error:
        print(f"  ✗ ERROR vid patchning av PAL 0xfffc-pekare: {error}")
        return False

def process_rom(rom_path: Path) -> bool:
    """Injicerar text, credits och patchar i en ROM."""
    print(f"\n{'=' * 60}")
    print(f"Processar: {rom_path.name}")
    print(f"{'=' * 60}")

    detection = detect_rom_version(rom_path)
    if detection is None:
        print("✗ Okänd ROM-version - kan inte identifiera build date")
        print("  Kontrollera att ROM:en är dekomprimerad och omodifierad")
        return False

    version_name, version = detection
    offsets = version.offsets
    print(f"✓ Identifierad som: {version_name} ({version.region})")
    print("\nInjicerar filer:")

    if version_name in PAL_LANGUAGE_ROM_VERSIONS:
        normal_table_name = "nes_message_data_static_PAL.tbl"
        normal_bin_name = "nes_message_data_static_PAL.bin"
    else:
        normal_table_name = "nes_message_data_static.tbl"
        normal_bin_name = "nes_message_data_static.bin"
    normal_table_path = INPUT_DIR / normal_table_name
    normal_bin_path = INPUT_DIR / normal_bin_name

    success = True
    needs_pal_font_order = version.patch_fffc_pointer or version.preserve_fffc_offset is not None
    if needs_pal_font_order:
        normal_table_data = build_pal_font_order_table(
            normal_table_path.read_bytes(),
            normal_bin_path.stat().st_size,
            offsets.table_max,
            version.preserve_fffc_offset,
        )
        success &= normal_table_data is not None and inject_data(
            rom_path, normal_table_data, offsets.table, offsets.table_max, "Normal text table"
        )
    else:
        success &= inject_file(
            rom_path, normal_table_path, offsets.table, offsets.table_max, "Normal text table"
        )

    success &= inject_file(
        rom_path, normal_bin_path, offsets.messages, offsets.messages_max, "Normal text data"
    )

    if version.patch_fffc_pointer:
        success &= patch_pal_fffc_pointer(
            rom_path, normal_bin_path, offsets.messages, offsets.messages_max
        )
    elif version.preserve_fffc_offset is not None:
        success &= inject_data(
            rom_path,
            DEFAULT_FONT_ORDER_DATA,
            offsets.messages + version.preserve_fffc_offset,
            offsets.messages_max - version.preserve_fffc_offset,
            "PAL 0xfffc-fontordning (bevarad debug-offset)",
        )

    if version.inject_credits:
        if version.region == "PAL":
            credits_table_name = "staff_message_data_static_PAL.tbl"
            credits_bin_name = "staff_message_data_static_PAL.bin"
        else:
            credits_table_name = "staff_message_data_static.tbl"
            credits_bin_name = "staff_message_data_static.bin"
        success &= inject_file(
            rom_path,
            INPUT_DIR / credits_table_name,
            offsets.credits_table,
            offsets.credits_table_max,
            f"Credits table ({version.region})",
        )
        success &= inject_file(
            rom_path,
            INPUT_DIR / credits_bin_name,
            offsets.credits_messages,
            offsets.credits_messages_max,
            f"Credits text data ({version.region})",
        )
    else:
        print(f"  ⊘ Hoppar över credits ({version.region} har egen översättning)")

    if version.patches:
        print("\nApplicerar ROM-patchar:")
        success &= apply_patches(rom_path, version.patches)

    if success:
        print(f"\n✓ {rom_path.name} klar!")
    else:
        print(f"\n✗ {rom_path.name} misslyckades!")
    return success

def main() -> None:
    print("=" * 60)
    print("Svenska Zelda OoT - Automatisk ROM-injektion")
    print("=" * 60)

    if not INPUT_DIR.exists():
        print(f"\n✗ ERROR: Mappen '{INPUT_DIR}' finns inte!")
        print("  Kör först extract_text_files.py för att skapa filerna.")
        return
    if not ROMS_DIR.exists():
        print(f"\n✗ ERROR: Mappen '{ROMS_DIR}' finns inte!")
        print("  Skapa mappen och lägg dina ROM-filer där.")
        return

    rom_files = sorted(ROMS_DIR.glob("*.z64"))
    if not rom_files:
        print(f"\n✗ ERROR: Inga ROM-filer hittades i '{ROMS_DIR}'!")
        print("  Stödda format: .z64")
        return

    print(f"\nHittade {len(rom_files)} ROM-fil(er):")
    for rom_path in rom_files:
        print(f"  - {rom_path.name}")

    successful = sum(process_rom(rom_path) for rom_path in rom_files)
    failed = len(rom_files) - successful
    print(f"\n{'=' * 60}")
    print("SAMMANFATTNING")
    print(f"{'=' * 60}")
    print(f"Totalt: {len(rom_files)} ROM-filer")
    print(f"✓ Lyckade: {successful}")
    if failed:
        print(f"✗ Misslyckade: {failed}")
    print("=" * 60)

if __name__ == "__main__":
    main()
