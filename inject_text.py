import os
from typing import Optional, Tuple, List

# Inmapp med filer att injicera
INPUT_DIR = "extract"

# Mapp med ROM-filer
ROMS_DIR = "roms"

# ROM-versioner och deras build dates
ROM_VERSIONS = {
    "NTSC_1_0": {
        "region": "NTSC",
        "build_date": b"98-10-21 04:56:31",
        "build_offset": 0x740C,
        "offsets": {
            "table": 0x00B84A4C,
            "credits_table": 0x00B88C6C,
            "messages": 0x92D000,
            "credits_messages": 0x0966000,
            "table_max": 16928,
            "credits_table_max": 392,
            "messages_max": 229680,
            "credits_messages_max": 3952,
        },
        "inject_credits": True,
        "byte_patches": [
            (0x00E6C34F, 0x79), # Flytta TRYCK START 7A är default
            (0x00E6C39F, 0x5C), # Flytta KONTROLL SAKNAS 5C är default
        ]
    },
    "NTSC_1_1": {
        "region": "NTSC",
        "build_date": b"98-10-26 10:58:45",
        "build_offset": 0x740C,
        "offsets": {
            "table": 0x00B84C2C,
            "credits_table": 0x00B88E4C,
            "messages": 0x92D000,
            "credits_messages": 0x0966000,
            "table_max": 16928,
            "credits_table_max": 392,
            "messages_max": 229632,
            "credits_messages_max": 3952,
        },
        "inject_credits": True,
        "byte_patches": [
            (0x00E6C6AF, 0x79), # Flytta TRYCK START 7A är default
            (0x00E6C6FF, 0x5C), # Flytta KONTROLL SAKNAS 5C är default
        ]
    },
    "NTSC_1_2": {
        "region": "NTSC",
        "build_date": b"98-11-12 18:17:03",
        "build_offset": 0x793C,
        "offsets": {
            "table": 0x00B84ABC,
            "credits_table": 0x00B88CDC,
            "messages": 0x92D000,
            "credits_messages": 0x0966000,
            "table_max": 16928,
            "credits_table_max": 392,
            "messages_max": 229600,
            "credits_messages_max": 3952,
        },
        "inject_credits": True,
        "byte_patches": [
            (0x00E6C88F, 0x79), # Flytta TRYCK START 7A är default
            (0x00E6C8DF, 0x5C), # Flytta KONTROLL SAKNAS 5C är default
        ]
    },
    "NTSC_MasterQuest": {
        "region": "NTSC",
        "build_date": b"02-12-19 14:05:42",
        "build_offset": 0x7150,
        "offsets": {
            "table": 0x00B8308C,
            "credits_table": 0x00B872AC,
            "messages": 0x92C000,
            "credits_messages": 0x0965000,
            "table_max": 16928,
            "credits_table_max": 392,
            "messages_max": 229600,
            "credits_messages_max": 3952,
        },
        "inject_credits": True,
        "byte_patches": [
            (0x00DFA0B7, 0x79), # Flytta TRYCK START 7A är default
            (0x00DFA107, 0x5C), # Flytta KONTROLL SAKNAS 5C är default
        ]
    },
    "NTSC_GameCube": {
        "region": "NTSC",
        "build_date": b"02-12-19 13:28:09",
        "build_offset": 0x71D0,
        "offsets": {
            "table": 0x00B8411C,
            "credits_table": 0x00B8833C,
            "messages": 0x92D000,
            "credits_messages": 0x0966000,
            "table_max": 16928,
            "credits_table_max": 392,
            "messages_max": 229600,
            "credits_messages_max": 3952,
        },
        "inject_credits": True,
        "byte_patches": [
            (0x00DFB1C7, 0x79), # Flytta TRYCK START 7A är default
            (0x00DFB217, 0x5C), # Flytta KONTROLL SAKNAS 5C är default
        ]
    },
    "PAL_MasterQuest": {
        "region": "PAL",
        "build_date": b"03-02-21 20:37:19",
        "build_offset": 0x71D0,
        "offsets": {
            "table": 0x00B7E8F0,
            "credits_table": 0x00B86D38,
            "messages": 0x8BA000,
            "credits_messages": 0x0967000,
            "table_max": 16928,
            "credits_table_max": 392,
            "messages_max": 229600,
            "credits_messages_max": 3952,
        },
        "inject_credits": True,
        "byte_patches": [
            (0x00DF87F7, 0x7B), # Flytta TRYCK START 7A är default
            (0x00DF8847, 0x5D), # Flytta KONTROLL SAKNAS 5C är default
        ]
    },
    "PAL_GC": {
        "region": "PAL",
        "build_date": b"03-02-21 20:12:23",
        "build_offset": 0x71D0,
        "offsets": {
            "table": 0x00B7E910,
            "credits_table": 0x00B86D58,
            "messages": 0x8BA000,
            "credits_messages": 0x0967000,
            "table_max": 16928,
            "credits_table_max": 392,
            "messages_max": 229600,
            "credits_messages_max": 3952,
        },
        "inject_credits": True,
        "byte_patches": [
            (0x00DF8897, 0x7B), # Flytta TRYCK START 7A är default
            (0x00DF88E7, 0x5D), # Flytta KONTROLL SAKNAS 5C är default
        ]
    },
    "PAL_1_0": {
        "region": "PAL",
        "build_date": b"98-11-10 14:34:22",
        "build_offset": 0x792C,
        "offsets": {
            "table": 0x00B801DC,
            "credits_table": 0x00B88624,
            "messages": 0x8BB000,
            "credits_messages": 0x0968000,
            "table_max": 16928,
            "credits_table_max": 392,
            "messages_max": 229600,
            "credits_messages_max": 3920,
        },
        "inject_credits": True,
        "byte_patches": [
            (0x00E6C94F, 0x7B), # Flytta TRYCK START 7A är default
            (0x00E6C99F, 0x5D), # Flytta KONTROLL SAKNAS 5C är default
        ]
    },
    "PAL_1_1": {
        "region": "PAL",
        "build_date": b"98-11-18 17:36:49",
        "build_offset": 0x794C,
        "offsets": {
            "table": 0x00B8027C,
            "credits_table": 0x00B886C4,
            "messages": 0x8BB000,
            "credits_messages": 0x0968000,
            "table_max": 16928,
            "credits_table_max": 392,
            "messages_max": 229600,
            "credits_messages_max": 3920,
        },
        "inject_credits": True,
        "byte_patches": [
            (0x00E6CB6F, 0x7B), # Flytta TRYCK START 7A är default
            (0x00E6CBBF, 0x5D), # Flytta KONTROLL SAKNAS 5C är default
        ]
    },
    "PAL_OTR": {
        "region": "PAL",
        "build_date": b"98-11-10 11:11:11",
        "build_offset": 0x792C,
        "offsets": {
            "table": 0x00B801DC,
            "credits_table": 0x00B88624,
            "messages": 0x8BB000,
            "credits_messages": 0x0968000,
            "table_max": 16928,
            "credits_table_max": 392,
            "messages_max": 229600,
            "credits_messages_max": 3920,
        },
        "inject_credits": True,
        "byte_patches": [
            (0x00E6C94F, 0x7B), # Flytta TRYCK START 7A är default
            (0x00E6C99F, 0x5D), # Flytta KONTROLL SAKNAS 5C är default
        ]
    },
}

def detect_rom_version(rom_path: str) -> Optional[Tuple[str, dict]]:
    """Detekterar ROM-version genom att läsa build date"""
    with open(rom_path, 'rb') as rom:
        for version_name, version_data in ROM_VERSIONS.items():
            # Gå till build date offset
            rom.seek(version_data["build_offset"])
            
            # Läs 17 bytes (build date-sträng)
            build_date = rom.read(17)
            
            # Jämför med förväntad build date
            if build_date == version_data["build_date"]:
                return version_name, version_data
    
    return None

def apply_byte_patches(rom_path: str, patches: List[Tuple[int, int]]) -> bool:
    """Applicerar byte-patches till ROM:en vid angivna offsets"""
    if not patches:
        return True  # Inga patches att applicera
    
    try:
        with open(rom_path, 'r+b') as rom:
            for offset, value in patches:
                rom.seek(offset)
                rom.write(bytes([value]))
                print(f"  ✓ Byte patch @ 0x{offset:08X} = 0x{value:02X}")
        return True
    except Exception as e:
        print(f"  ✗ ERROR vid byte patching: {e}")
        return False

def inject_file(rom_path: str, file_path: str, offset: int, max_size: int, description: str) -> bool:
    """Injicerar en fil in i ROM:en vid given offset"""
    if not os.path.exists(file_path):
        print(f"  ✗ Varning: Kunde inte hitta '{file_path}' - hoppar över")
        return True  # Inte ett kritiskt fel
    
    with open(file_path, 'rb') as f:
        data = f.read()
    
    file_size = len(data)
    
    if file_size > max_size:
        print(f"  ✗ ERROR: {description}")
        print(f"    Filstorlek: {file_size} bytes")
        print(f"    Max storlek: {max_size} bytes")
        print(f"    Överskridning: {file_size - max_size} bytes")
        return False
    
    with open(rom_path, 'r+b') as rom:
        rom.seek(offset)
        rom.write(data)
        
        # Fyll med nollor
        if file_size < max_size:
            padding = max_size - file_size
            rom.write(b'\x00' * padding)
    
    print(f"  ✓ {description}: {file_size}/{max_size} bytes @ 0x{offset:08X}")
    return True

def process_rom(rom_path: str) -> bool:
    """Processar en enskild ROM-fil"""
    rom_name = os.path.basename(rom_path)
    print(f"\n{'='*60}")
    print(f"Processar: {rom_name}")
    print(f"{'='*60}")
    
    # Detektera ROM-version
    detection_result = detect_rom_version(rom_path)
    
    if detection_result is None:
        print("✗ Okänd ROM-version - kan inte identifiera build date")
        print("  Kontrollera att ROM:en är dekomprimerad och omodifierad")
        return False
    
    version_name, version_data = detection_result
    offsets = version_data["offsets"]
    inject_credits = version_data["inject_credits"]
    byte_patches = version_data.get("byte_patches", [])
    region = version_data.get("region", "NTSC")  # Default till NTSC om inte angivet
    
    print(f"✓ Identifierad som: {version_name} ({region})")
    
    print(f"\nInjicerar filer:")
    
    # Injicera normala textfiler
    success = True
    
    success &= inject_file(
        rom_path,
        os.path.join(INPUT_DIR, "nes_message_data_static.tbl"),
        offsets["table"],
        offsets["table_max"],
        "Normal text table"
    )
    
    success &= inject_file(
        rom_path,
        os.path.join(INPUT_DIR, "nes_message_data_static.bin"),
        offsets["messages"],
        offsets["messages_max"],
        "Normal text data"
    )
    
    # Injicera credits (om inject_credits är True)
    if inject_credits:
        # Välj rätt credits-filer baserat på region
        if region == "PAL":
            credits_table_file = "staff_message_data_static_PAL.tbl"
            credits_bin_file = "staff_message_data_static_PAL.bin"
        else:  # NTSC
            credits_table_file = "staff_message_data_static.tbl"
            credits_bin_file = "staff_message_data_static.bin"
        
        success &= inject_file(
            rom_path,
            os.path.join(INPUT_DIR, credits_table_file),
            offsets["credits_table"],
            offsets["credits_table_max"],
            f"Credits table ({region})"
        )
        
        success &= inject_file(
            rom_path,
            os.path.join(INPUT_DIR, credits_bin_file),
            offsets["credits_messages"],
            offsets["credits_messages_max"],
            f"Credits text data ({region})"
        )
    else:
        print(f"  ⊘ Hoppar över credits ({region} har egen översättning)")
    
    # Applicera byte patches
    if byte_patches:
        print(f"\nApplicerar byte patches:")
        success &= apply_byte_patches(rom_path, byte_patches)
    
    if success:
        print(f"\n✓ {rom_name} klar!")
    else:
        print(f"\n✗ {rom_name} misslyckades!")
    
    return success

def main():
    print("="*60)
    print("Svenska Zelda OoT - Automatisk ROM-injektion")
    print("="*60)
    
    # Kontrollera att extract-mappen finns
    if not os.path.exists(INPUT_DIR):
        print(f"\n✗ ERROR: Mappen '{INPUT_DIR}' finns inte!")
        print("  Kör först extract_text_files.py för att skapa filerna.")
        return
    
    # Kontrollera att roms-mappen finns
    if not os.path.exists(ROMS_DIR):
        print(f"\n✗ ERROR: Mappen '{ROMS_DIR}' finns inte!")
        print(f"  Skapa mappen och lägg dina ROM-filer där.")
        return
    
    # Hitta alla ROM-filer
    rom_files = []
    for filename in os.listdir(ROMS_DIR):
        if filename.lower().endswith('.z64'):
            rom_files.append(os.path.join(ROMS_DIR, filename))
    
    if not rom_files:
        print(f"\n✗ ERROR: Inga ROM-filer hittades i '{ROMS_DIR}'!")
        print("  Stödda format: .z64")
        return
    
    print(f"\nHittade {len(rom_files)} ROM-fil(er):")
    for rom in rom_files:
        print(f"  - {os.path.basename(rom)}")
    
    # Processar alla ROM-filer
    total = len(rom_files)
    successful = 0
    failed = 0
    
    for rom_path in rom_files:
        if process_rom(rom_path):
            successful += 1
        else:
            failed += 1
    
    # Slutsammanfattning
    print(f"\n{'='*60}")
    print("SAMMANFATTNING")
    print(f"{'='*60}")
    print(f"Totalt: {total} ROM-filer")
    print(f"✓ Lyckade: {successful}")
    if failed > 0:
        print(f"✗ Misslyckade: {failed}")
    print("="*60)

if __name__ == "__main__":
    main()