# core/command_new_setup.py
import os
import sys
import subprocess
import webbrowser
import shutil
from pathlib import Path
from datetime import datetime

from core.env_manager import choose_environment, load_env_config
from core.template_engine import create_default_templates, generate_readme
from core import env_manager

def run_command(cmd, cwd=None):
    try:
        subprocess.check_call(cmd, cwd=cwd, shell=True)
    except subprocess.CalledProcessError as e:
        print(f"❌ Error saat menjalankan: {cmd}")
        sys.exit(1)

def create_laravel_project(client_name, name, stack, init_git=False, with_filament=False, serve=False):
    """Membuat project Laravel baru otomatis + optional Filament dashboard + serve + auto-open browser"""
    env_name, base_path = choose_environment()
    project_path = base_path / name.replace(" ", "-")

    if project_path.exists():
        print(f"⚠️ Folder {project_path} sudah ada, hapus dulu atau gunakan nama lain.")
        sys.exit(1)

    print(f"🚀 Membuat Laravel project di {project_path} ...")
    os.makedirs(project_path, exist_ok=True)

    # 1️⃣ Install Laravel
    run_command(f"composer create-project laravel/laravel \"{project_path}\"")

    # 2️⃣ Tanya user untuk konfigurasi database
    print("\n🛠️  Konfigurasi Database Laravel:")
    db_name = input("Nama database (contoh: db_codesparks): ").strip()
    db_user = input("User database (default: root): ").strip() or "root"
    db_pass = input("Password database (boleh kosong): ").strip()

    # Edit file .env
    env_file = project_path / ".env"
    if env_file.exists():
        env_content = env_file.read_text(encoding="utf-8")
        env_content = (
            env_content.replace("DB_DATABASE=laravel", f"DB_DATABASE={db_name}")
                        .replace("DB_USERNAME=root", f"DB_USERNAME={db_user}")
                        .replace("DB_PASSWORD=", f"DB_PASSWORD={db_pass}")
        )
        env_file.write_text(env_content, encoding="utf-8")
        print(f"✅ File .env diperbarui dengan database: {db_name}")

    # 3️⃣ Jalankan migrasi awal
    print("🧱 Menjalankan migrasi awal database...")
    run_command("php artisan migrate", cwd=project_path)

    # 4️⃣ Jika user minta Filament
    if with_filament:
        print("⚡ Menginstal Filament Admin Panel...")
        run_command("composer require filament/filament:\"^3.0\" -W", cwd=project_path)

        # 🧩 Install Filament menggunakan panel default
        print("🧱 Menjalankan instalasi Filament (panel admin default)...")
        run_command("php artisan filament:install --panels --no-interaction", cwd=project_path)

        # ✅ Sekarang aman buat user admin
        print("👤 Membuat user admin awal (email: admin@example.com / password: password)")
        run_command("php artisan make:filament-user --name=Admin --email=admin@example.com --password=password", cwd=project_path)

        # 📦 Tambahkan contoh CRUD resource
        print("🧩 Membuat CRUD sample 'Post' di Filament...")
        run_command("php artisan make:filament-resource Post --generate", cwd=project_path)


    # 5️⃣ Tambahkan README
    create_default_templates()
    context = {
        "name": name,
        "client_name": client_name,
        "project_type": "laravel",
        "stack": stack,
        "created_at": datetime.utcnow().isoformat(),
    }
    generate_readme(project_path, context)

    # 6️⃣ Inisialisasi Git jika diminta
    if init_git:
        print("🌀 Inisialisasi Git repository...")
        run_command("git init", cwd=project_path)
        run_command("git add --all", cwd=project_path)
        run_command('git commit -m "chore: initial laravel scaffold by devcore"', cwd=project_path)

    print(f"✅ Laravel project berhasil dibuat di: {project_path}")

    # 7️⃣ Jalankan Laravel server jika diminta
    if serve:
        print("🚀 Menjalankan Laravel server di http://127.0.0.1:8000 ...")
        subprocess.Popen(["php", "artisan", "serve"], cwd=project_path)
        print("🖥️ Server Laravel berjalan di background (Ctrl+C untuk hentikan).")

        # 8️⃣ Buka browser otomatis
        try:
            print("🌐 Membuka browser otomatis...")
            webbrowser.open("http://127.0.0.1:8000")
        except Exception as e:
            print(f"⚠️ Gagal membuka browser otomatis: {e}")

    return str(project_path)