import os

def check_settings_file(settings_path, injection_folder):
    with open(settings_path, 'r', encoding='utf-8') as file:
        lines = file.readlines()
    
    missing_files = []
    found_files = []
    subfolder = ''
    
    for line in lines:
        if not line.strip() or line.strip().startswith('#'):
            continue
        parts = line.strip().split()
        
        if parts[0] == 'Dir':
            subfolder = parts[1]
        elif parts[0] == 'Exp':
            name = parts[3]
            expected_path = os.path.join(injection_folder, subfolder, f"{name}.png")
            
            if os.path.exists(expected_path):
                found_files.append(expected_path)
            else:
                missing_files.append(expected_path)
    
    return missing_files, found_files, len(missing_files) + len(found_files)

def main():
    settings_folder = 'extrsettings'
    injection_folder = 'injection'
    
    # Kontrollera att mapparna finns
    if not os.path.exists(settings_folder):
        print(f"FEL: Mappen '{settings_folder}' finns inte!")
        return
    
    if not os.path.exists(injection_folder):
        print(f"FEL: Mappen '{injection_folder}' finns inte!")
        return
    
    print("=" * 70)
    print("VERIFIERING AV INJEKTIONSFILER")
    print("=" * 70)
    
    # Hämta alla settingsfiler
    settings_files = [f for f in os.listdir(settings_folder) if f.endswith('.txt')]
    
    if not settings_files:
        print(f"Inga settingsfiler hittades i '{settings_folder}'")
        return
    
    total_missing = 0
    total_found = 0
    total_files = 0
    all_missing = set()
    
    # Kontrollera varje settingsfil
    for settings_file in sorted(settings_files):
        settings_path = os.path.join(settings_folder, settings_file)
        
        print(f"\n{settings_file}")
        print("-" * 70)
        
        missing, found, total = check_settings_file(settings_path, injection_folder)
        
        total_missing += len(missing)
        total_found += len(found)
        total_files += total
        
        if missing:
            print(f"  ✗ SAKNAS: {len(missing)} filer")
            for mf in missing:
                print(f"     - {mf}")
                all_missing.add(mf)
        
        if found:
            print(f"  ✓ FINNS: {len(found)} filer")
        
        if total > 0:
            percentage = (len(found) / total) * 100
            print(f"  Status: {len(found)}/{total} ({percentage:.1f}%)")
    
    # Sammanfattning
    print("\n" + "=" * 70)
    print("SAMMANFATTNING")
    print("=" * 70)
    print(f"Totalt antal filer refererade: {total_files}")
    print(f"Hittade: {total_found}")
    print(f"Saknas: {total_missing}")
    
    if total_files > 0:
        percentage = (total_found / total_files) * 100
        print(f"Täckning: {percentage:.1f}%")
    
    if all_missing:
        print(f"\n{'=' * 70}")
        print(f"UNIKA FILER SOM SAKNAS ({len(all_missing)} st):")
        print("=" * 70)
        for mf in sorted(all_missing):
            print(f"  - {mf}")
    
    print("\n" + "=" * 70)
    if total_missing == 0:
        print("✓ ALLA FILER FINNS! Redo för injektering.")
    else:
        print("✗ VISSA FILER SAKNAS. Lägg till dessa innan injektering.")
    print("=" * 70)

if __name__ == '__main__':
    main()
