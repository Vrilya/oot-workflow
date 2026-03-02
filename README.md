# 🗡️ Legenden om Zelda - Tidens okarina

## 📖 Om Projektet

Detta projekt tillhandahåller en komplett svensk översättning av **The Legend of Zelda: Ocarina of Time** (Tidens okarina). Arbetet har pågått av och till under cirka tre år och bygger på en noggrann genomgång av det japanska originalmanuset, korsrefererat mot det engelska, tyska och franska skriptet. Målet har varit att skapa en svensk text som låter naturligt samtidigt som den förblir trogen det japanska källmaterialet.

En del av arbetet har bestått i att själv kartlägga PAL-ROM:en och dokumentera var alla bitmapbilder jag behövde fanns. Jag har byggt egna verktyg från grunden i Python, C och C#, bland annat för yaz0-komprimering/dekomprimering, extrahering/konvertering av bitmappar samt en editor för redigering av spelets text.

Jag har även ändrat tillbaka till Nintendo 64-färger för knappar i GameCube-ROM:arna och återinfört Nintendo 64-bootlogon. För GameCube-ROM:arna man hittar på PAL-bonusskivor har jag bytt ut spelets videointerface (NTSC) mot standard-PAL så att spelet visas korrekt på europeiska Nintendo 64.

## 🖼️ Screenshots

<div align="center">

| <img src="https://vrilya.github.io/ocarinaswe/images/ganon.png" width="300" alt="Ganon"> | <img src="https://vrilya.github.io/ocarinaswe/images/kingdodongo.png" width="300" alt="King Dodongo"> |
|:---:|:---:|
| <img src="https://vrilya.github.io/ocarinaswe/images/kingsgrave1.png" width="300" alt="King's Grave"> | <img src="https://vrilya.github.io/ocarinaswe/images/title.png" width="300" alt="Title Screen"> |
| <img src="https://vrilya.github.io/ocarinaswe/images/ui.png" width="300" alt="UI"> | <img src="https://vrilya.github.io/ocarinaswe/images/zeldaletter.png" width="300" alt="Zelda Letter"> |

</div>

## 🎥 Video

Videor från översättningen kan du hitta här:
**[🔗 Vrilyas YouTube-kanal](https://www.youtube.com/@brinkofdeath)**

## 🚀 Patchning av ROM och mod för Ship of Harkinian

### 💻 Webbläsare (Rekommenderat)
Den enklaste metoden är att använda webbverktyget jag har satt upp här:
**[🌐 Patcha din ROM här](https://vrilya.github.io/ocarinaswe/)**

### 📁 Manuell patchning
1. Ladda ner patch-filen från **[Releases](https://github.com/Vrilya/ocarinaswe/releases)**
2. Använd ditt föredragna verktyg för att applicera patchen

💡 **Notera:**  
ROM-filen måste vara någon av dessa:  
- **Database match:** Legend of Zelda, The - Ocarina of Time (Europe) (En,Fr,De)  
- **SHA-1:** `328a1f1beba30ce5e178f031662019eb32c5f3b5`
- **MD5:** `E040DE91A74B61E3201DB0E2323F768A`
- **Database match:** Legend of Zelda, The - Ocarina of Time (Europe) (En,Fr,De) (Rev 1)
- **SHA-1:** `cfbb98d392e4a9d39da8285d10cbef3974c2f012`
- **MD5:** `d714580dd74c2c033f5e1b6dc0aeac77`
- **Database match:** Legend of Zelda, The - Ocarina of Time (Europe) (GameCube)
- **SHA-1:** `0227d7c0074f2d0ac935631990da8ec5914597b4`
- **MD5:** `2c27b4e000e85fd78dbca551f1b1c965`
- **Database match:** Legend of Zelda, The - Ocarina of Time - Master Quest (Europe) (En,Fr,De) (GameCube)
- **SHA-1:** `f46239439f59a2a594ef83cf68ef65043b1bffe2`
- **MD5:** `1618403427e4344a57833043db5ce3c3`
- **Database match:** Legend of Zelda, The - Ocarina of Time (USA)
- **SHA-1:** `ad69c91157f6705e8ab06c79fe08aad47bb57ba7`
- **MD5:** `5bd1fe107bf8106b2ab6650abecd54d6`
- **Database match:** Legend of Zelda, The - Ocarina of Time (USA) (Rev 1)
- **SHA-1:** `d3ecb253776cd847a5aa63d859d8c89a2f37b364`
- **MD5:** `721fdcc6f5f34be55c43a807f2a16af4`
- **Database match:** Legend of Zelda, The - Ocarina of Time (USA) (Rev 2)
- **SHA-1:** `41b3bdc48d98c48529219919015a1af22f5057c2`
- **MD5:** `57a9719ad547c516342e1a15d5c28c3d`
- **Database match:** Legend of Zelda, The - Ocarina of Time (USA) (GameCube)
- **SHA-1:** `b82710ba2bd3b4c6ee8aa1a7e9acf787dfc72e9b`
- **MD5:** `cd09029edcfb7c097ac01986a0f83d3f`
- **Database match:** Legend of Zelda, The - Ocarina of Time - Master Quest (USA) (GameCube)
- **SHA-1:** `8b5d13aac69bfbf989861cfdc50b1d840945fc1d`
- **MD5:** `da35577fe54579f6a266931cc75f512d`

### 🚢 Ship of Harkinian Setup

Det enklaste sättet är att ladda ner den färdiga OTR-filen via GameBanana:  
**[📥 Direktlänk till modens sida här](https://gamebanana.com/mods/613613)**  
Packa upp arkivet och placera `Svenska.otr` i `mods`-mappen i din Ship of Harkinian-installation.  

Om du hellre vill skapa filen själv manuellt:  

1. **Ladda ner** `OTRMod_PAL10.txt` från [Releases](https://github.com/Vrilya/ocarinaswe/releases)  
2. **Dekomprimera din redan patchade ROM** med yaz0encdec (Bara PAL 1.0 än så länge):  
   ```
   https://github.com/Vrilya/yaz0encdec
   ```
3. **Generera OTR-filen** på:  
   ```
   https://soh.xoas.eu.org/
   ```
   - Välj `OTRMod_PAL10.txt` under "Choose a script"  
   - Välj den dekomprimerade ROM-filen under "Choose a ROM"  
   - Klicka på "Generate OTR"
4. **Installera moden**:  
   - Spara den genererade `Svenska.otr`-filen till `mods`-mappen i din Ship of Harkinian-installation  

> ⚠️ **Viktigt**: Andra mods som påverkar text och bilder kan orsaka konflikter och störa funktionaliteten.

## 🔮 Framtida Planer

Om folk gillar den här översättningen och det finns tillräckligt med intresse så kanske jag tar mig an Majora's Mask som nästa projekt. Det är inget jag lovar eller har bestämt mig för än, men tanken finns där beroende på hur det här tas emot.

## 📞 Kontakt

Har du frågor eller synpunkter? Kontakta mig gärna:

- **Discord**: `.vrilya`
- **Steam**: `Vrilya`
- **Email**: `vinterhjarta@gmail.com`
- **YouTube**: Du kan även kommentera på min YouTube-kanal.

## 🛠️ Verktyg & Resurser

- **Bitmap-verktyg (VOoTIE)**: [GitHub Repository](https://github.com/Vrilya/VOoTIE)
- **Yaz0-Kompressor/dekompressor (yaz0encdec)**: [GitHub Repository](https://github.com/Vrilya/yaz0encdec)
- **Texteditorn jag utvecklade för det här projektet (OoT Text Editor)**: [GitHub Repository](https://github.com/Vrilya/oottexteditor)
- **Workflow för batch-hantering av hela projektet (OoT Workflow)**: [GitHub Repository](https://github.com/Vrilya/oot-workflow)

## 📜 Användning & Rättigheter

Jag delar **inte** med mig av ROM-filer och kan därför inte hjälpa till med att skaffa dem.  
Utöver det gäller: *Gör vad du vill ska vara lagen*, som en viss engelsk poet en gång skrev.

Du behöver inte fråga mig om lov för att:  
- Göra egna repros med den här översättningen  
- Skriva om, ändra eller vidareutveckla texten  
- Använda rader du tycker om i din egen översättning  
- Skapa helt nya projekt baserade på mitt arbete  

Kort sagt - använd, förändra och sprid hur du vill.

---

<div align="center">

**Tack för att du visar intresse för projektet!** ⭐

*Om du uppskattar min översättning, lämna gärna en stjärna på repot!*

</div>

# Vrilya's Ocarina of Time Image Extractor/Injector

## Overview
Vrilya's Ocarina of Time Image Extractor/Injector is a tool designed for extracting and injecting image textures from The Legend of Zelda: Ocarina of Time ROM files. This tool allows users to extract textures, modify them, and re-insert them into the game, making it useful for modding and custom texture replacements.

## Features
- **Extract Images**: Extract textures from the game ROM.
- **Inject Images**: Replace existing textures in the ROM with custom images.
- **Automatic Format Detection**: Reads settings from a configuration file to extract images correctly.
- **Batch Processing**: Extract and inject multiple images automatically based on predefined settings.
- **GUI Interface**: A user-friendly graphical interface for selecting ROMs, settings, and output folders.

## Download
You can download the latest version of **VOoTIE** from the [Releases page](https://github.com/Vrilya/VOoTIE/releases).

## How to Use
### Extracting Images
1. **Run the program**: Open `VOoTIE.exe`.
2. **Select a ROM version file**: Choose a `.txt` file that defines image locations and formats.
3. **Choose a ROM file**: Select an Ocarina of Time `.z64` ROM.
4. **Select an output folder**: Specify where extracted images should be saved.
5. **Start extraction**: Click "Extract Images" to start extracting.

### Injecting Images
1. **Modify extracted images**: Edit the `.png` files as needed.
2. **Start injection**: Click "Inject Images" to inject the modified images back into the ROM.

### Testing in an Emulator
- Click "Start Emulator" to launch the emulator with the modified ROM.

## ROM Version File Format
The settings file defines image extraction and injection parameters.

Example:
Set TexS 32x32  # Sets texture size
Exp IA8 0x12345678 my_texture  # Exports texture at given address

## Notes
- Always create a backup of your ROM before making modifications.

# yaz0encdec

yaz0encdec is a command-line tool for compressing and decompressing N64 Ocarina of Time ROMs using the Yaz0 algorithm. It was created as a study of how OoT ROMs are typically compressed and how the DMA file table relates to the Yaz0-encoded segments within the ROM.

The tool is primarily intended for use with the ROMs produced by my Swedish translation of Ocarina of Time and may not work correctly with official retail ROMs.

## Usage

Compress a decompressed ROM:

    yaz0encdec --compress --in <decompressed.z64> --out <compressed.z64>

Decompress a compressed ROM:

    yaz0encdec --decompress --in <compressed.z64> --out <decompressed.z64>

Batch compress all recognized ROMs in a directory:

    yaz0encdec --batch --in <source_dir> --out <target_dir>

This scans the source directory for `.z64` files, identifies each ROM version automatically, compresses them, and saves the results to the target directory using the same filenames. Unrecognized files are skipped. Existing files in the target directory are overwritten without prompting.

The ROM version is detected automatically from the build date string embedded in the ROM header.

## Building

The project is written in C99 with no external dependencies.

### Windows (cross-compile from WSL/Linux)

Requires `mingw-w64`:

    sudo apt install gcc-mingw-w64-x86-64

Build:

    make

This produces `yaz0encdec.exe`.

### Linux

    make native

This produces `yaz0encdec`.

### Cleaning build artifacts

    make clean

## Project structure

    src/
      main.c          Entry point and argument parsing
      yaz0.c/.h       Yaz0 encoder and decoder
      n64crc.c/.h     N64 ROM CRC calculation
      dma.c/.h        DMA table parsing, validation and writing
      romdb.c/.h      ROM version database and detection
      compress.c/.h   Full-ROM compression pipeline
      decompress.c/.h Full-ROM decompression pipeline
      util.c/.h       Shared helpers (byte I/O, alignment, dynamic buffers)
    Makefile

# OoT Text Editor

OoT Text Editor is a Windows desktop application for editing message and dialogue text in Ocarina of Time. It was created as part of my Swedish translation of the game. This repository primarily serves to document my work. More feature complete and polished text editors for OoT are available within the community. The goal of this project was to build every part of the toolchain independently, without relying on existing tools. The editor was originally prototyped in Python and later rewritten in C#.

## Usage

1. Build the project with Visual Studio or `dotnet build`.
2. Launch the application.
3. Go to **File → Load** and select your `.tbl` and `.bin` files.
4. Select a message from the list, edit the text, and adjust metadata as needed.
5. Go to **File → Save** or **File → Save As...** when done.

Requires Windows and the [.NET 8 Desktop Runtime](https://dotnet.microsoft.com/en-us/download/dotnet/8.0).

## Project structure

    OoTEditor/
      Program.cs          Entry point
      MainForm.cs         UI layout and event handling
      MessageCodec.cs     Binary encode/decode and table parsing
      MessageEntry.cs     Data model for a single message

Feel free to use or adapt this project however you like if you want to build something of your own from it.


# OoT Workflow
A collection of Python scripts for injecting translated text and images into Ocarina of Time ROMs as part of my Swedish translation project workflow. Comments and output messages are written in Swedish. These scripts are intended for use with the ROMs produced by the Swedish translation of Ocarina of Time and will not work correctly with official retail ROMs.

Text is edited in the `extract` folder using [OoT Text Editor](https://github.com/Vrilya/oottexteditor). Images are edited in the `injection` folder using any image editor - for example GIMP. Once edits are complete, the scripts inject the changes into all ROMs in a single run. When satisfied with the result, the ROMs are batch-compressed using [yaz0encdec](https://github.com/Vrilya/yaz0encdec).

## Workflow overview

    1. Edit text files in extract/ using OoT Text Editor
    2. Edit image files in injection/ using GIMP or similar
    3. Run verify_files.py to check that all required images are present
    4. Run inject_text.py to inject text into all ROMs in roms/
    5. Run inject_img.py to inject images into all ROMs in roms/
    6. Run otrpacker.py to package textures and text into an OTR mod file

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

### otrpacker.py
Packages translated textures and text into an `.otr` archive for use with [Ship of Harkinian](https://github.com/HarbourMasters/Shipwright). Reads a decompressed ROM from `roms/Tidens_okarina-PALOTR.z64` and a set of extraction instructions from `extrsettings/OTRPacker.txt`, then writes the finished archive to `klara/`.
The script file describes which textures and text segments to extract from the ROM, their format and dimensions, and where to place them inside the archive.
Run:

    python otrpacker.py

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
      ...                               Compressed output ROMs and OTR file
    inject_text.py
    inject_img.py
    verify_files.py
    otrpacker.py