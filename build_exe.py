#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
MicBoard .exe Paketleme Scripti
Bu script, MicBoard uygulamasını Windows için tek başına çalışabilir .exe dosyasına paketler.
Not: Önce setup_venv.py ile sanal ortamı kurmuş olmanız gerekmektedir.
Kullanım: python build_exe.py
"""

import os
import sys
import subprocess
import platform
import argparse
from pathlib import Path


def is_windows():
    """Mevcut işletim sisteminin Windows olup olmadığını kontrol eder."""
    return platform.system().lower() == "windows"


def activate_venv(venv_path):
    """Sanal ortamı aktifleştirir ve gerekli yolu döndürür."""
    if is_windows():
        # Windows için
        python_path = os.path.join(venv_path, "Scripts", "python.exe")
        pyinstaller_path = os.path.join(venv_path, "Scripts", "pyinstaller.exe")
    else:
        # Linux/MacOS için
        python_path = os.path.join(venv_path, "bin", "python")
        pyinstaller_path = os.path.join(venv_path, "bin", "pyinstaller")
    
    if not os.path.exists(python_path):
        raise FileNotFoundError(f"Python yürütülebilir dosyası bulunamadı: {python_path}")
    
    if not os.path.exists(pyinstaller_path):
        raise FileNotFoundError(f"PyInstaller bulunamadı. Lütfen önce setup_venv.py çalıştırın.")
    
    return python_path, pyinstaller_path


def create_icon(output_path, python_path):
    """Programatik olarak ikon dosyası oluşturur."""
    print(f"İkon oluşturuluyor: {output_path}")
    
    # İkon oluşturmak için geçici bir script oluştur
    icon_script = """
from PyQt5.QtGui import QIcon, QPixmap, QPainter, QColor
from PyQt5.QtCore import Qt
import sys

def create_icon(output_path):
    # Geçici bir .ico dosyası oluştur
    size = 128
    pixmap = QPixmap(size, size)
    pixmap.fill(Qt.transparent)
    
    # Yeşil ikonu çiz (aktif ikon)
    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.Antialiasing)
    
    # Arka plan dairesi
    painter.setBrush(QColor("#4CAF50"))
    painter.setPen(Qt.NoPen)
    painter.drawEllipse(4, 4, size-8, size-8)
    
    # Mikrofon simgesi
    painter.setBrush(QColor("white"))
    center_x = size // 2
    center_y = size // 2
    
    # Mikrofon gövdesi
    mic_width = size // 4
    mic_height = size // 3
    painter.drawRoundedRect(center_x - mic_width//2, center_y - mic_height//2, 
                        mic_width, mic_height, mic_width//4, mic_width//4)
    
    # Mikrofon ayağı ve tabanı
    stand_width = size // 12
    stand_height = size // 6
    painter.drawRect(center_x - stand_width//2, center_y + mic_height//2, 
                    stand_width, stand_height)
    
    base_width = size // 3
    base_height = size // 16
    painter.drawRect(center_x - base_width//2, center_y + mic_height//2 + stand_height - base_height//2, 
                    base_width, base_height)
    
    painter.end()
    
    # İkonu kaydet
    print(f"İkon kaydediliyor: {output_path}")
    pixmap.save(output_path, "ICO")
    return True

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Kullanım: python create_icon.py ÇIKTI_DOSYASI")
        sys.exit(1)
    
    output_path = sys.argv[1]
    success = create_icon(output_path)
    sys.exit(0 if success else 1)
"""
    
    # Geçici dosyayı oluştur
    temp_script = os.path.join(os.path.dirname(output_path), "create_icon_temp.py")
    with open(temp_script, "w", encoding="utf-8") as f:
        f.write(icon_script)
    
    try:
        # İkon oluşturma scriptini çalıştır
        subprocess.check_call([python_path, temp_script, output_path])
        print(f"İkon başarıyla oluşturuldu: {output_path}")
        return True
    except Exception as e:
        print(f"İkon oluşturulurken hata: {e}")
        return False
    finally:
        # Geçici dosyayı temizle
        if os.path.exists(temp_script):
            os.remove(temp_script)


def build_executable(pyinstaller_path, app_path, output_dir, icon_path=None):
    """PyInstaller kullanarak uygulamayı .exe olarak paketler."""
    print(f"Uygulama .exe'ye paketleniyor...")
    
    cmd = [
        pyinstaller_path,
        "--onefile",
        "--windowed",
        "--clean",
        "--name", "MicBoard"
    ]
    
    # İkon belirtilmişse ekle
    if icon_path and os.path.exists(icon_path):
        cmd.extend(["--icon", icon_path])
    
    # Çıktı dizini belirtilmişse ekle
    if output_dir:
        cmd.extend(["--distpath", output_dir])
    
    # Uygulama dosyasını ekle
    cmd.append(app_path)
    
    subprocess.check_call(cmd)
    print(f"Uygulama başarıyla paketlendi!")


def main():
    """Ana fonksiyon."""
    parser = argparse.ArgumentParser(description="MicBoard .exe paketleme aracı")
    parser.add_argument("--venv", help="Kullanılacak sanal ortamın konumu", default="venv")
    parser.add_argument("--output", help="Paketlenmiş uygulamanın çıktı dizini", default="dist")
    parser.add_argument("--icon", help="Kullanılacak ikon dosyası (oluşturulacaksa konum)")
    args = parser.parse_args()
    
    # Proje dizini
    project_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Sanal ortam dizini
    venv_dir = os.path.join(project_dir, args.venv)
    
    # Uygulama ve çıktı
    app_path = os.path.join(project_dir, "micboard.py")
    output_dir = os.path.join(project_dir, args.output)
    
    # İkon dosyası
    icon_path = args.icon if args.icon else os.path.join(project_dir, "icon.ico")
    
    # Windows olmayan sistemlerde uyarı ver
    if not is_windows():
        print("Uyarı: Windows dışı bir işletim sistemi algılandı. PyInstaller Windows dışında Windows için .exe oluşturamaz.")
    
    try:
        # Sanal ortamı kontrol et
        if not os.path.exists(venv_dir):
            print(f"Sanal ortam bulunamadı: {venv_dir}")
            print("Lütfen önce setup_venv.py çalıştırarak sanal ortamı kurun:")
            print("python setup_venv.py")
            sys.exit(1)
        
        # Sanal ortamı aktifleştir
        python_path, pyinstaller_path = activate_venv(venv_dir)
        
        # İkon dosyası oluştur (belirtilmediyse)
        if not os.path.exists(icon_path):
            create_icon(icon_path, python_path)
        
        # Çıktı dizini oluştur (yoksa)
        os.makedirs(output_dir, exist_ok=True)
        
        # .exe olarak paketle
        build_executable(pyinstaller_path, app_path, output_dir, icon_path)
        
        print("\nPaketleme işlemi tamamlandı!")
        print(f"Uygulamanız şu konumda bulunabilir: {os.path.join(output_dir, 'MicBoard.exe')}")
        
    except Exception as e:
        print(f"Hata: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
