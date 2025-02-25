#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
MicBoard Sanal Ortam Kurulum Scripti
Bu script, MicBoard uygulaması için gerekli sanal ortamı oluşturur ve kütüphaneleri yükler.
Kullanım: python setup_venv.py
"""

import os
import sys
import subprocess
import shutil
import platform
import argparse
from pathlib import Path


def is_windows():
    """Mevcut işletim sisteminin Windows olup olmadığını kontrol eder."""
    return platform.system().lower() == "windows"


def create_venv(venv_path):
    """Belirtilen konumda sanal ortam oluşturur."""
    print(f"Sanal ortam oluşturuluyor: {venv_path}")
    subprocess.check_call([sys.executable, "-m", "venv", venv_path])
    print("Sanal ortam başarıyla oluşturuldu.")


def activate_venv(venv_path):
    """Sanal ortamı aktifleştirir ve gerekli yolu döndürür."""
    if is_windows():
        # Windows için
        python_path = os.path.join(venv_path, "Scripts", "python.exe")
        pip_path = os.path.join(venv_path, "Scripts", "pip.exe")
    else:
        # Linux/MacOS için
        python_path = os.path.join(venv_path, "bin", "python")
        pip_path = os.path.join(venv_path, "bin", "pip")
    
    if not os.path.exists(python_path):
        raise FileNotFoundError(f"Python yürütülebilir dosyası bulunamadı: {python_path}")
    
    return python_path, pip_path


def install_requirements(pip_path, requirements_path):
    """Gerekli kütüphaneleri kurar."""
    print(f"Gerekli kütüphaneler yükleniyor...")
    subprocess.check_call([pip_path, "install", "-r", requirements_path])
    
    # PyInstaller'ı ayrıca yükleyin
    print(f"PyInstaller yükleniyor...")
    subprocess.check_call([pip_path, "install", "pyinstaller"])
    print("Tüm gerekli kütüphaneler başarıyla yüklendi.")


def main():
    """Ana fonksiyon."""
    parser = argparse.ArgumentParser(description="MicBoard için sanal ortam kurulum aracı")
    parser.add_argument("--venv", help="Oluşturulacak sanal ortamın konumu", default="venv")
    parser.add_argument("--clean", action="store_true", help="Varolan sanal ortamı temizle ve yeniden oluştur")
    args = parser.parse_args()
    
    # Proje dizini
    project_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Sanal ortam dizini
    venv_dir = os.path.join(project_dir, args.venv)
    
    # Gereksinimler dosyası
    requirements_path = os.path.join(project_dir, "requirements.txt")
    
    # Daha önce oluşturulmuş bir venv varsa kaldır
    if args.clean and os.path.exists(venv_dir):
        print(f"Var olan sanal ortam temizleniyor: {venv_dir}")
        shutil.rmtree(venv_dir)
    
    try:
        # Sanal ortam mevcut mu kontrol et
        if os.path.exists(venv_dir):
            print(f"Sanal ortam zaten mevcut: {venv_dir}")
            print("Varolan sanal ortamı yeniden kullanmak için --clean parametresini kullanın.")
            python_path, pip_path = activate_venv(venv_dir)
        else:
            # Sanal ortam oluştur
            create_venv(venv_dir)
            
            # Sanal ortamı aktifleştir
            python_path, pip_path = activate_venv(venv_dir)
            
            # Gereksinimleri kur
            install_requirements(pip_path, requirements_path)
        
        print("\nSanal ortam kurulumu tamamlandı!")
        print(f"Python yolu: {python_path}")
        print(f"Pip yolu: {pip_path}")
        print("\nUygulamayı .exe'ye paketlemek için şimdi build_exe.py scriptini çalıştırabilirsiniz:")
        print("python build_exe.py")
        
    except Exception as e:
        print(f"Hata: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
