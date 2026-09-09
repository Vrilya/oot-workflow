import os
import struct
import sys
from typing import Optional, Tuple, List

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")

# Inmapp med filer att injicera
INPUT_DIR = "extract"

# Mapp med ROM-filer
ROMS_DIR = "roms"

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
    "PAL_MasterQuest_Debug": {
        "region": "PAL",
        "build_date": b"03-02-21 00:16:31",
        "build_offset": 0x12F50,
        "offsets": {
            "table": 0x00BC24C0,
            "credits_table": 0x00BCA908,
            "messages": 0x008C6000,
            "credits_messages": 0x00973000,
            "table_max": 16928,
            "credits_table_max": 392,
            "messages_max": 229664,
            "credits_messages_max": 3920,
        },
        "inject_credits": True,
        # Debug-ROM har redan rätt fontordningsdata på denna fasta adress.
        # Behåll adressen i stället för att leta efter retail-ROMens
        # instruktionssekvens för Font_LoadOrderedFont.
        "preserve_fffc_offset": 0x380D4,
        "byte_patches": [
            # Debug-ROMens breddtabell börjar vid 0x00BCABA0.
            # Varje tecken har ett 32-bitars flyttal vid tabell + (teckenkod - 0x20) * 4.
            # Ge Å (0x7B) och å (0x7D) samma bredder som i övriga svenska ROM:ar.
            (0x00BCAD0C, 0x41),  # Å: 7.0 (40 E0 00 00) -> 12.0 (41 40 00 00), första byten
            (0x00BCAD0D, 0x40),  # Å: andra byten
            (0x00BCAD14, 0x41),  # å: 7.0 (40 E0 00 00) -> 8.0 (41 00 00 00), första byten
            (0x00BCAD15, 0x00),  # å: andra byten
            # Titeltext: svenska strängar och tillhörande ritloopvärden.
            (0x00E59BAF, 0x7B),  # X-position för TRYCK START
            (0x00E59C1B, 0x5D),  # X-position för KONTROLL SAKNAS
            (0x00E5BA5B, 0xCE),  # Pekare för NO CONTROLLER (5ED0 -> 5ECE)
            (0x00E5BAA7, 0x07),  # Mellanslag efter KONTROLL (första ritloopen)
            (0x00E5BB5B, 0x07),  # Mellanslag efter KONTROLL (andra ritloopen)
            (0x00E5BACB, 0x0E),  # 14 svenska tecken (första ritloopen)
            (0x00E5BB7F, 0x0E),  # 14 svenska tecken (andra ritloopen)
            (0x00B34020, 0x00),  # Stäng av den GameCube-specifika FMV-hoppningen till 0x81000000
            (0x00B34021, 0x00),  # Stäng av den GameCube-specifika FMV-hoppningen till 0x81000000
            (0x00B34022, 0x00),  # Stäng av den GameCube-specifika FMV-hoppningen till 0x81000000
            (0x00B34023, 0x00),  # Stäng av den GameCube-specifika FMV-hoppningen till 0x81000000
        ],
        "sequence_patches": [
            (
                0x00E5B958,
                bytes.fromhex(
                    "8F B9 01 48 3C 0C E4 3B 3C 0D 00 13 27 28 00 08 "
                    "AF A8 01 48 35 AD 83 18 35 8C 83 58 AF 2C 00 00"
                ),
                bytes.fromhex(
                    "8F B9 01 48 3C 0C E4 54 3C 0D 00 2C 27 28 00 08 "
                    "AF A8 01 48 35 AD 03 78 35 8C 03 B8 AF 2C 00 00"
                ),
                "Flytta copyright-bilden till nedre högra hörnet",
            ),
        ],
        "title_data_patches": [
            (0x00E5BF3E, bytes([
                0x14, 0x18, 0x17, 0x1D, 0x1B, 0x18, 0x15, 0x15,
                0x1C, 0x0A, 0x14, 0x17, 0x0A, 0x1C,
            ])),
            (0x00E5BF4C, bytes([
                0x1D, 0x1B, 0x22, 0x0C, 0x14, 0x1C, 0x1D, 0x0A,
                0x1B, 0x1D, 0x00, 0x00,
            ])),
        ],
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

def apply_sequence_patches(
    rom_path: str,
    patches: List[Tuple[int, bytes, bytes, str]],
) -> bool:
    """Byter en hel byteföljd efter kontroll av den förväntade originalföljden."""
    if not patches:
        return True

    try:
        with open(rom_path, "rb") as rom_file:
            rom_data = bytearray(rom_file.read())

        ändringar = []
        for offset, expected, replacement, description in patches:
            if len(expected) != len(replacement):
                print(f"  ✗ ERROR: Byteföljden för {description} har olika längd före och efter patchning")
                return False

            end_offset = offset + len(expected)
            actual = bytes(rom_data[offset:end_offset])

            if actual == replacement:
                print(f"  ✓ {description}: redan patchad vid 0x{offset:08X}")
                continue

            if actual != expected:
                print(f"  ✗ ERROR: Oväntad byteföljd vid 0x{offset:08X} för {description}")
                print(f"    Förväntad: {expected.hex(' ').upper()}")
                print(f"    Hittad:    {actual.hex(' ').upper()}")
                return False

            rom_data[offset:end_offset] = replacement
            ändringar.append((offset, description))

        if ändringar:
            with open(rom_path, "r+b") as rom_file:
                rom_file.seek(0)
                rom_file.write(rom_data)

            for offset, description in ändringar:
                print(f"  ✓ {description} vid 0x{offset:08X}")

        return True
    except Exception as e:
        print(f"  ✗ ERROR vid sekvenspatchning: {e}")
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

def inject_data(rom_path: str, data: bytes, offset: int, max_size: int, description: str) -> bool:
    """Injicerar bytes in i ROM:en vid given offset"""
    data_size = len(data)

    if data_size > max_size:
        print(f"  ✗ ERROR: {description}")
        print(f"    Datastorlek: {data_size} bytes")
        print(f"    Max storlek: {max_size} bytes")
        print(f"    Överskridning: {data_size - max_size} bytes")
        return False

    with open(rom_path, 'r+b') as rom:
        rom.seek(offset)
        rom.write(data)

        if data_size < max_size:
            rom.write(b'\x00' * (max_size - data_size))

    print(f"  ✓ {description}: {data_size}/{max_size} bytes vid 0x{offset:08X}")
    return True

def build_pal_font_order_table(
    table_data: bytes,
    message_data_size: int,
    max_size: int,
    font_order_offset: Optional[int] = None,
) -> Optional[bytes]:
    """Lägger till en 0xfffc-post för PAL-ROM:ar som använder Font_LoadOrderedFont-pekaren."""
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
    font_entry[2] = 0x00
    font_entry[3] = 0x00
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

def patch_pal_fffc_pointer(rom_path: str, data_path: str, message_offset: int, max_size: int) -> bool:
    """Lägger in standard 0xfffc-fontordning och patchar PAL Font_LoadOrderedFont."""
    try:
        with open(data_path, "rb") as data_file:
            message_data = data_file.read()

        font_order_offset = len(message_data)
        font_order_length = len(DEFAULT_FONT_ORDER_DATA)
        if font_order_offset + font_order_length > max_size:
            print("  ✗ ERROR: Standard 0xfffc-fontordning får inte plats i meddelandebanken")
            print(f"    Datastorlek: {font_order_offset} bytes")
            print(f"    Fontordning: {font_order_length} bytes")
            print(f"    Max storlek: {max_size} bytes")
            return False

        with open(rom_path, "r+b") as rom_file:
            rom = bytearray(rom_file.read())
            function_offset = rom.find(FONT_LOAD_ORDERED_FONT_PROLOG)
            if function_offset < 0:
                print("  ✗ ERROR: Kunde inte hitta Font_LoadOrderedFont")
                return False

            segment_start = read_lui_addiu_address(rom, function_offset + 0x38, function_offset + 0x40)
            fffc_address = segment_start + font_order_offset
            fffd_address = fffc_address + font_order_length

            rom[message_offset + font_order_offset:message_offset + font_order_offset + font_order_length] = DEFAULT_FONT_ORDER_DATA

            write_lui_addiu_address(rom, function_offset + 0x08, function_offset + 0x0C, fffc_address)
            write_lui_addiu_address(rom, function_offset + 0x3C, function_offset + 0x44, fffd_address)

            rom_file.seek(0)
            rom_file.write(rom)

        print(f"  ✓ Patchade PAL 0xfffc-pekare: offset 0x{font_order_offset:05X}, längd {font_order_length} bytes")
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
    
    normal_table_path = os.path.join(INPUT_DIR, normal_table_file)
    normal_bin_path = os.path.join(INPUT_DIR, normal_bin_file)
    needs_pal_font_order_table = (
        version_data.get("patch_fffc_pointer", False)
        or "preserve_fffc_offset" in version_data
    )
    if needs_pal_font_order_table:
        with open(normal_table_path, "rb") as table_file:
            normal_table_data = table_file.read()
        normal_bin_size = os.path.getsize(normal_bin_path)
        preserved_fffc_offset = version_data.get("preserve_fffc_offset")
        normal_table_data = build_pal_font_order_table(
            normal_table_data,
            normal_bin_size,
            offsets["table_max"],
            preserved_fffc_offset,
        )
        success &= normal_table_data is not None and inject_data(
            rom_path,
            normal_table_data,
            offsets["table"],
            offsets["table_max"],
            "Normal text table"
        )
    else:
        success &= inject_file(
            rom_path,
            normal_table_path,
            offsets["table"],
            offsets["table_max"],
            "Normal text table"
        )
    
    success &= inject_file(
        rom_path,
        normal_bin_path,
        offsets["messages"],
        offsets["messages_max"],
        "Normal text data"
    )
    
    # Injicera credits (om inject_credits är sant)
    if version_data.get("patch_fffc_pointer", False):
        success &= patch_pal_fffc_pointer(
            rom_path,
            normal_bin_path,
            offsets["messages"],
            offsets["messages_max"],
        )
    elif "preserve_fffc_offset" in version_data:
        # Debug-ROM:ar behåller den ursprungliga fungerande fontordningsadressen.
        # Den vanliga textinjektionen nollställer segmentet, så återställ den här.
        fffc_offset = version_data["preserve_fffc_offset"]
        success &= inject_data(
            rom_path,
            DEFAULT_FONT_ORDER_DATA,
            offsets["messages"] + fffc_offset,
            offsets["messages_max"] - fffc_offset,
            "PAL 0xfffc-fontordning (bevarad debug-offset)",
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

    sequence_patches = version_data.get("sequence_patches", [])
    if sequence_patches:
        print("\nApplicerar sekvenspatchar:")
        success &= apply_sequence_patches(rom_path, sequence_patches)

    title_data_patches = version_data.get("title_data_patches", [])
    if title_data_patches:
        print("\nSkriver svensk debug-titeltext:")
        try:
            with open(rom_path, "r+b") as rom:
                for offset, data in title_data_patches:
                    rom.seek(offset)
                    rom.write(data)
                    print(f"  ✓ Titeldata vid 0x{offset:08X} ({len(data)} bytes)")
        except Exception as e:
            print(f"  ✗ ERROR vid titeldata-patchning: {e}")
            success = False
    
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
