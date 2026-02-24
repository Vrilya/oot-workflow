import os
from PIL import Image
import numpy as np


# Hjälpfunktioner för bitexpansion och nedskalning

def expand_3_to_8(v3: int) -> int:
    # 3 bitar till 8 bitar: (v<<5)|(v<<2)|(v>>1)
    v3 &= 0x7
    return (v3 << 5) | (v3 << 2) | (v3 >> 1)

def expand_4_to_8(v4: int) -> int:
    # 4 bitar till 8 bitar: (v<<4)|v
    v4 &= 0xF
    return (v4 << 4) | v4

def expand_5_to_8(v5: int) -> int:
    # 5 bitar till 8 bitar: (v<<3)|(v>>2)
    v5 &= 0x1F
    return (v5 << 3) | (v5 >> 2)

def scale_8_to_3(value: int) -> int:
    # 8 bitar till 3 bitar
    return (int(value) >> 5) & 0x7

def scale_8_to_4(value: int) -> int:
    # 8 bitar till 4 bitar
    return (int(value) >> 4) & 0xF

def scale_8_to_5(value: int) -> int:
    # 8 bitar till 5 bitar
    return (int(value) >> 3) & 0x1F


# Avkodning N64 -> PNG-buffert

def decode_to_png_array_and_mode(data: bytes, width: int, height: int, fmt: str):
    format_norm = fmt.upper()
    if format_norm == 'RGBA3':
        format_norm = 'RGBA16'

    if format_norm == 'I4':
        # 2 pixlar per byte, 4 bit grå som expanderas till 8 och dupliceras till RGB
        img = np.zeros((height, width, 3), dtype=np.uint8)
        idx = 0
        for y in range(height):
            for x in range(0, width, 2):
                byte = data[idx]
                idx += 1
                g0_4 = (byte >> 4) & 0xF
                g1_4 = byte & 0xF
                g0 = expand_4_to_8(g0_4)
                g1 = expand_4_to_8(g1_4)
                img[y, x, :] = [g0, g0, g0]
                if x + 1 < width:
                    img[y, x + 1, :] = [g1, g1, g1]
        return img, 'RGB'

    elif format_norm == 'I8':
        # 1 pixel per byte, ren gråskala dupliceras till RGB
        img = np.zeros((height, width, 3), dtype=np.uint8)
        idx = 0
        for y in range(height):
            for x in range(width):
                g = data[idx]
                idx += 1
                img[y, x, :] = [g, g, g]
        return img, 'RGB'

    elif format_norm == 'IA4':
        # 2 pixlar per byte, varje nibble: ggg a
        img = np.zeros((height, width, 4), dtype=np.uint8)
        idx = 0
        for y in range(height):
            for x in range(0, width, 2):
                byte = data[idx]
                idx += 1
                for i in range(2):
                    nibble = (byte >> 4) & 0xF if i == 0 else (byte & 0xF)
                    grayscale_4bit = nibble & 0b1110  # Behåll 4-bit struktur
                    a1 = nibble & 0x1
                    g = (grayscale_4bit << 4) | (grayscale_4bit << 1) | (grayscale_4bit >> 2)
                    a = 255 if a1 else 0
                    xx = x + i
                    if xx < width:
                        img[y, xx, :] = [g, g, g, a]
        return img, 'RGBA'

    elif format_norm == 'IA8':
        # 1 byte per pixel, övre 4 bit grå, nedre 4 bit alfa
        img = np.zeros((height, width, 4), dtype=np.uint8)
        idx = 0
        for y in range(height):
            for x in range(width):
                byte = data[idx]
                idx += 1
                g4 = (byte >> 4) & 0xF
                a4 = byte & 0xF
                g = expand_4_to_8(g4)
                a = expand_4_to_8(a4)
                img[y, x, :] = [g, g, g, a]
        return img, 'RGBA'

    elif format_norm == 'IA16':
        # 2 byte per pixel, 8 bit grå och 8 bit alfa
        img = np.zeros((height, width, 4), dtype=np.uint8)
        idx = 0
        for y in range(height):
            for x in range(width):
                g = data[idx]
                a = data[idx + 1]
                idx += 2
                img[y, x, :] = [g, g, g, a]
        return img, 'RGBA'

    elif format_norm == 'RGBA16':
        # 2 byte per pixel, rgb5a1
        img = np.zeros((height, width, 4), dtype=np.uint8)
        idx = 0
        for y in range(height):
            for x in range(width):
                hi = data[idx]
                lo = data[idx + 1]
                idx += 2
                val = (hi << 8) | lo
                r5 = (val >> 11) & 0x1F
                g5 = (val >> 6) & 0x1F
                b5 = (val >> 1) & 0x1F
                a1 = val & 0x1
                r = expand_5_to_8(r5)
                g = expand_5_to_8(g5)
                b = expand_5_to_8(b5)
                a = 255 if a1 else 0
                img[y, x, :] = [r, g, b, a]
        return img, 'RGBA'

    elif format_norm == 'RGBA32':
        # 4 byte per pixel, 8 bit vardera för RGBA
        img = np.zeros((height, width, 4), dtype=np.uint8)
        idx = 0
        for y in range(height):
            for x in range(width):
                r = data[idx]
                g = data[idx + 1]
                b = data[idx + 2]
                a = data[idx + 3]
                idx += 4
                img[y, x, :] = [r, g, b, a]
        return img, 'RGBA'

    else:
        raise ValueError(f"Okänt eller ej implementerat format: {fmt}")

# Kodning PNG-buffert -> N64

def encode_from_png_array(img_array: np.ndarray, fmt: str) -> bytearray:
    format_norm = fmt.upper()
    if format_norm == 'RGBA3':
        format_norm = 'RGBA16'

    h, w = img_array.shape[0], img_array.shape[1]
    out = bytearray()

    if format_norm == 'I4':
        # Förväntar gråskaleinnehåll, använd rödkanalen om 3-kanalers RGB
        if img_array.ndim == 3 and img_array.shape[2] == 3:
            gray = img_array[:, :, 0]
        elif img_array.ndim == 2:
            gray = img_array
        else:
            # Om det är RGBA, ta r
            gray = img_array[:, :, 0]
        for y in range(h):
            x = 0
            while x < w:
                g0 = scale_8_to_4(int(gray[y, x]))
                if x + 1 < w:
                    g1 = scale_8_to_4(int(gray[y, x + 1]))
                else:
                    g1 = 0
                out.append((g0 << 4) | g1)
                x += 2
        return out

    elif format_norm == 'I8':
        if img_array.ndim == 3:
            gray = img_array[:, :, 0]
        else:
            gray = img_array
        for y in range(h):
            for x in range(w):
                out.append(int(gray[y, x]) & 0xFF)
        return out

    elif format_norm == 'IA4':
        # Källa ska vara grå med alfa. Om RGB eller RGBA, använd r och alpha.
        if img_array.ndim == 2:
            r = img_array
            a = np.full_like(r, 255)
        elif img_array.shape[2] == 4:
            r = img_array[:, :, 0]
            a = img_array[:, :, 3]
        elif img_array.shape[2] == 2:
            r = img_array[:, :, 0]
            a = img_array[:, :, 1]
        else:
            r = img_array[:, :, 0]
            a = np.full((h, w), 255, dtype=np.uint8)

        for y in range(h):
            x = 0
            while x < w:
                g0_3 = scale_8_to_3(int(r[y, x]))
                a0_1 = 1 if int(a[y, x]) != 0 else 0
                nib0 = ((g0_3 << 1) & 0xE) | a0_1

                if x + 1 < w:
                    g1_3 = scale_8_to_3(int(r[y, x + 1]))
                    a1_1 = 1 if int(a[y, x + 1]) != 0 else 0
                    nib1 = ((g1_3 << 1) & 0xE) | a1_1
                else:
                    nib1 = 0

                out.append(((nib0 & 0xF) << 4) | (nib1 & 0xF))
                x += 2
        return out

    elif format_norm == 'IA8':
        # 4 bit grå, 4 bit alfa
        if img_array.ndim == 2:
            r = img_array
            a = np.full_like(r, 255)
        elif img_array.shape[2] == 4:
            r = img_array[:, :, 0]
            a = img_array[:, :, 3]
        elif img_array.shape[2] == 2:
            r = img_array[:, :, 0]
            a = img_array[:, :, 1]
        else:
            r = img_array[:, :, 0]
            a = np.full((h, w), 255, dtype=np.uint8)

        for y in range(h):
            for x in range(w):
                g4 = scale_8_to_4(int(r[y, x]))
                a4 = scale_8_to_4(int(a[y, x]))
                out.append(((g4 & 0xF) << 4) | (a4 & 0xF))
        return out

    elif format_norm == 'IA16':
        # 8 bit grå och 8 bit alfa
        if img_array.ndim == 2:
            r = img_array
            a = np.full_like(r, 255)
        elif img_array.shape[2] == 4:
            r = img_array[:, :, 0]
            a = img_array[:, :, 3]
        elif img_array.shape[2] == 2:
            r = img_array[:, :, 0]
            a = img_array[:, :, 1]
        else:
            r = img_array[:, :, 0]
            a = np.full((h, w), 255, dtype=np.uint8)

        for y in range(h):
            for x in range(w):
                out.append(int(r[y, x]) & 0xFF)
                out.append(int(a[y, x]) & 0xFF)
        return out

    elif format_norm == 'RGBA16':
        # 5 bit r, 5 bit g, 5 bit b, 1 bit a
        # Alfabit via tröskel 128, inte bara a!=0
        if img_array.ndim == 2:
            r = g = b = img_array
            a = np.full_like(r, 255)
        elif img_array.shape[2] == 4:
            r = img_array[:, :, 0]
            g = img_array[:, :, 1]
            b = img_array[:, :, 2]
            a = img_array[:, :, 3]
        elif img_array.shape[2] == 3:
            r = img_array[:, :, 0]
            g = img_array[:, :, 1]
            b = img_array[:, :, 2]
            a = np.full((h, w), 255, dtype=np.uint8)
        else:
            raise ValueError("Oväntat bildformat vid RGBA16-kodning")

        for y in range(h):
            for x in range(w):
                R5 = scale_8_to_5(int(r[y, x]))
                G5 = scale_8_to_5(int(g[y, x]))
                B5 = scale_8_to_5(int(b[y, x]))
                A1 = 1 if int(a[y, x]) != 0 else 0
                word = ((R5 & 0x1F) << 11) | ((G5 & 0x1F) << 6) | ((B5 & 0x1F) << 1) | (A1 & 0x1)
                out.append((word >> 8) & 0xFF)
                out.append(word & 0xFF)
        return out

    elif format_norm == 'RGBA32':
        # 8 bit vardera för RGBA, 4 byte per pixel
        if img_array.ndim == 2:
            r = g = b = img_array
            a = np.full_like(r, 255)
        elif img_array.shape[2] == 4:
            r = img_array[:, :, 0]
            g = img_array[:, :, 1]
            b = img_array[:, :, 2]
            a = img_array[:, :, 3]
        elif img_array.shape[2] == 3:
            r = img_array[:, :, 0]
            g = img_array[:, :, 1]
            b = img_array[:, :, 2]
            a = np.full((h, w), 255, dtype=np.uint8)
        else:
            raise ValueError("Oväntat bildformat vid RGBA32-kodning")

        for y in range(h):
            for x in range(w):
                out.append(int(r[y, x]) & 0xFF)
                out.append(int(g[y, x]) & 0xFF)
                out.append(int(b[y, x]) & 0xFF)
                out.append(int(a[y, x]) & 0xFF)
        return out

    else:
        raise ValueError(f"Okänt eller ej implementerat format: {fmt}")

# Injektionsfunktioner

def inject_image(filename, input_image_path, width, height, fmt, address):
    try:
        fmt_norm = fmt.upper()
        if fmt_norm == 'RGBA3':
            fmt_norm = 'RGBA16'

        # Välj korrekt PIL-mode för inläsning före kodning
        if fmt_norm in ['I4', 'I8']:
            pil_mode = 'L'         # gråskala utan alfa
        elif fmt_norm in ['IA4', 'IA8', 'IA16']:
            pil_mode = 'LA'        # gråskala med alfa
        elif fmt_norm in ['RGBA16', 'RGBA32']:
            pil_mode = 'RGBA'      # färg med alfa
        else:
            raise ValueError(f"Okänt format: {fmt}")

        print(f"  Öppnar bild för injektering: {input_image_path}")
        image = Image.open(input_image_path).convert(pil_mode).resize((width, height))
        img_array = np.array(image)

        encoded = encode_from_png_array(img_array, fmt_norm)

        with open(filename, 'r+b') as f:
            f.seek(address)
            f.write(encoded)
            print(f"  Injicerat '{input_image_path}' till '{filename}' på adress {address:X}")
    except Exception as e:
        print(f"  Fel vid injektering av '{input_image_path}': {e}")

def parse_settings_and_inject(settings_path, rom_path, injection_folder):
    # Läser en settingsfil och injicerar alla bilder från injection_folder till rom_path
    print(f"\nBearbetar: {os.path.basename(rom_path)}")
    print(f"Använder settings: {os.path.basename(settings_path)}")
    
    with open(settings_path, 'r', encoding='utf-8') as file:
        lines = file.readlines()

    width = height = None
    subfolder = ''
    injection_count = 0
    
    for line in lines:
        if not line.strip() or line.strip().startswith('#'):
            continue
        parts = line.strip().split()
        if parts[0] == 'Dir':
            subfolder = parts[1]
        elif parts[0] == 'Set' and parts[1] == 'TexS':
            size = parts[2].split('x')
            width, height = map(int, size)
        elif parts[0] == 'Exp':
            current_format = parts[1]
            address = int(parts[2], 16)
            name = parts[3]
            input_image_path = os.path.join(injection_folder, subfolder, f"{name}.png")
            if os.path.exists(input_image_path):
                inject_image(rom_path, input_image_path, width, height, current_format, address)
                injection_count += 1
            else:
                print(f"  Varning: Filen '{input_image_path}' hittades inte.")
    
    print(f"Totalt {injection_count} bilder injicerade till {os.path.basename(rom_path)}")

# Huvudprogram

def main():
    # Definiera mappar
    settings_folder = 'extrsettings'
    roms_folder = 'roms'
    injection_folder = 'injection'
    
    # Kontrollera att mapparna finns
    for folder in [settings_folder, roms_folder, injection_folder]:
        if not os.path.exists(folder):
            print(f"FEL: Mappen '{folder}' finns inte!")
            return
    
    # Definiera mappning mellan rommar och settingsfiler
    rom_settings_map = {
        'Tidens_okarina-NTSC10.z64': 'NTSC SWE v1.0.txt',
        'Tidens_okarina-NTSC11.z64': 'NTSC SWE v1.1.txt',
        'Tidens_okarina-NTSC12.z64': 'NTSC SWE v1.2.txt',
        'Tidens_okarina-NTSCGC.z64': 'NTSC SWE GC.txt',
        'Tidens_okarina-NTSCMQ.z64': 'NTSC SWE MQ.txt',
        'Tidens_okarina-PAL10.z64': 'PAL SWE v1.0.txt',
        'Tidens_okarina-PAL11.z64': 'PAL SWE v1.1.txt',
        'Tidens_okarina-PALGC.z64': 'PAL SWE GC.txt',
        'Tidens_okarina-PALMQ.z64': 'PAL SWE MQ.txt',
        'Tidens_okarina-PALOTR.z64': 'PAL OTR.txt'
    }
    
    print("=" * 60)
    print("BATCH INJEKTERING - ZELDA: OCARINA OF TIME")
    print("=" * 60)
    
    # Gå igenom alla rommar
    total_roms = 0
    successful_roms = 0
    
    for rom_name, settings_name in rom_settings_map.items():
        rom_path = os.path.join(roms_folder, rom_name)
        settings_path = os.path.join(settings_folder, settings_name)
        
        # Kontrollera att både rom och settings finns
        if not os.path.exists(rom_path):
            print(f"\nVarning: Rom '{rom_name}' finns inte, hoppar över.")
            continue
        
        if not os.path.exists(settings_path):
            print(f"\nVarning: Settingsfil '{settings_name}' finns inte, hoppar över {rom_name}.")
            continue
        
        total_roms += 1
        
        try:
            parse_settings_and_inject(settings_path, rom_path, injection_folder)
            successful_roms += 1
        except Exception as e:
            print(f"\nFEL vid bearbetning av {rom_name}: {e}")
    
    print("\n" + "=" * 60)
    print(f"KLART! {successful_roms}/{total_roms} rommar bearbetade framgångsrikt.")
    print("=" * 60)

if __name__ == '__main__':
    main()