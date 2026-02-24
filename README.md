# OoT Workflow
A collection of Python scripts for injecting translated text and images into Ocarina of Time ROMs as part of my Swedish translation project workflow. Comments and output messages are written in Swedish. These scripts are intended for use with the ROMs produced by the Swedish translation of Ocarina of Time and will not work correctly with official retail ROMs.

Text is edited in the `extract` folder using [OoT Text Editor](https://github.com/Vrilya/oottexteditor). Images are edited in the `injection` folder using any image editor - for example GIMP. Once edits are complete, the scripts inject the changes into all ROMs in a single run. When satisfied with the result, the ROMs are batch-compressed using [yaz0encdec](https://github.com/Vrilya/yaz0encdec).

## Workflow overview

    1. Edit text files in extract/ using OoT Text Editor
    2. Edit image files in injection/ using GIMP or similar
    3. Run verify_files.py to check that all required images are present
    4. Run inject_text.py to inject text into all ROMs in roms/
    5. Run inject_img.py to inject images into all ROMs in roms/
    6. Batch-compress all finished ROMs into klara/ using yaz0encdec

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

Injects translated images into all ROMs listed in its internal ROM-to-settings mapping. Each ROM has a corresponding settings file in `extrsettings/` that describes which images to inject, their format, dimensions, and ROM address. Images are read from the `injection/` folder.

Supports the following N64 texture formats: `I4`, `I8`, `IA4`, `IA8`, `IA16`, `RGBA16`, `RGBA32`.

Run:

    python inject_img.py

### verify_files.py

Checks that all image files referenced by the settings files in `extrsettings/` are present in the `injection/` folder. Reports found and missing files per settings file, along with a total coverage percentage. Run this before inject_img.py to catch missing assets early.

Run:

    python verify_files.py

## Compression

Once all edits are injected, compress all ROMs in `roms/` and save the results to `klara/` using yaz0encdec:

    yaz0encdec.exe --batch --in roms --out klara

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
      NTSC SWE v1.0.txt                 Image injection settings per ROM version
      ...
    injection/
      ...                               Translated images organized in subfolders
    roms/
      ...                               Decompressed ROM files (.z64)
    klara/
      ...                               Compressed output ROMs
    inject_text.py
    inject_img.py
    verify_files.py