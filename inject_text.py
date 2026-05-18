import os
import struct
from typing import Optional, Tuple, List

# Inmapp med filer att injicera
INPUT_DIR = "extract"

# Mapp med ROM-filer
ROMS_DIR = "roms"

FONT_LOAD_ORDERED_FONT_PROLOG = bytes([0x27, 0xBD, 0xFF, 0xC0, 0xAF, 0xB3, 0x00, 0x24])

PAL_LANGUAGE_ROM_VERSIONS = {
    "PAL_MasterQuest",
    "PAL_GC",
    "PAL_1_0",
    "PAL_1_1",
    "PAL_OTR",
}

# ROM-versioner och deras build dates
ROM_VERSIONS = {
    "NTSC_1_0": {
        "region": "NTSC",
        "build_date": b"26-05-18 10:00:04",
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
            (0x00E79629, 0xEF), # Ganon gate: bnel t7,at blir bnel t7,t7. t7==t7 är alltid sant, bnel hoppar aldrig, faller igenom till barriär-logiken.
            (0x00DBECD9, 0x20), # Fiskedamm: sb v0 blir sb zero. sReelLock skrivs alltid som 0 oavsett CIC-chip.
            (0x00C8CB08, 0x10), # Zeldas hår (1/2): opcode beq blir b. Instruktionen blir ovillkorlig branch.
            (0x00C8CB09, 0x00), # Zeldas hår (2/2): register t9,at blir zero,zero. Hoppar alltid förbi Matrix_Scale oavsett CIC-chip.
        ]
    },
    "NTSC_1_1": {
        "region": "NTSC",
        "build_date": b"26-05-18 10:00:05",
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
            (0x00E79989, 0xEF), # Ganon gate: bnel t7,at blir bnel t7,t7. t7==t7 är alltid sant, bnel hoppar aldrig, faller igenom till barriär-logiken.
            (0x00DBEFF9, 0x20), # Fiskedamm: sb v0 blir sb zero. sReelLock skrivs alltid som 0 oavsett CIC-chip.
            (0x00C8CDF8, 0x10), # Zeldas hår (1/2): opcode beq blir b. Instruktionen blir ovillkorlig branch.
            (0x00C8CDF9, 0x00), # Zeldas hår (2/2): register t9,at blir zero,zero. Hoppar alltid förbi Matrix_Scale oavsett CIC-chip.
        ]
    },
    "NTSC_1_2": {
        "region": "NTSC",
        "build_date": b"26-05-18 10:00:06",
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
            (0x00E79B69, 0xEF), # Ganon gate: bnel t7,at blir bnel t7,t7. t7==t7 är alltid sant, bnel hoppar aldrig, faller igenom till barriär-logiken.
            (0x00DBF139, 0x20), # Fiskedamm: sb v0 blir sb zero. sReelLock skrivs alltid som 0 oavsett CIC-chip.
            (0x00C8CE58, 0x10), # Zeldas hår (1/2): opcode beq blir b. Instruktionen blir ovillkorlig branch.
            (0x00C8CE59, 0x00), # Zeldas hår (2/2): register t9,at blir zero,zero. Hoppar alltid förbi Matrix_Scale oavsett CIC-chip.
        ]
    },
    "NTSC_MasterQuest": {
        "region": "NTSC",
        "build_date": b"26-05-18 10:00:08",
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
        "build_date": b"26-05-18 10:00:07",
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
        "build_date": b"26-05-18 10:00:12",
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
        "patch_fffc_pointer": True,
        "byte_patches": [
            (0x00DF87F7, 0x7B), # Flytta TRYCK START 7A är default
            (0x00DF8847, 0x5D), # Flytta KONTROLL SAKNAS 5C är default
        ]
    },
    "PAL_GC": {
        "region": "PAL",
        "build_date": b"26-05-18 10:00:11",
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
        "patch_fffc_pointer": True,
        "byte_patches": [
            (0x00DF8897, 0x7B), # Flytta TRYCK START 7A är default
            (0x00DF88E7, 0x5D), # Flytta KONTROLL SAKNAS 5C är default
        ]
    },
    "PAL_1_0": {
        "region": "PAL",
        "build_date": b"26-05-18 10:00:09",
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
        "patch_fffc_pointer": True,
        "byte_patches": [
            (0x00E6C94F, 0x7B), # Flytta TRYCK START 7A är default
            (0x00E6C99F, 0x5D), # Flytta KONTROLL SAKNAS 5C är default
            (0x00E79879, 0xEF), # Ganon gate: bnel t7,at blir bnel t7,t7. t7==t7 är alltid sant, bnel hoppar aldrig, faller igenom till barriär-logiken.
            (0x00DBF1F9, 0x20), # Fiskedamm: sb v0 blir sb zero. sReelLock skrivs alltid som 0 oavsett CIC-chip.
            (0x00C8CF68, 0x10), # Zeldas hår (1/2): opcode beq blir b. Instruktionen blir ovillkorlig branch.
            (0x00C8CF69, 0x00), # Zeldas hår (2/2): register t9,at blir zero,zero. Hoppar alltid förbi Matrix_Scale oavsett CIC-chip.
        ]
    },
    "PAL_1_1": {
        "region": "PAL",
        "build_date": b"26-05-18 10:00:10",
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
        "patch_fffc_pointer": True,
        "byte_patches": [
            (0x00E6CB6F, 0x7B), # Flytta TRYCK START 7A är default
            (0x00E6CBBF, 0x5D), # Flytta KONTROLL SAKNAS 5C är default
            (0x00E79A99, 0xEF), # Ganon gate: bnel t7,at blir bnel t7,t7. t7==t7 är alltid sant, bnel hoppar aldrig, faller igenom till barriär-logiken.
            (0x00DBF419, 0x20), # Fiskedamm: sb v0 blir sb zero. sReelLock skrivs alltid som 0 oavsett CIC-chip.
            (0x00C8D128, 0x10), # Zeldas hår (1/2): opcode beq blir b. Instruktionen blir ovillkorlig branch.
            (0x00C8D129, 0x00), # Zeldas hår (2/2): register t9,at blir zero,zero. Hoppar alltid förbi Matrix_Scale oavsett CIC-chip.
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
        "patch_fffc_pointer": True,
        "byte_patches": [
            (0x00E6C94F, 0x7B), # Flytta TRYCK START 7A är default
            (0x00E6C99F, 0x5D), # Flytta KONTROLL SAKNAS 5C är default
        ]
    },
    "IQUENTSC": {
        "region": "NTSC",
        "build_date": b"26-05-18 10:00:02",
        "build_offset": 0xB75C,
        "offsets": {
            "table": 0x00B8B8E8,
            "credits_table": 0x00B8FB08,
            "messages": 0x00931000,
            "credits_messages": 0x0096A000,
            "table_max": 16928,
            "credits_table_max": 392,
            "messages_max": 229632,
            "credits_messages_max": 3952,
        },
        "inject_credits": True,
        "byte_patches": [
            (0x00E62777, 0x7A), # Flytta TRYCK START 77 är default
            (0x00E627D7, 0x5C), # Flytta KONTROLL SAKNAS 5A är default
        ]
    },
    "IQUEPAL": {
        "region": "PAL",
        "build_date": b"26-05-18 10:00:03",
        "build_offset": 0xB75C,
        "offsets": {
            "table": 0x00B8B8E8,
            "credits_table": 0x00B8FB08,
            "messages": 0x00931000,
            "credits_messages": 0x0096A000,
            "table_max": 16928,
            "credits_table_max": 392,
            "messages_max": 229632,
            "credits_messages_max": 3952,
        },
        "inject_credits": True,
        "byte_patches": [
            (0x00E62777, 0x7A), # Flytta TRYCK START 77 är default
            (0x00E627D7, 0x5C), # Flytta KONTROLL SAKNAS 5A är default
        ]
    },
    "IQUENTSCMQ": {
        "region": "NTSC",
        "build_date": b"26-05-18 10:00:00",
        "build_offset": 0xB75C,
        "offsets": {
            "table": 0x00B8B8C8,
            "credits_table": 0x00B8FAE8,
            "messages": 0x00931000,
            "credits_messages": 0x0096A000,
            "table_max": 16928,
            "credits_table_max": 392,
            "messages_max": 229632,
            "credits_messages_max": 3952,
        },
        "inject_credits": True,
        "byte_patches": [
            (0x00E626D3, 0x7A), # Flytta TRYCK START 77 är default
            (0x00E62733, 0x5C), # Flytta KONTROLL SAKNAS 5A är default
        ]
    },
    "IQUEPALMQ": {
        "region": "PAL",
        "build_date": b"26-05-18 10:00:01",
        "build_offset": 0xB75C,
        "offsets": {
            "table": 0x00B8B8C8,
            "credits_table": 0x00B8FAE8,
            "messages": 0x00931000,
            "credits_messages": 0x0096A000,
            "table_max": 16928,
            "credits_table_max": 392,
            "messages_max": 229632,
            "credits_messages_max": 3952,
        },
        "inject_credits": True,
        "byte_patches": [
            (0x00E626D3, 0x7A), # Flytta TRYCK START 77 är default
            (0x00E62733, 0x5C), # Flytta KONTROLL SAKNAS 5A är default
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
                print(f"  ✓ Byte-patch vid 0x{offset:08X} = 0x{value:02X}")
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
    
    print(f"  ✓ {description}: {file_size}/{max_size} bytes vid 0x{offset:08X}")
    return True

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

def control_code_arg_size(value: int) -> int:
    if value in (0x05, 0x06, 0x0C, 0x0E, 0x13, 0x14, 0x1E):
        return 1
    if value in (0x07, 0x11, 0x12):
        return 2
    if value == 0x15:
        return 3
    return 0

def get_padded_message_length(message_data: bytes, offset: int) -> int:
    i = offset
    while i < len(message_data):
        value = message_data[i]
        i += 1
        if value == 0x02:
            break
        i += control_code_arg_size(value)

    return (i - offset + 3) & ~3

def find_message_offset(table_data: bytes, message_id: int) -> Optional[int]:
    for offset in range(0, len(table_data) - 7, 8):
        current_id = struct.unpack_from(">H", table_data, offset)[0]
        message_offset = (table_data[offset + 5] << 16) | (table_data[offset + 6] << 8) | table_data[offset + 7]
        if current_id == message_id:
            return message_offset
        if current_id in (0xFFFD, 0xFFFF):
            break
    return None

def patch_pal_fffc_pointer(rom_path: str, table_path: str, data_path: str) -> bool:
    """Patchar PAL Font_LoadOrderedFont så den pekar på injicerad 0xfffc-data."""
    try:
        with open(table_path, "rb") as table_file:
            table_data = table_file.read()
        with open(data_path, "rb") as data_file:
            message_data = data_file.read()

        fffc_offset = find_message_offset(table_data, 0xFFFC)
        if fffc_offset is None:
            print("  ✗ ERROR: Kunde inte hitta 0xfffc i den injicerade meddelandetabellen")
            return False

        fffc_length = get_padded_message_length(message_data, fffc_offset)

        with open(rom_path, "r+b") as rom_file:
            rom = bytearray(rom_file.read())
            function_offset = rom.find(FONT_LOAD_ORDERED_FONT_PROLOG)
            if function_offset < 0:
                print("  ✗ ERROR: Kunde inte hitta Font_LoadOrderedFont")
                return False

            segment_start = read_lui_addiu_address(rom, function_offset + 0x38, function_offset + 0x40)
            fffc_address = segment_start + fffc_offset
            fffd_address = fffc_address + fffc_length

            write_lui_addiu_address(rom, function_offset + 0x08, function_offset + 0x0C, fffc_address)
            write_lui_addiu_address(rom, function_offset + 0x3C, function_offset + 0x44, fffd_address)

            rom_file.seek(0)
            rom_file.write(rom)

        print(f"  ✓ Patchade PAL 0xfffc-pekare: offset 0x{fffc_offset:05X}, längd {fffc_length} bytes")
        return True
    except Exception as e:
        print(f"  ✗ ERROR vid patchning av PAL 0xfffc-pekare: {e}")
        return False

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

    if version_name in PAL_LANGUAGE_ROM_VERSIONS:
        normal_table_file = "nes_message_data_static_PAL.tbl"
        normal_bin_file = "nes_message_data_static_PAL.bin"
    else:
        normal_table_file = "nes_message_data_static.tbl"
        normal_bin_file = "nes_message_data_static.bin"
    
    success &= inject_file(
        rom_path,
        os.path.join(INPUT_DIR, normal_table_file),
        offsets["table"],
        offsets["table_max"],
        "Normal text table"
    )
    
    success &= inject_file(
        rom_path,
        os.path.join(INPUT_DIR, normal_bin_file),
        offsets["messages"],
        offsets["messages_max"],
        "Normal text data"
    )
    
    # Injicera credits (om inject_credits är sant)
    if version_data.get("patch_fffc_pointer", False):
        success &= patch_pal_fffc_pointer(
            rom_path,
            os.path.join(INPUT_DIR, normal_table_file),
            os.path.join(INPUT_DIR, normal_bin_file),
        )

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
