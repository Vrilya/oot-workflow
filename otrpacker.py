import os
import sys
import struct
import zlib
from typing import Dict, List, Optional, Tuple

# MPQ-Krypto

def _init_crypt_table() -> List[int]:
    # StormLib gör exakt samma sak, magikonstanterna är från originalkällan
    seed = 0x00100001
    table = [0] * 0x500
    for i in range(0x100):
        pos = i
        for _ in range(5):
            seed = (seed * 125 + 3) % 0x2AAAAB
            hi   = (seed & 0xFFFF) << 16
            seed = (seed * 125 + 3) % 0x2AAAAB
            lo   = seed & 0xFFFF
            table[pos] = hi | lo
            pos += 0x100
    return table

_CRYPT_TABLE = _init_crypt_table()


def _hash_string(name: str, kind: int) -> int:
    # kind: 0=slot, 1=nameA, 2=nameB, 3=filnyckel
    a = 0x7FED7FED
    b = 0xEEEEEEEE
    for ch in name.upper():
        v = ord(ch)
        entry = _CRYPT_TABLE[kind * 0x100 + v]
        a = (entry ^ (a + b)) & 0xFFFFFFFF
        b = (v + a + b + (b << 5) + 3) & 0xFFFFFFFF
    return a


def _crypt_inplace(buf: bytearray, key: int):
    b = 0xEEEEEEEE
    i = 0
    while i < len(buf) - 3:
        b = (b + _CRYPT_TABLE[0x400 + (key & 0xFF)]) & 0xFFFFFFFF
        plain = struct.unpack_from('<I', buf, i)[0]
        enc   = plain ^ ((key + b) & 0xFFFFFFFF)
        # nyckeluppdatering – se Ladik MPQ-spec
        t   = ((~key & 0xFFFFFFFF) << 21) & 0xFFFFFFFF
        key = ((t + 0x11111111) & 0xFFFFFFFF) | (key >> 11)
        b   = (plain + b + (b << 5) + 3) & 0xFFFFFFFF
        struct.pack_into('<I', buf, i, enc)
        i += 4


# Komprimering / sektorshantering

_SECTOR_SIZE = 512 << 3  # 4096 byte, standard i OTR-arkiv

_ZLIB_MARKER = 0x02
_ZLIB_LEVEL  = 6

# Flaggkombinationer för block-tabellen
_FLAG_PLAIN   = 0x80000200  # EXISTS | CompressedMulti
_FLAG_CRYPTED = 0x80030200  # EXISTS | CompressedMulti | Encrypted | AdjustedKey


def _split_sectors(data: bytes) -> List[bytes]:
    if not data:
        return []
    sects = []
    n = (len(data) + _SECTOR_SIZE - 1) // _SECTOR_SIZE
    for i in range(n):
        chunk      = data[i * _SECTOR_SIZE : (i + 1) * _SECTOR_SIZE]
        compressed = bytes([_ZLIB_MARKER]) + zlib.compress(chunk, _ZLIB_LEVEL)
        # använd bara komprimerad version om den faktiskt är kortare
        sects.append(compressed if len(compressed) < len(chunk) else chunk)
    return sects


def _make_sector_stream(sectors: List[bytes]) -> bytes:
    # offset-tabell direkt följt av sektordata, precis som MPQ förväntar sig
    n      = len(sectors)
    tbl_sz = (n + 1) * 4
    offs   = [tbl_sz]
    for s in sectors:
        offs.append(offs[-1] + len(s))
    return struct.pack(f'<{n + 1}I', *offs) + b''.join(sectors)


def _pack_plain(data: bytes) -> bytes:
    if not data:
        # tom fil: offset-tabell med bara start==end
        return struct.pack('<2I', 8, 8)
    sectors = _split_sectors(data)
    return _make_sector_stream(sectors)


def _pack_encrypted(data: bytes, base_key: int, file_offset: int) -> bytes:
    # offset-justerad nyckel enligt MPQ-spec: (key + offset - 1) XOR filesize
    fs      = len(data)
    sectors = _split_sectors(data)
    raw     = bytearray(_make_sector_stream(sectors))
    adj_key = ((base_key + file_offset - 1) ^ fs) & 0xFFFFFFFF

    tbl_sz = (len(sectors) + 1) * 4

    tbl = bytearray(raw[:tbl_sz])
    _crypt_inplace(tbl, adj_key)
    raw[:tbl_sz] = tbl

    pos = tbl_sz
    for i, s in enumerate(sectors):
        blk = bytearray(raw[pos : pos + len(s)])
        _crypt_inplace(blk, (adj_key + 1 + i) & 0xFFFFFFFF)
        raw[pos : pos + len(s)] = blk
        pos += len(s)

    return bytes(raw)


# Arkivbyggaren

_LISTFILE_NAME   = "(listfile)"
_ATTRIBUTES_NAME = "(attributes)"
_EMPTY_SLOT      = 0xFFFFFFFF


class ArchiveWriter:
    # Bygger MPQ-arkiv i OTR-format. Håll en global instans och återanvänd.

    def __init__(self):
        self._entries: Dict[str, bytes] = {}

    def add(self, path: str, data: bytes):
        # normalisera separatorer direkt så vi inte får dubbletter
        key = path.replace('\\', '/')
        if key in self._entries:
            print(f"  Varning: skriver över befintlig post '{key}'")
        self._entries[key] = data

    def reset(self):
        self._entries.clear()

    def write(self, out_path: str):
        items = list(self._entries.items())
        if not items:
            raise RuntimeError("Inga resurser att skriva – glömde du add()?")

        file_crcs = [zlib.crc32(d) & 0xFFFFFFFF for _, d in items]

        listfile_data = ('\r\n'.join(p for p, _ in items) + '\r\n').encode('latin-1')
        listfile_crc  = zlib.crc32(listfile_data) & 0xFFFFFFFF

        # attributes: version 100, flagga 1 = CRC32 aktiverat
        # ordning: användarfiler, listfile, sedan platshållare för attributes sig självt (0)
        all_crcs  = file_crcs + [listfile_crc, 0]
        attr_data = struct.pack('<II', 100, 1)
        attr_data += struct.pack(f'<{len(all_crcs)}I', *all_crcs)

        n_total = len(items) + 2  # user-filer + listfile + attributes

        # hashtabellstorlek: minst 8x antal poster, max 64 k, alltid potens av 2
        raw_ht  = min(n_total * 8, 65536)
        ht_size = 1
        while ht_size < raw_ht:
            ht_size <<= 1
        if ht_size < n_total:
            ht_size = n_total

        ht:    List[Optional[Tuple[int, int, int]]] = [None] * ht_size
        bt:    List[Tuple[int, int, int, int]]      = []
        parts: List[bytes]                           = []
        cur = 32  # data börjar på offset 32 (direkt efter headern)

        def insert(name: str, data: bytes, encrypted: bool) -> None:
            nonlocal cur
            idx = len(bt)

            if encrypted:
                key  = _hash_string(name, 3)
                blob = _pack_encrypted(data, key, cur)
                flag = _FLAG_CRYPTED
            else:
                blob = _pack_plain(data)
                flag = _FLAG_PLAIN

            bt.append((cur, len(blob), len(data), flag))
            parts.append(blob)
            cur += len(blob)

            slot = _hash_string(name, 0) % ht_size
            while ht[slot] is not None:
                slot = (slot + 1) % ht_size
            ht[slot] = (_hash_string(name, 1), _hash_string(name, 2), idx)

        for name, data in items:
            insert(name, data, encrypted=False)
        insert(_LISTFILE_NAME,   listfile_data, encrypted=False)
        insert(_ATTRIBUTES_NAME, attr_data,     encrypted=True)

        # kryptera hash-tabellen
        ht_buf = bytearray()
        for entry in ht:
            if entry is None:
                ht_buf += struct.pack('<IIHHI',
                    _EMPTY_SLOT, _EMPTY_SLOT, 0, 0, _EMPTY_SLOT)
            else:
                hA, hB, blk = entry
                ht_buf += struct.pack('<IIHHI', hA, hB, 0, 0, blk)
        _crypt_inplace(ht_buf, _hash_string("(hash table)", 3))

        # kryptera block-tabellen
        bt_buf = bytearray()
        for off, cs, fs, fl in bt:
            bt_buf += struct.pack('<IIII', off, cs, fs, fl)
        _crypt_inplace(bt_buf, _hash_string("(block table)", 3))

        ht_offset  = cur
        bt_offset  = ht_offset + len(ht_buf)
        total_size = bt_offset + len(bt_buf)

        header = struct.pack('<IIIHHIIII',
            0x1A51504D,  # 'MPQ\x1a'
            32,          # headerstorlek = dataoffset
            total_size,
            0,           # format v1
            3,           # sektorexponent: 512 << 3 = 4096
            ht_offset,
            bt_offset,
            ht_size,
            n_total,
        )

        os.makedirs(os.path.dirname(os.path.abspath(out_path)), exist_ok=True)
        with open(out_path, 'wb') as f:
            f.write(header)
            for p in parts:
                f.write(p)
            f.write(bytes(ht_buf))
            f.write(bytes(bt_buf))

        print(f"Sparad: {out_path}")


_writer = ArchiveWriter()


def add_resource(path: str, data: bytes):
    _writer.add(path, data)


def build_archive(out_path: str):
    _writer.write(out_path)
    _writer.reset()


def clear_resources():
    _writer.reset()


# Resursformat

_RES_HEADER_SZ = 0x40
_RES_MAGIC     = 0xDEADBEEFDEADBEEF  # identitetsvärde som OTR-parsern kollar

# Fyrbokstavsidentifierare för resurstyper
_TYPE_TEXTURE = 0x4F544558  # 'OTEX'
_TYPE_TEXT    = 0x4F545854  # 'OTXT'


def _res_header(res_type: int, version: int, is_mod: bool = False) -> bytes:
    # 64 byte huvud, resten nollor (bytearray är nollinitierat)
    hdr = bytearray(_RES_HEADER_SZ)
    # offset 0x00-0x03 lämnas tomma (används inte i v0)
    struct.pack_into('<I', hdr, 0x04, res_type)   # OTEX / OTXT etc.
    struct.pack_into('<i', hdr, 0x08, version)
    struct.pack_into('<Q', hdr, 0x0C, _RES_MAGIC) # 8 byte magic, OTR-parsern verifierar detta
    # 0x14-0x17 är padding, 0x18 är mod-flaggan
    if is_mod:
        hdr[0x18] = 1
    return bytes(hdr)


def _make_resource(res_type: int, version: int, payload: bytes, is_mod: bool = False) -> bytes:
    hdr = _res_header(res_type, version, is_mod)
    return hdr + payload


# Texturer

_PIXEL_FORMATS = {
    'RGBA32': 1, 'RGBA16': 2,
    'CI4':    3, 'CI8':    4,
    'I4':     5, 'I8':     6,
    'IA4':    7, 'IA8':    8, 'IA16': 9,
}


def _pixel_byte_count(fmt: int, pixels: int) -> int:
    if fmt == 1:           # RGBA32
        return pixels * 4
    elif fmt in (2, 9):    # RGBA16, IA16
        return pixels * 2
    elif fmt in (3, 5, 7): # CI4, I4, IA4 – 4 bitar per pixel
        return pixels // 2
    elif fmt in (4, 6, 8): # CI8, I8, IA8 – 1 byte per pixel
        return pixels
    raise ValueError(f"Okänt pixelformat id: {fmt}")


def pack_texture(fmt: int, w: int, h: int, pixels: bytes) -> bytes:
    if w <= 0 or h <= 0:
        raise ValueError(f"Ogiltiga texturdimensioner: {w}x{h}")
    payload  = struct.pack('<i', fmt)
    payload += struct.pack('<i', w)
    payload += struct.pack('<i', h)
    payload += struct.pack('<i', len(pixels))
    payload += pixels
    return _make_resource(_TYPE_TEXTURE, 0, payload)


# Text / meddelandeformat

_MSG_EXTRA_1 = {0x05, 0x06, 0x0C, 0x0E, 0x13, 0x14, 0x1E}
_MSG_EXTRA_2 = {0x07, 0x11, 0x12}
_MSG_EXTRA_3 = {0x15}
_MSG_END     = 0x02
_MSG_CODES   = set(range(0x02, 0x20))

# Standardteckenuppsättning för PAL-versionen (annorlunda ordning mot NTSC)
_PAL_CHARSET = (
    b"0123456789\x01"
    b"ABCDEFGHIJKLMN\x01"
    b"OPQRSTUVWXYZ\x01"
    b"abcdefghijklmn\x01"
    b"opqrstuvwxyz\x01"
    b" -.\x01"
    b"\x02\x02"
)


def _read_message(msg_data: bytes, start: int) -> bytes:
    out   = bytearray()
    pos   = start
    extra = 0
    done  = False

    while pos < len(msg_data):
        c = msg_data[pos]
        if c == 0 and extra == 0 and not done:
            break
        out.append(c)
        pos += 1

        if extra == 0:
            if c in _MSG_CODES:
                if c == _MSG_END:
                    done = True
                elif c in _MSG_EXTRA_1:
                    extra = 1
                elif c in _MSG_EXTRA_2:
                    extra = 2
                    if c == 0x07:
                        done = True
                elif c in _MSG_EXTRA_3:
                    extra = 3
        else:
            extra -= 1

        if done and extra == 0:
            break

    return bytes(out)


def pack_text(msg_data: bytes, table_data: bytes, add_charset: bool) -> bytes:
    entries: List[Tuple[int, int, int, bytes]] = []
    idx = 0

    while idx < len(table_data):
        if idx + 7 >= len(table_data):
            break
        msg_id = struct.unpack_from('>H', table_data, idx)[0]
        if msg_id == 0xFFFF:
            break
        if msg_id in (0xFFFC, 0xFFFD) and add_charset:
            entries.append((0xFFFC, 0, 0, _PAL_CHARSET))
            break
        raw_offset = struct.unpack_from('>I', table_data, idx + 4)[0]
        offset   = raw_offset & 0x00FFFFFF
        box_byte = table_data[idx + 2]
        box_type = (box_byte & 0xF0) >> 4
        box_pos  = (box_byte & 0x0F)
        content  = _read_message(msg_data, offset)
        entries.append((msg_id, box_type, box_pos, content))
        idx += 8

    raw = bytearray()
    for msg_id, box_type, box_pos, content in entries:
        raw += struct.pack('<H', msg_id)
        raw += bytes([box_type, box_pos])
        raw += struct.pack('<i', len(content))
        raw += content

    payload = struct.pack('<i', len(entries)) + bytes(raw)
    return _make_resource(_TYPE_TEXT, 0, payload)


# Skripttolkaren

def _hex(s: str) -> int:
    return int(s, 16)


def _join_path(*parts: str) -> str:
    return '/'.join(p for p in parts if p)


def run_script(image_data: bytes, lines: List[str]) -> str:
    variables: Dict[str, bytes] = {}
    settings:  Dict[str, str]   = {}
    subdir       = ""
    default_name = "Mod.otr"

    def save(data: bytes, path: str):
        add_resource(path, data)

    def out_path(words: List[str]) -> str:
        # sista ordet på raden är alltid målfilens namn
        return _join_path(subdir, words[-1])

    def extract_texture(fmt_name: str, offset_str: str) -> bytes:
        fmt = _PIXEL_FORMATS.get(fmt_name)
        if fmt is None:
            raise ValueError(f"Okänt pixelformat: {fmt_name}")
        use_header = settings.get('AddH', 'true').lower() not in ('false', '0')
        tex_s = settings.get('TexS')
        if tex_s is None:
            raise RuntimeError("'TexS' saknas – sätt det med: Set TexS BREDDxHÖJD")
        w, h   = map(int, tex_s.split('x'))
        start  = _hex(offset_str)
        length = _pixel_byte_count(fmt, w * h)
        pixels = image_data[start : start + length]
        if use_header:
            return pack_texture(fmt, w, h, pixels)
        return pixels

    for line_num, line in enumerate(lines, 1):
        line = line.strip()
        if not line or line.startswith('#'):
            continue

        words  = line.split()
        action = words[0]

        try:
            if action == 'Get':
                name, start, length = words[1], words[2], words[3]
                variables[name] = image_data[_hex(start) : _hex(start) + _hex(length)]

            elif action == 'Rep':
                name  = words[1]
                old_b = bytes.fromhex(words[2])
                new_b = bytes.fromhex(words[3])
                arr   = bytearray(variables[name])
                n     = len(old_b)
                i     = 0
                while i <= len(arr) - n:
                    if arr[i:i + n] == old_b:
                        arr[i:i + n] = new_b
                    i += 1
                variables[name] = bytes(arr)

            elif action == 'Set':
                settings[words[1]] = ' '.join(words[2:])

            elif action == 'Mrg':
                msg_var   = words[1]
                tbl_var   = words[2]
                add_chars = words[3].lower() == 'true'
                save(pack_text(variables[msg_var], variables[tbl_var], add_chars),
                     out_path(words))

            elif action == 'Dir':
                subdir = '/'.join(words[1:]) if len(words) > 1 else ""

            elif action == 'Exp':
                if words[1] in _PIXEL_FORMATS:
                    save(extract_texture(words[1], words[2]), out_path(words))
                else:
                    raise ValueError(f"Okänt Exp-format: {words[1]}")

            else:
                raise ValueError(f"Okänd instruktion: '{action}'")

        except (KeyError, IndexError, ValueError, RuntimeError) as e:
            raise RuntimeError(f"Fel på rad {line_num} ({repr(line)}): {e}") from e

    return settings.get('OTRFileName', default_name)


# Sökvägar - ändra här om filer ligger någon annanstans

IMAGE_PATH  = os.path.join("roms", "Tidens_okarina-PALOTR.z64")
SCRIPT_PATH = os.path.join("extrsettings", "OTRPacker.txt")
OUTPUT_DIR  = "klara"


def main():
    print("otrpacker - Skapa OTR-modfil")
    print("ROM förutsätts vara dekomprimerad.")
    print("=" * 34)

    print(f"Bildfil:   {IMAGE_PATH}")
    print(f"Skriptfil: {SCRIPT_PATH}")

    print("Läser filer...", flush=True)
    with open(IMAGE_PATH, 'rb') as f:
        image_data = f.read()
    with open(SCRIPT_PATH, 'r', encoding='latin-1', errors='replace') as f:
        script_lines = f.read().splitlines()

    clear_resources()

    print("Tolkar skript...", flush=True)
    try:
        otr_name = run_script(image_data, script_lines)
    except RuntimeError as e:
        print(f"\nFEL: {e}")
        clear_resources()
        sys.exit(1)

    out = os.path.join(OUTPUT_DIR, otr_name)

    print(f"Utdatafil: {out}")
    print("Genererar arkiv...", flush=True)
    try:
        build_archive(out)
    except Exception as e:
        print(f"\nFEL vid skrivning: {e}")
        clear_resources()
        sys.exit(1)

    print("Klart!")


if __name__ == '__main__':
    main()