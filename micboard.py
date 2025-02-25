#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
MicBoard: Sesli Klavye Uygulaması
Bu uygulama kullanıcının mikrofonundan sesi dinler, 
metne dönüştürür ve klavye girişi olarak simüle eder.
"""

import os
import sys
import time
import threading
import queue
from io import BytesIO
import logging
from typing import Optional

# PyQt5 kütüphaneleri - Sistem tepsisi için
from PyQt5.QtWidgets import QApplication, QSystemTrayIcon, QMenu, QAction
from PyQt5.QtGui import QIcon, QPixmap, QPainter, QColor
from PyQt5.QtCore import QObject, pyqtSignal, QByteArray, Qt

# Ses tanıma ve giriş kütüphaneleri
import speech_recognition as sr
import pyaudio
import wave

# Klavye simülasyonu
from pynput.keyboard import Controller as KeyboardController

# Loglama konfigürasyonu
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("MicBoard")


class AudioRecorder:
    """Mikrofon girişinden sürekli ses kayıt eden sınıf"""
    
    def __init__(self, audio_queue: queue.Queue):
        self.audio_queue = audio_queue
        self.is_recording = False
        self.p = pyaudio.PyAudio()
        self.stream = None
        self.chunk = 1024
        self.format = pyaudio.paInt16
        self.channels = 1
        self.rate = 44100  # Hz - 16000'den 44100'e yükseltildi, daha yüksek ses kalitesi için

    def start_recording(self):
        """Ses kaydını başlatır"""
        if self.is_recording:
            return
            
        self.is_recording = True
        self.stream = self.p.open(
            format=self.format,
            channels=self.channels,
            rate=self.rate,
            input=True,
            frames_per_buffer=self.chunk
        )
        
        logger.info("Ses kaydı başlatıldı")
        
        # Ayrı bir thread'de kayıt işlemini başlat
        threading.Thread(target=self._record_audio, daemon=True).start()
    
    def stop_recording(self):
        """Ses kaydını durdurur"""
        self.is_recording = False
        if self.stream:
            self.stream.stop_stream()
            self.stream.close()
            logger.info("Ses kaydı durduruldu")
    
    def _record_audio(self):
        """Ses kayıt işlemini sürekli olarak gerçekleştirir"""
        frames = []
        silence_threshold = 500  # Sessizlik eşiği - 300'den 500'e yükseltildi
        silent_chunks = 0
        max_silent_chunks = 20  # Yaklaşık 0.7 saniye sessizlik - 30'dan 20'ye düşürüldü

        while self.is_recording:
            try:
                data = self.stream.read(self.chunk, exception_on_overflow=False)
                frames.append(data)
                
                # Konuşma bittiğinde ses paketini işlem kuyruğuna ekle
                # Basit bir sessizlik tespiti
                if len(frames) > 5:  # En az birkaç paket topla
                    # Sessizliği algıla (çok basit yöntem)
                    is_silent = max(abs(int.from_bytes(data[i:i+2], byteorder='little', signed=True)) 
                                  for i in range(0, len(data), 2)) < silence_threshold
                    
                    if is_silent:
                        silent_chunks += 1
                    else:
                        silent_chunks = 0
                    
                    # Yeterince sessizlik varsa, biriken ses verilerini işle
                    if silent_chunks >= max_silent_chunks and len(frames) > 10:
                        audio_data = self._frames_to_audio_data(frames)
                        self.audio_queue.put(audio_data)
                        frames = []  # Çerçeveleri sıfırla
                        silent_chunks = 0
            except Exception as e:
                logger.error(f"Ses kaydı sırasında hata: {e}")
                break
    
    def _frames_to_audio_data(self, frames):
        """Ses çerçevelerini WAV formatına dönüştürür"""
        buffer = BytesIO()
        wf = wave.open(buffer, 'wb')
        wf.setnchannels(self.channels)
        wf.setsampwidth(self.p.get_sample_size(self.format))
        wf.setframerate(self.rate)
        wf.writeframes(b''.join(frames))
        wf.close()
        
        buffer.seek(0)
        return buffer.read()
    
    def __del__(self):
        """Temizlik işlemleri"""
        self.stop_recording()
        self.p.terminate()


class SpeechRecognizer:
    """Ses verilerini metne dönüştüren sınıf"""
    
    def __init__(self, audio_queue: queue.Queue, text_queue: queue.Queue):
        self.audio_queue = audio_queue
        self.text_queue = text_queue
        self.is_processing = False
        self.recognizer = sr.Recognizer()
        
        # Konuşma tanıma optimizasyonları
        self.recognizer.energy_threshold = 400  # 300'den 400'e yükseltildi - daha iyi konuşma tespiti
        self.recognizer.dynamic_energy_threshold = True
        self.recognizer.pause_threshold = 0.6  # 0.8'den 0.6'ya düşürüldü - daha hızlı yanıt
        self.recognizer.phrase_threshold = 0.3  # Yeni eklendi - kısa ifadeleri daha iyi tanıma
        self.recognizer.non_speaking_duration = 0.4  # Yeni eklendi - sessizlik tespiti iyileştirmesi
    
    def start_processing(self):
        """Ses işlemeyi başlatır"""
        if self.is_processing:
            return
            
        self.is_processing = True
        logger.info("Ses tanıma başlatıldı")
        
        # Ayrı bir thread'de işleme başlat
        threading.Thread(target=self._process_audio, daemon=True).start()
    
    def stop_processing(self):
        """Ses işlemeyi durdurur"""
        self.is_processing = False
        logger.info("Ses tanıma durduruldu")
    
    def _process_audio(self):
        """Ses verilerini işler ve metne dönüştürür"""
        while self.is_processing:
            try:
                # Kuyruktan ses verisi al
                if self.audio_queue.empty():
                    time.sleep(0.1)
                    continue
                
                audio_data = self.audio_queue.get()
                
                # Ses verisini speech_recognition formatına dönüştür
                with BytesIO(audio_data) as buffer:
                    with sr.AudioFile(buffer) as source:
                        audio = self.recognizer.record(source)
                
                # Konuşmayı metne dönüştür
                try:
                    # Google tanıma servisinde gelişmiş parametreler eklendi
                    text = self.recognizer.recognize_google(
                        audio, 
                        language="tr-TR",
                        show_all=False,  # En güvenilir sonucu al
                    )
                    if text:
                        logger.info(f"Tanınan metin: {text}")
                        
                        # Metin formatlama işlemi
                        formatted_text = self._format_text(text)
                        logger.info(f"Formatlanmış metin: {formatted_text}")
                        
                        self.text_queue.put(formatted_text)
                except sr.UnknownValueError:
                    logger.debug("Konuşma anlaşılamadı")
                except sr.RequestError as e:
                    logger.error(f"Google API hatası: {e}")
                
            except Exception as e:
                logger.error(f"Ses işleme sırasında hata: {e}")
                time.sleep(0.5)
    
    def _format_text(self, text: str) -> str:
        """Metni formatlar: küçük harfe çevirir, kelimelere ayırır ve boşluk ekler"""
        # Küçük harfe çevir
        text = text.lower()
        
        # Kelimelere ayır ve her kelime sonuna boşluk ekle
        words = text.split()
        
        # Kelimeleri boşluklarla birleştir (zaten yapılıyor ama netlik için)
        formatted_text = " ".join(words)
        
        return formatted_text


class KeyboardSimulator:
    """Metni klavye girişi olarak simüle eden sınıf"""
    
    def __init__(self, text_queue: queue.Queue):
        self.text_queue = text_queue
        self.is_typing = False
        self.keyboard = KeyboardController()
        self.typing_speed = 0.05  # Karakter başına yazma hızı (saniye)
    
    def start_typing(self):
        """Metin yazma işlemini başlatır"""
        if self.is_typing:
            return
            
        self.is_typing = True
        logger.info("Klavye simülasyonu başlatıldı")
        
        # Ayrı bir thread'de yazma işlemini başlat
        threading.Thread(target=self._type_text, daemon=True).start()
    
    def stop_typing(self):
        """Metin yazma işlemini durdurur"""
        self.is_typing = False
        logger.info("Klavye simülasyonu durduruldu")
    
    def _type_text(self):
        """Metni klavye tuşları olarak yazar"""
        while self.is_typing:
            try:
                # Kuyruktan metin al
                if self.text_queue.empty():
                    time.sleep(0.1)
                    continue
                
                text = self.text_queue.get()
                
                # Metni karakter karakter yaz
                for char in text:
                    self.keyboard.type(char)
                    time.sleep(self.typing_speed)  # Her karakter arasında belirtilen süre kadar bekle
                
                # Metinden sonra bir boşluk ekle
                self.keyboard.type(" ")
                
            except Exception as e:
                logger.error(f"Metin yazma sırasında hata: {e}")
                time.sleep(0.5)


class MicBoardApp(QObject):
    """Ana uygulama sınıfı"""
    
    statusChanged = pyqtSignal(bool)
    
    def __init__(self):
        super().__init__()
        
        # Kuyruklar
        self.audio_queue = queue.Queue()
        self.text_queue = queue.Queue()
        
        # Bileşenler
        self.recorder = AudioRecorder(self.audio_queue)
        self.recognizer = SpeechRecognizer(self.audio_queue, self.text_queue)
        self.keyboard = KeyboardSimulator(self.text_queue)
        
        # Uygulama durumu
        self.is_active = False
        
        # Sistem tepsisi simgesi
        self._setup_tray_icon()
        
        # Durum değişikliği sinyalini bağla
        self.statusChanged.connect(self._handle_status_change)
    
    def _setup_tray_icon(self):
        """Sistem tepsisi simgesini hazırlar"""
        # Uygulama
        self.app = QApplication(sys.argv)
        self.app.setQuitOnLastWindowClosed(False)
        
        # Simge oluştur (programatik olarak)
        self.active_icon = self._create_icon(True)
        self.passive_icon = self._create_icon(False)
        
        # Sistem tepsisi simgesi
        self.tray_icon = QSystemTrayIcon()
        self.tray_icon.setIcon(self.passive_icon)
        self.tray_icon.setToolTip("MicBoard - Sesli Klavye")
        
        # Tıklama olayları
        self.tray_icon.activated.connect(self._tray_icon_activated)
        
        # Simgeyi göster
        self.tray_icon.show()
    
    def _create_icon(self, is_active: bool) -> QIcon:
        """Programatik olarak simge oluşturur"""
        size = 128  # İkon boyutu 128x128 olarak değiştirildi
        pixmap = QPixmap(size, size)
        pixmap.fill(Qt.transparent)
        
        # Basit bir simge çiz
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Arka plan rengi - Aktif için yeşil, pasif için gri
        bg_color = QColor("#4CAF50") if is_active else QColor("#9E9E9E")
        
        # Daire çiz (tüm ikonu kaplayan basit bir daire)
        painter.setBrush(bg_color)
        painter.setPen(Qt.NoPen)
        painter.drawEllipse(4, 4, size-8, size-8)
        
        # Mikrofon ikonu (basit simge)
        painter.setBrush(QColor("white"))
        center_x = size // 2
        center_y = size // 2
        
        # Mikrofon gövdesi
        mic_width = size // 4
        mic_height = size // 3
        painter.drawRoundedRect(center_x - mic_width//2, center_y - mic_height//2, 
                               mic_width, mic_height, mic_width//4, mic_width//4)
        
        # Mikrofon ayağı
        stand_width = size // 12
        stand_height = size // 6
        painter.drawRect(center_x - stand_width//2, center_y + mic_height//2, 
                        stand_width, stand_height)
        
        # Mikrofon tabanı
        base_width = size // 3
        base_height = size // 16
        painter.drawRect(center_x - base_width//2, center_y + mic_height//2 + stand_height - base_height//2, 
                        base_width, base_height)
        
        painter.end()
        
        return QIcon(pixmap)
    
    def _tray_icon_activated(self, reason):
        """Sistem tepsisi simgesine tıklandığında çağrılır"""
        if reason == QSystemTrayIcon.Trigger:  # Sol tık
            self.toggle_active_state()
        elif reason == QSystemTrayIcon.Context:  # Sağ tık
            self.quit()  # Doğrudan kapat
    
    def toggle_active_state(self):
        """Aktif ve pasif durum arasında geçiş yapar"""
        self.is_active = not self.is_active
        self.statusChanged.emit(self.is_active)
    
    def _handle_status_change(self, is_active: bool):
        """Uygulama durumu değiştiğinde çağrılır"""
        if is_active:
            # Aktif moda geçiş
            self.tray_icon.setIcon(self.active_icon)
            self.recorder.start_recording()
            self.recognizer.start_processing()
            self.keyboard.start_typing()
            logger.info("MicBoard aktif.")
        else:
            # Pasif moda geçiş
            self.tray_icon.setIcon(self.passive_icon)
            self.recorder.stop_recording()
            self.recognizer.stop_processing()
            self.keyboard.stop_typing()
            logger.info("MicBoard pasif.")
    
    def run(self):
        """Uygulamayı çalıştırır"""
        # Qt olay döngüsünü başlat
        return self.app.exec_()
    
    def quit(self):
        """Uygulamayı kapatır"""
        logger.info("Uygulama kapatılıyor...")
        
        # Bileşenleri durdur
        self.recorder.stop_recording()
        self.recognizer.stop_processing()
        self.keyboard.stop_typing()
        
        # Uygulamadan çık
        self.app.quit()


if __name__ == "__main__":
    # Import here to avoid circular imports
    from PyQt5.QtGui import QPainter, QColor
    
    app = MicBoardApp()
    sys.exit(app.run())
