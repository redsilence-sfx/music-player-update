import os
import sys
import subprocess

# ============================================================
# SOUNDWAVE RUNNING SYSTEM
# Install dependencies + install theme once + run app
# ============================================================

PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))

python_path = r"C:\Users\sirodex\AppData\Local\Programs\Python\Python311\python.exe"

if not os.path.exists(python_path):
    print("❌ Python 3.11 tidak ditemukan di path tersebut!")
    print(f"Path dicek: {python_path}")
    sys.exit(1)


# ============================================================
# 1. INSTALL LIBRARIES
# ============================================================

libraries = {
    "PyQt5": "PyQt5",
    "pygame": "pygame",
    "colorama": "colorama",
    "requests": "requests",
    "python-dotenv": "dotenv",
    "mutagen": "mutagen",
}

print("\n🔍 Mengecek library...\n")

for package_name, import_name in libraries.items():
    try:
        __import__(import_name)
        print(f"✅ {package_name} sudah terinstall")
    except ImportError:
        print(f"📦 {package_name} sedang diinstall...")
        subprocess.check_call([
            python_path,
            "-m",
            "pip",
            "install",
            package_name
        ])


# ============================================================
# 2. INSTALL THEME CUSTOMIZATION ONCE
# ============================================================

config_dir = os.path.join(PROJECT_ROOT, "config")
theme_marker = os.path.join(config_dir, "theme_installed.flag")
theme_installer = os.path.join(PROJECT_ROOT, "scripts", "install_theme_customization.py")

os.makedirs(config_dir, exist_ok=True)

if os.path.exists(theme_installer):
    if not os.path.exists(theme_marker):
        print("\n🎨 Theme Customization belum terpasang.")
        print("⚙️ Menginstall Theme Customization...\n")

        try:
            subprocess.check_call([
                python_path,
                theme_installer
            ], cwd=PROJECT_ROOT)

            with open(theme_marker, "w", encoding="utf-8") as f:
                f.write("Theme customization installed successfully.\n")

            print("\n✅ Theme Customization berhasil dipasang!")

        except subprocess.CalledProcessError as e:
            print("\n❌ Gagal menginstall Theme Customization!")
            print(f"Error: {e}")
            print("Aplikasi tidak dijalankan dulu agar file tidak makin rusak.")
            sys.exit(1)
    else:
        print("✅ Theme Customization sudah pernah dipasang")
else:
    print("⚠️ Installer Theme tidak ditemukan, dilewati")
    print(f"Dicari di: {theme_installer}")


# ============================================================
# 3. RUN SOUNDWAVE
# ============================================================

main_file = os.path.join(PROJECT_ROOT, "main.py")

if not os.path.exists(main_file):
    print("\n❌ main.py tidak ditemukan!")
    print(f"Dicari di: {main_file}")
    sys.exit(1)

print("\n🚀 Menjalankan SoundWave...\n")

subprocess.call([
    python_path,
    main_file
], cwd=PROJECT_ROOT)