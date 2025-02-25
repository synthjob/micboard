# MicBoard 🎤⌨️

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python: 3.7+](https://img.shields.io/badge/python-3.7+-blue.svg)](https://www.python.org/downloads/)

MicBoard, mikrofondan alınan sesi gerçek zamanlı olarak metne dönüştüren ve bu metni klavye girişi olarak simüle eden bir uygulamadır. Uygulama, metin giriş alanlarında ellerinizi kullanmadan, sadece sesinizle metin oluşturmanıza olanak tanır.

![MicBoard Screenshot](https://example.com/screenshot.png)

## ✨ Özellikler

- 🎤 Gerçek zamanlı ses tanıma
- ⌨️ Karakterlerin tek tek ve doğal bir hızda yazılması
- 🔄 Metin formatlama (küçük harfe çevirme)
- 🖥️ Basit ve sade arayüz (sadece sistem tepsisi simgesi)
- 🟢 Aktif/Pasif mod desteği (renkli ikonlar)
- 🧵 Çoklu işlem tasarımı ile kesintisiz çalışma

## 🚀 Kurulum

```bash
# Gerekli kütüphaneleri yükleyin
pip install -r requirements.txt
```

## 🔧 Kullanım

Uygulamayı başlatmak için:

```bash
python micboard.py
```

### 🎮 Kontroller

- **Sol tıklama**: Aktif/Pasif modu değiştirir
- **Sağ tıklama**: Uygulamayı kapatır

## 📦 Paketleme

MicBoard'u tek bir .exe dosyası olarak paketlemek için aşağıdaki adımları izleyin:

1. İlk olarak sanal ortamı kurun:
```bash
python setup_venv.py
```

2. Ardından uygulamayı .exe dosyasına dönüştürün:
```bash
python build_exe.py
```

Paketleme işlemi tamamlandığında, `dist` klasöründe `MicBoard.exe` dosyasını bulabilirsiniz.

## 📋 Gereksinimler

- Python 3.7 veya üzeri
- PyQt5 - Sistem tepsisi arayüzü için
- SpeechRecognition - Konuşma tanıma için
- pyaudio - Ses kaydı için
- pynput - Klavye simülasyonu için

## 🔍 Nasıl Çalışır?

MicBoard, birbirleriyle iletişim kuran birkaç bağımsız bileşenden oluşur:

1. **AudioRecorder**: Mikrofonu dinler ve ses parçalarını algılar
2. **SpeechRecognizer**: Ses parçalarını metne dönüştürür
3. **KeyboardSimulator**: Metni klavye girişi olarak simüle eder

Bu bileşenler birbirleriyle kuyruk veri yapıları üzerinden iletişim kurar.

## 🛠️ Sorun Giderme

### Ses tanıma çalışmıyor:
- Mikrofonunuzun açık ve çalışır durumda olduğundan emin olun
- İnternet bağlantınızı kontrol edin (Google Speech API kullanılmaktadır)
- Sistem ses ayarlarında mikrofonun varsayılan giriş cihazı olarak ayarlandığından emin olun

### Klavye simülasyonu çalışmıyor:
- Uygulamayı yönetici olarak çalıştırın
- Başka bir metin düzenleyicide deneyin

## 📜 Lisans

Bu proje MIT Lisansı altında lisanslanmıştır - daha fazla bilgi için [LICENSE](LICENSE) dosyasına bakın.
