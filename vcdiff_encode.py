import sys
from pathlib import Path
from typing import List, Tuple, Optional


# VCDIFF-konstanter (RFC 3284 + xdelta3-tillägg)

VCDIFF_MAGIC        = b"\xd6\xc3\xc4\x00"   # 4-byte magic
HDR_INDICATOR       = 0x00                  # ingen sekundär komprimering, ingen anpassad kodtabell
VCD_SOURCE          = 0x01                  # Win_Indicator: källsegment från "källfilen"
VCD_TARGET          = 0x02                  # Win_Indicator: källsegment från målet (används ej här)
VCD_ADLER32         = 0x04                  # Win_Indicator: xdelta3 Adler-32-kontrollsumma-tillägg

# Delta-indikator-bitar (vi använder aldrig sekundär komprimering)
DELTA_INDICATOR     = 0x00

# Instruktionstyper
NOOP  = 0
ADD   = 1
RUN   = 2
COPY  = 3

# Adresslägen
VCD_SELF = 0
VCD_HERE = 1

# Standard cachestorlekar (RFC 3284-standard, samma som xdelta3)
S_NEAR = 4
S_SAME = 3

# Minsta kopieringslängd värd att koda
MIN_MATCH   = 4
# Hashfönsterstorlekar
LARGE_LOOK  = 16
SMALL_LOOK  = 4

# Fönsterstorlek: bearbeta målet i bitar av denna storlek
WIN_SIZE = 1 << 23


# Variabellängdsheltalskodning (VCDIFF / xdelta3-stil)

def encode_varint(n: int) -> bytes:
    # Koda ett icke-negativt heltal som VCDIFF variabellängdsheltal.
    if n < 0:
        raise ValueError("varint måste vara icke-negativt")
    if n == 0:
        return b"\x00"
    out = []
    while n:
        out.append(n & 0x7f)
        n >>= 7
    out.reverse()
    # Sätt fortsättningsbit på alla bytes utom den sista
    for i in range(len(out) - 1):
        out[i] |= 0x80
    return bytes(out)


def decode_varint(data: bytes, pos: int) -> Tuple[int, int]:
    # Avkoda varint vid data[pos]. Returnerar (värde, ny_pos).
    val = 0
    while True:
        b = data[pos]; pos += 1
        val = (val << 7) | (b & 0x7f)
        if not (b & 0x80):
            break
    return val, pos


# Adresscache

class AddressCache:

    def __init__(self, s_near: int = S_NEAR, s_same: int = S_SAME):
        self.s_near     = s_near
        self.s_same     = s_same
        self.near       = [0] * s_near
        self.next_slot  = 0
        self.same       = [0] * (s_same * 256)

    def reset(self):
        self.near       = [0] * self.s_near
        self.next_slot  = 0
        self.same       = [0] * (self.s_same * 256)

    def update(self, addr: int):
        if self.s_near > 0:
            self.near[self.next_slot] = addr
            self.next_slot = (self.next_slot + 1) % self.s_near
        if self.s_same > 0:
            self.same[addr % (self.s_same * 256)] = addr

    def encode_address(self, addr: int, here: int) -> Tuple[int, int, bool]:
        # Välj det bästa adressläget för `addr` givet att den aktuella
        # utdatapositionen är here.
        best_d    = addr
        best_mode = VCD_SELF

        # VCD_HERE
        d = here - addr
        if d < best_d:
            best_d, best_mode = d, VCD_HERE

        # NEAR[i]
        for i in range(self.s_near):
            if addr >= self.near[i]:
                d = addr - self.near[i]
                if d < best_d:
                    best_d, best_mode = d, i + 2

        # SAME[i] – enkelbyteskodning
        use_byte = False
        if self.s_same > 0:
            idx = addr % (self.s_same * 256)
            if self.same[idx] == addr:
                # SAME-lägets bytevärde = idx % 256, läge = s_near + 2 + idx // 256
                sd    = idx % 256
                smode = self.s_near + 2 + idx // 256
                # SAME kodar alltid i 1 byte – alltid bättre än varint ≥ 2 bytes
                if best_d >= 128 or True:
                    best_d    = sd
                    best_mode = smode
                    use_byte  = True

        self.update(addr)
        return best_d, best_mode, use_byte


# Standard RFC 3284-kodtabell

def _build_code_table() -> List[Tuple[int,int,int,int,int,int]]:
    t = []

    t.append((RUN, 0, 0, NOOP, 0, 0))

    for sz in [0] + list(range(1, 18)):
        t.append((ADD, sz, 0, NOOP, 0, 0))

    for mode in range(9):
        for sz in [0] + list(range(4, 19)):
            t.append((COPY, sz, mode, NOOP, 0, 0))

    for mode in range(9):
        copy_sizes = [4, 5, 6] if mode < 6 else [4]
        for add_sz in range(1, 5):
            for copy_sz in copy_sizes:
                t.append((ADD, add_sz, 0, COPY, copy_sz, mode))

    # Fyll ut till 256 med NOOP:er om det behövs
    while len(t) < 256:
        t.append((NOOP, 0, 0, NOOP, 0, 0))

    assert len(t) == 256, f"kodtabellens längd = {len(t)}"
    return t


CODE_TABLE = _build_code_table()

# Bygg omvänd uppslagstabell: (typ, storlek, läge) → lista med opkodindex
# Vi behåller den första förekomsten (lägsta opkoden) för varje nyckel.
_SINGLE_LOOKUP: dict = {}
_FIRST_LOOKUP:  dict = {}
_SECOND_LOOKUP: dict = {}

for _idx, (t1, s1, m1, t2, s2, m2) in enumerate(CODE_TABLE):
    _key1 = (t1, s1, m1)
    if t1 != NOOP and _key1 not in _SINGLE_LOOKUP:
        _SINGLE_LOOKUP[_key1] = _idx
    if t2 != NOOP:
        _combo = (t1, s1, m1, t2, s2, m2)
        if _combo not in _SECOND_LOOKUP:
            _SECOND_LOOKUP[_combo] = _idx


def find_opcode_single(itype: int, size: int, mode: int) -> Tuple[int, bool]:
    # Returnera (opkod, storlek_i_inst) för en enskild instruktion.
    # Försök med exakt storlek först
    key = (itype, size, mode)
    if key in _SINGLE_LOOKUP:
        return _SINGLE_LOOKUP[key], True
    # Falla tillbaka på storlek=0-varianten
    key0 = (itype, 0, mode)
    if key0 in _SINGLE_LOOKUP:
        return _SINGLE_LOOKUP[key0], False
    raise ValueError(f"Ingen opkod för ({itype}, {size}, {mode})")


def find_opcode_double(t1: int, s1: int, m1: int,
                       t2: int, s2: int, m2: int) -> Optional[int]:
    return _SECOND_LOOKUP.get((t1, s1, m1, t2, s2, m2))

# Strängmatchning

def _build_hash_table(data: bytes, look: int, step: int) -> dict:
    # Bygg {n-gram → position} hashtabell.
    table = {}
    limit = len(data) - look + 1
    for i in range(0, limit, step):
        ng = data[i:i + look]
        table[ng] = i
    return table


def _extend_match(source: bytes, src_off: int,
                  target: bytes, tgt_off: int,
                  max_fwd: int) -> int:
    # Förläng en matchning framåt från (src_off, tgt_off).
    # Returnerar antalet matchande bytes som börjar vid dessa positioner.
    length = 0
    while (length < max_fwd
           and src_off + length < len(source)
           and tgt_off + length < len(target)
           and source[src_off + length] == target[tgt_off + length]):
        length += 1
    return length


class StringMatcher:
    # Tvånivås strängmatchare (stor=källa, liten=mål).
    # Förenklad från xdelta3:s metod men producerar korrekt utdata.

    def __init__(self, source: bytes,
                 src_base: int = 0,
                 large_look: int = LARGE_LOOK,
                 large_step: int = LARGE_LOOK,
                 small_look: int = SMALL_LOOK):
        self.source     = source
        self.src_base   = src_base
        self.large_look = large_look
        self.large_step = large_step
        self.small_look = small_look
        # Bygg källans hashtabell (stora kontrollsummor)
        self.large_table = _build_hash_table(source, large_look, large_step)

    def find_matches(self, target: bytes) -> List[Tuple[int, int, int, bool]]:
        # Skanna `target` och returnera en lista med matchningar.
        src       = self.source
        src_len   = len(src)
        tgt_len   = len(target)
        ll        = self.large_look
        sl        = self.small_look

        matches   = []
        tgt_pos   = 0
        small_tbl = {}

        while tgt_pos <= tgt_len - sl:
            best_len  = 0
            best_addr = 0
            best_src  = False

            # Stor uppslagning
            if tgt_pos + ll <= tgt_len:
                ng = target[tgt_pos:tgt_pos + ll]
                sp = self.large_table.get(ng)
                if sp is not None:
                    mlen = _extend_match(src, sp, target, tgt_pos,
                                         tgt_len - tgt_pos)
                    if mlen >= MIN_MATCH and mlen > best_len:
                        best_len  = mlen
                        best_addr = sp   # absolut källadress
                        best_src  = True

            # Liten uppslagning
            if tgt_pos + sl <= tgt_len:
                ng = target[tgt_pos:tgt_pos + sl]
                tp = small_tbl.get(ng)
                if tp is not None and (tgt_pos - tp) >= sl:
                    # Förläng bara framåt (kan inte gå tillbaka i redan bearbetad region)
                    ref = tp
                    cur = tgt_pos
                    mlen = 0
                    while cur + mlen < tgt_len and target[ref + mlen] == target[cur + mlen]:
                        mlen += 1
                        # Tillåt överlappande kopiering
                        if ref + mlen >= tgt_pos:
                            break   # enkelt: stoppa vid överlappningsgräns
                    if mlen >= MIN_MATCH and mlen > best_len:
                        best_len  = mlen
                        best_addr = src_len + tp   # målutrymmes-adress
                        best_src  = False

            if best_len >= MIN_MATCH:
                matches.append((tgt_pos, best_len, best_addr, best_src))
                # Lägg in alla tabellposter vi hoppade över
                for p in range(tgt_pos, tgt_pos + best_len):
                    if p + sl <= tgt_len:
                        small_tbl[target[p:p + sl]] = p
                tgt_pos += best_len
            else:
                # Ingen matchning – lägg in i liten tabell och gå vidare
                if tgt_pos + sl <= tgt_len:
                    small_tbl[target[tgt_pos:tgt_pos + sl]] = tgt_pos
                tgt_pos += 1

        return matches


# Fönsterkodare

class WindowEncoder:
    # Kodar ett enskilt VCDIFF-fönster.

    def __init__(self, source: bytes, src_base: int = 0):
        self.source   = source
        self.src_base = src_base
        self.cache    = AddressCache()

    def encode_window(self, target: bytes) -> bytes:
        # Koda ett målfönster. Returnerar det fullständigt serialiserade fönstret.
        src     = self.source
        src_len = len(src)

        # Återställ adresscachen för varje fönster
        self.cache.reset()

        # Hitta matchningar
        matcher = StringMatcher(src, self.src_base)
        matches = matcher.find_matches(target)

        # Bygg instruktionslista från matchningar
        data_buf = bytearray()
        inst_buf = bytearray()
        addr_buf = bytearray()

        tgt_pos = 0

        def _emit_instruction(itype: int, size: int, mode: int,
                               addr_encoded: int, use_byte: bool):
            # Skriv opkod
            opcode, size_in_inst = find_opcode_single(itype, size, mode)
            inst_buf.append(opcode)
            if not size_in_inst:
                inst_buf.extend(encode_varint(size))
            if itype == COPY:
                if use_byte:
                    addr_buf.append(addr_encoded)
                else:
                    addr_buf.extend(encode_varint(addr_encoded))

        for (m_tgt_pos, m_len, m_addr, m_is_src) in matches:
            # Spola ut icke-matchade bytes före denna matchning som en ADD
            if tgt_pos < m_tgt_pos:
                add_data = target[tgt_pos:m_tgt_pos]
                add_len  = len(add_data)
                data_buf.extend(add_data)
                opcode, sii = find_opcode_single(ADD, add_len, 0)
                inst_buf.append(opcode)
                if not sii:
                    inst_buf.extend(encode_varint(add_len))
                tgt_pos += add_len

            here = src_len + tgt_pos

            enc_addr, mode, use_byte = self.cache.encode_address(m_addr, here)
            _emit_instruction(COPY, m_len, mode, enc_addr, use_byte)

            tgt_pos += m_len

        # Spola ut avslutande bytes
        if tgt_pos < len(target):
            add_data = target[tgt_pos:]
            add_len  = len(add_data)
            data_buf.extend(add_data)
            opcode, sii = find_opcode_single(ADD, add_len, 0)
            inst_buf.append(opcode)
            if not sii:
                inst_buf.extend(encode_varint(add_len))

        # Serialisera fönstret
        tgt_len = len(target)
        data_bytes = bytes(data_buf)
        inst_bytes = bytes(inst_buf)
        addr_bytes = bytes(addr_buf)

        win_ind = 0
        cpy_seg = b""
        if src_len > 0:
            win_ind |= VCD_SOURCE
            cpy_seg = encode_varint(src_len) + encode_varint(self.src_base)

        delta_indicator = DELTA_INDICATOR
        delta_enc  = (encode_varint(tgt_len)
                    + bytes([delta_indicator])
                    + encode_varint(len(data_bytes))
                    + encode_varint(len(inst_bytes))
                    + encode_varint(len(addr_bytes))
                    + data_bytes
                    + inst_bytes
                    + addr_bytes)

        window = (bytes([win_ind])
                 + cpy_seg
                 + encode_varint(len(delta_enc))
                 + delta_enc)
        return window


# Toppnivåkodare

def encode(source: bytes, target: bytes) -> bytes:
    # Producera en VCDIFF-patchbytes från source → target.
    out = bytearray()

    # Filhuvud: magiskt tal + hdr_indicator=0
    out.extend(VCDIFF_MAGIC)
    out.append(HDR_INDICATOR)

    # Bearbeta målet i fönster
    win_enc = WindowEncoder(source, src_base=0)
    offset  = 0
    while offset < len(target):
        chunk = target[offset:offset + WIN_SIZE]
        out.extend(win_enc.encode_window(chunk))
        offset += len(chunk)

    # Kantfall: tomt mål → emittera ett tomt fönster
    if len(target) == 0:
        out.extend(win_enc.encode_window(b""))

    return bytes(out)


# Batchbearbetning

RETAIL_DIR = Path("retail_roms")
KLARA_DIR  = Path("klara")
OUT_DIR    = Path("xdelta")

# Filpar: (källfil i retail_roms, målfil i klara)
FILE_PAIRS = [
    ("ntsc10_orig.z64",  "Tidens_okarina-NTSC10.z64"),
    ("ntsc11_orig.z64",  "Tidens_okarina-NTSC11.z64"),
    ("ntsc12_orig.z64",  "Tidens_okarina-NTSC12.z64"),
    ("ntscgc_orig.z64",  "Tidens_okarina-NTSCGC.z64"),
    ("ntscmq_orig.z64",  "Tidens_okarina-NTSCMQ.z64"),
    ("pal10_orig.z64",   "Tidens_okarina-PAL10.z64"),
    ("pal11_orig.z64",   "Tidens_okarina-PAL11.z64"),
    ("palgc_orig.z64",   "Tidens_okarina-PALGC.z64"),
    ("palmq_orig.z64",   "Tidens_okarina-PALMQ.z64"),
]


def main():
    for d in (RETAIL_DIR, KLARA_DIR):
        if not d.is_dir():
            print(f"FEL: mappen '{d}' hittades inte.")
            sys.exit(1)

    OUT_DIR.mkdir(exist_ok=True)

    print(f"Skapar {len(FILE_PAIRS)} patch(ar)...\n")

    ok = 0
    skipped = 0

    for source_name, target_name in FILE_PAIRS:
        source_path = RETAIL_DIR / source_name
        target_path = KLARA_DIR  / target_name

        if not source_path.exists():
            print(f"  [HOPPAR]  källfil saknas: {source_path}")
            skipped += 1
            continue
        if not target_path.exists():
            print(f"  [HOPPAR]  målfil saknas: {target_path}")
            skipped += 1
            continue

        out_name = target_path.stem + ".xdelta"
        out_path = OUT_DIR / out_name

        print(f"  {source_name}  +  {target_name}")
        print(f"  → {out_path}")

        source_bytes = source_path.read_bytes()
        target_bytes = target_path.read_bytes()

        print(f"  Skapar patch...", end="", flush=True)
        patch = encode(source_bytes, target_bytes)
        out_path.write_bytes(patch)

        ratio = len(patch) / max(len(target_bytes), 1) * 100
        print(f"  {len(patch):,} bytes  ({ratio:.1f}% av målfilen)\n")
        ok += 1

    print(f"Klar - {ok} patch(ar) sparade i '{OUT_DIR}/', {skipped} hoppade över.")


if __name__ == "__main__":
    main()