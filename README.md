# OoT Workflow
A collection of Python scripts for injecting translated text and images into Ocarina of Time ROMs as part of my Swedish translation project workflow. Comments and output messages are written in Swedish. These scripts are intended for use with the ROMs produced by the Swedish translation of Ocarina of Time and will not work correctly with official retail ROMs.

Text is edited in the `extract` folder using [Hylian Grimoire](https://github.com/Vrilya/Hylian-Grimoire). Images are edited in the `injection` folder using any image editor - for example GIMP. Once edits are complete, the scripts inject the changes into all ROMs in a single run. When satisfied with the result, the ROMs are batch-compressed using [yaz0encdec](https://github.com/Vrilya/yaz0encdec).

## Workflow overview

    1. Edit text files in extract/ using Hylian-Grimoire
    2. Edit image files in injection/ using GIMP or similar
    3. Run verify_files.py to check that all required images are present
    4. Run inject_text.py to inject text into all ROMs in roms/
    5. Run inject_img.py to inject images into all ROMs in roms/
    6. Compress ROMs in roms/ to klara/ with yaz0encdec
    7. Run vcdiff_encode.py to generate xdelta patches from retail and finished ROMs
    8. If Navi's WAV files changed, run prepare_soh_audio.py once
    9. Run sohpacker.py to package textures, text and prepared audio into an OTR or O2R mod file

## Scripts

### inject_text.py

Injects translated text and credits into all ROMs found in the `roms/` folder. The ROM version is detected automatically from the build date string embedded in the ROM. Supports the ROM versions targeted by the Swedish translation of Ocarina of Time.

For each detected ROM, the script injects:

- The main message table and text data from `extract/nes_message_data_static.tbl` and `.bin`
- Credits table and text data from `extract/staff_message_data_static.tbl` and `.bin` (NTSC), or the PAL equivalents
- Version-specific byte patches to reposition certain on-screen messages

Run:

    python inject_text.py

### inject_img.py

Injects translated images into all ROMs listed in its internal ROM-to-settings mapping. Each ROM has a corresponding TOML settings file in `extrsettings/` that describes which images to inject, their format, dimensions, and ROM address. Images are read from the `injection/` folder.

Supports the following N64 texture formats: `I4`, `I8`, `IA4`, `IA8`, `IA16`, `RGBA16`, `RGBA32`.

Run:

    python inject_img.py

### verify_files.py

Checks that all image files referenced by the TOML settings files in `extrsettings/` are present in the `injection/` folder. Reports found and missing files per settings file, along with a total coverage percentage. Run this before inject_img.py to catch missing assets early.

Run:

    python verify_files.py

### sohpacker.py
Packages translated textures, text and prepared audio into an `.otr` or `.o2r` archive for use with [Ship of Harkinian](https://github.com/HarbourMasters/Shipwright). Reads a decompressed ROM from `roms/Tidens_okarina-PALOTR.z64` and a TOML manifest from `extrsettings/OTRPacker.toml`, then writes the finished archive to `klara/Svenska.o2r` by default.
The TOML manifest describes which textures and text segments to extract from the ROM, their format and dimensions, and where to place them inside the archive. The output file extension controls the archive format: `.otr` writes the legacy OTR/MPQ format, while `.o2r` writes the newer O2R/ZIP format.

`[[file]]` entries include existing resource files byte for byte. Each entry has `source` (relative to the TOML file's directory), `path` (directory inside the archive) and `name` (resource filename). For example:

```toml
[[file]]
path = "audio/samples"
name = "Navi - Hello!_META"
source = "../audio/soh/Navi - Hello!_META"
```

The manifest includes all five prepared Navi resources from `audio/soh/`. Their archive paths must match the original resources exactly: `audio/samples/Navi - …_META`. Files directly under `audio/` do not replace these samples. This path was verified against `oot.o2r` and its `audio/fonts/00_Sound_Effects_1` references in the tested SoH 9.2.3 installation, as well as the working voice pack.

Packing never runs the audio converter and does not read the source WAVs. Missing, empty or duplicate file resources stop the build before writing the archive. Run from the project directory:

    python sohpacker.py

### prepare_soh_audio.py

Run this separate preparation step only when Navi's WAV recordings change:

    python prepare_soh_audio.py

The five WAV files in `audio/` must be uncompressed 16-bit PCM, mono, 16000 Hz. This rate matches Navi's existing soundfont tuning; binary AudioSample v2 does not store a sample rate. The original WAVs are preserved.

| Source WAV | Prepared file in `audio/soh/` | Resource inside the mod |
| --- | --- | --- |
| `hello.wav` | `Navi - Hello!_META` | `audio/samples/Navi - Hello!_META` |
| `hey.wav` | `Navi - Hey!_META` | `audio/samples/Navi - Hey!_META` |
| `listen.wav` | `Navi - Listen!_META` | `audio/samples/Navi - Listen!_META` |
| `look.wav` | `Navi - Look!_META` | `audio/samples/Navi - Look!_META` |
| `watchout.wav` | `Navi - Watch Out!_META` | `audio/samples/Navi - Watch Out!_META` |

The converter uses [ZeldaRET sampleconv](https://github.com/zeldaret/oot/tree/main/tools/audio/sampleconv) for Nintendo/SGI ADPCM encoding and predictor-book generation. It searches for `sampleconv.exe` next to the script, then in the sibling `../navi-replace/` project, then on `PATH`. To specify another location:

    python prepare_soh_audio.py --sampleconv "D:\path\to\sampleconv.exe"

Only this preparation step requires sampleconv. Ordinary packing uses Python's standard library and the prepared `_META` files. Keep those files with the project so they can be reused. Changing a WAV alone does not update the mod; rerun preparation explicitly after editing audio.

Each output is a complete binary `OSMP` version 2 resource: the 64-byte resource header, codec 0 ADPCM data, a non-looping end position equal to the WAV's PCM sample count, and that encoding's own predictor book. All five inputs are converted and checked before any prepared files are replaced. This follows [Shipwright's AudioSample v2 reader](https://github.com/HarbourMasters/Shipwright/blob/develop/soh/soh/resource/importer/AudioSampleFactory.cpp) and [Torch's sample writer](https://github.com/HarbourMasters/Torch/blob/main/src/factories/oot/OoTAudioSampleWriter.cpp).

After building, test all five Navi clips in your Ship of Harkinian installation. Archive and decoding checks do not verify playback in the game.

### vcdiff_encode.py

Generates xdelta patch files from the retail ROMs in `retail_roms/` together with the finished ROMs in `klara/`. Patches are written to `xdelta/` with the same filename as the target ROM but with the `.xdelta` extension. File pairs are hardcoded in the script.

Run:

    python vcdiff_encode.py

## Compression

Once all edits are injected, compress all ROMs in `roms/` and save the results to `klara/` using yaz0encdec:

    yaz0encdec.exe --batchc --in roms --out klara

This automatically detects each ROM version, compresses it, and writes the output using the same filename.

## Folder structure

    extract/
      nes_message_data_static.tbl       Main text table
      nes_message_data_static.bin       Main text data
      staff_message_data_static.tbl     Credits table (NTSC)
      staff_message_data_static.bin     Credits text data (NTSC)
      staff_message_data_static_PAL.tbl Credits table (PAL)
      staff_message_data_static_PAL.bin Credits text data (PAL)
    extrsettings/
      NTSC SWE v1.0.toml                Image injection settings per ROM version
      OTRPacker.toml                    Ship of Harkinian packaging manifest
      ...
    injection/
      ...                               Translated images organized in subfolders
    audio/
      hello.wav, hey.wav, listen.wav, look.wav, watchout.wav
      soh/
        Navi - Hello!_META              Prepared binary audio resources
        ...                             Five resources, reused during packing
    roms/
      ...                               Decompressed ROM files (.z64)
    klara/
      ...                               Compressed output ROMs and OTR/O2R file
    retail_roms/
      ...                               Compressed retail-ROMs (.z64)
    xdelta/
      ...                               Generated xdelta-patchfiles
    inject_text.py
    inject_img.py
    verify_files.py
    sohpacker.py
    prepare_soh_audio.py
    vcdiff_encode.py
