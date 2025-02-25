# MicBoard 🎤⌨️

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python: 3.7+](https://img.shields.io/badge/python-3.7+-blue.svg)](https://www.python.org/downloads/)

MicBoard, mikrofondan alınan sesi gerçek zamanlı olarak metne dönüştüren ve bu metni klavye girişi olarak simüle eden bir uygulamadır. Ellerinizi kullanmadan sadece konuşarak metin yazmanıza olanak sağlar. Sistem tepsisinde çalışan basit ve kullanımı kolay bir arayüze sahiptir.

## ✨ Özellikler

- 🎤 Gerçek zamanlı ses tanıma ve konuşma çevirisi
- ⌨️ Metni doğal yazım hızıyla otomatik olarak yazma
- 🔄 Metin formatlama (küçük harfe çevirme gibi)
- 🖥️ Sistem tepsisinde çalışan sade ve kullanışlı arayüz
- 🟢 Çift renkli ikon ile aktif/pasif mod gösterimi
- 🧵 Çoklu işlem mimarisi ile kesintisiz performans
- 🔌 Kolay kurulum ve tek tıkla çalıştırma

## 📋 Sistem Gereksinimleri

- Python 3.7 veya üzeri
- Windows/macOS/Linux işletim sistemleri
- İnternet bağlantısı (Google Speech API kullanımı için)
- Çalışan bir mikrofon

## 🚀 Kurulum

### Normal Kurulum (Geliştirici Modu)

1. Bu depoyu bilgisayarınıza klonlayın:
```bash
git clone https://github.com/synthjob/micboard.git
cd micboard
```

2. Gerekli kütüphaneleri yükleyin:
```bash
pip install -r requirements.txt
```

3. Uygulamayı başlatın:
```bash
python micboard.py
```

### Windows .exe Olarak Kurulum

1. İlk olarak sanal ortamı kurun:
```bash
python setup_venv.py
```

2. Uygulamayı .exe dosyasına dönüştürün:
```bash
python build_exe.py
```

3. `dist` klasöründe oluşturulan `MicBoard.exe` dosyasını çalıştırın.

## 🔧 Kullanım

Uygulama başlatıldığında sistem tepsisinde bir mikrofon simgesi görünecektir:

- **Yeşil mikrofon**: Aktif mod - ses dinleniyor ve metne dönüştürülüyor
- **Kırmızı mikrofon**: Pasif mod - ses dinleme kapalı

### Kontrol Seçenekleri

- **Sol tıklama**: Aktif/Pasif modları arasında geçiş yapar
- **Sağ tıklama**: Menüyü açar (Kapat seçeneği içerir)

## 🧩 Uygulama Mimarisi

MicBoard, paralel çalışan üç temel bileşenden oluşur:

1. **AudioRecorder** - Mikrofonu sürekli dinler ve ses parçalarını yakalar
2. **SpeechRecognizer** - Ses parçalarını Google Speech API ile metne dönüştürür
3. **KeyboardSimulator** - Dönüştürülen metni doğal bir yazım hızıyla klavye tuşlarına çevirir

Bileşenler arasındaki veri akışı kuyruk veri yapıları ile sağlanır ve her bileşen ayrı bir iş parçacığında çalışır.

## 🛠️ Sorun Giderme

### Ses tanıma çalışmıyor:
- Mikrofonunuzun açık ve çalışır durumda olduğundan emin olun
- İnternet bağlantınızı kontrol edin (Google Speech API kullanılmaktadır)
- Sistem ses ayarlarında mikrofonun varsayılan giriş cihazı olarak ayarlandığından emin olun
- Gürültülü ortamlarda ses tanıma doğruluğu düşebilir

### Klavye simülasyonu çalışmıyor:
- Uygulamayı yönetici olarak çalıştırın
- Başka bir metin düzenleyicide deneyin
- Bazı güvenlik yazılımları klavye simülasyonunu engelleyebilir

## 🔍 Teknik Detaylar

MicBoard aşağıdaki ana kütüphaneleri kullanır:

- **PyQt5**: Sistem tepsisi arayüzü için 
- **SpeechRecognition**: Konuşma tanıma için
- **PyAudio**: Ses kaydı için
- **pynput**: Klavye simülasyonu için

Uygulama, üç farklı süreç arasında veri paylaşımı için iş parçacıkları arası iletişim kullanır ve bu sayede kullanıcı deneyimini kesintisiz tutar.

## 📄 Lisans

Bu proje MIT Lisansı altında lisanslanmıştır - detaylar için [LICENSE](LICENSE) dosyasına bakın.

## 👨‍💻 Katkıda Bulunma

Katkılarınızı bekliyoruz! Lütfen:

1. Bu depoyu forklayın
2. Değişiklikleriniz için yeni bir dal oluşturun
3. Değişikliklerinizi bu dala pushlayın
4. Bir pull request oluşturun

---

Geliştirici: Halil Sak

Son Güncelleme: 26 Şubat 2025
