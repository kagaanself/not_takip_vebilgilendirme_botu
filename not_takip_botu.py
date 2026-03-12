import os
import time
import sqlite3
import logging
import requests
from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.common.by import By

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.FileHandler("bot_log.txt"), logging.StreamHandler()]
)

class UniversityBot:
    def __init__(self):
        """Botun temel ayarlarını ve veritabanını hazırlar."""
        self.student_no = os.getenv("STUDENT_NO")
        self.password = os.getenv("PASSWORD")
        self.tg_token = os.getenv("TELEGRAM_TOKEN")
        self.tg_chat_id = os.getenv("TELEGRAM_CHAT_ID")
        self.db_name = "notlar.db"
        
       
        self.driver: WebDriver = webdriver.Chrome()
        self._setup_db()
        logging.info("Sistem hazırlandı. Veritabanı bağlantısı kuruldu.")

    def _setup_db(self):
        """Notların saklanacağı veritabanı tablosunu oluşturur."""
        with sqlite3.connect(self.db_name) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS ogrenci_notlari (
                    ders_adi TEXT PRIMARY KEY,
                    vize TEXT,
                    final TEXT,
                    harf_notu TEXT
                )
            """)

    def send_notification(self, message):
        """Telegram üzerinden kullanıcıya mesaj gönderir."""
        try:
            url = f"https://api.telegram.org/bot{self.tg_token}/sendMessage"
            requests.get(url, params={"chat_id": self.tg_chat_id, "text": message})
        except Exception as e:
            logging.error(f"Telegram mesajı gönderilemedi: {e}")

    def login(self):
        """Üniversite otomasyonuna giriş yapar."""
        try:
            self.driver.get("https://obsogrenci.ktun.edu.tr/")
            time.sleep(2) 

      
            self.driver.find_element(By.XPATH, "/html/body/div[1]/div/div/div/form/div[1]/div/input").send_keys(self.student_no)
            self.driver.find_element(By.XPATH, "/html/body/div[1]/div/div/div/form/div[2]/div/input").send_keys(self.password)
            
            print("\n🚨 LÜTFEN TARAYICIYA GİDİN VE GÜVENLİK KODUNU GİRİN 🚨")
            captcha = input("Güvenlik kodunu yazıp botu devam ettirmek için ENTER'a basın: ")
            
            
            self.driver.find_element(By.XPATH, "/html/body/div[1]/div/div/div/form/div[3]/center/table/tbody/tr[2]/td/input").send_keys(captcha)
            self.driver.find_element(By.XPATH, "/html/body/div[1]/div/div/div/form/div[4]/div/input").click()
            self.driver.find_element(By.XPATH, "/html/body/div[1]/div/div/div/form/div[5]/div/input").click()
            self.driver.find_element(By.XPATH, "/html/body/div[1]/div/div/div/form/div[6]/button").click()
            
            time.sleep(3)
            logging.info("Sisteme başarılı bir şekilde giriş yapıldı.")
            self.send_notification("🎓 KTÜN Otomasyonuna giriş yapıldı. Nöbet başladı!")
            
        except Exception as e:
            logging.error(f"Giriş sırasında bir hata oluştu: {e}")

    def check_grades(self):
        """Not durum sayfasını tarar ve değişiklikleri raporlar."""
        try:
            self.driver.get("https://obsogrenci.ktun.edu.tr/Ogrenci/NotDurumu")
            time.sleep(4) 
            
            tablolar = self.driver.find_elements(By.TAG_NAME, "tbody")
            
            with sqlite3.connect(self.db_name) as conn:
                cursor = conn.cursor()
                for tablo in tablolar:
                    satirlar = tablo.find_elements(By.TAG_NAME, "tr")
                    for satir in satirlar:
                        hucreler = satir.find_elements(By.TAG_NAME, "td")
                        if len(hucreler) < 7: continue 

                        ders = hucreler[2].text.strip()
                        sinav_verisi = hucreler[4].text.split()
                        vize = sinav_verisi[1] if "Vize" in sinav_verisi else "-"
                        final = sinav_verisi[3] if "Final" in sinav_verisi else "-"
                        harf = hucreler[6].text.strip()

                        cursor.execute("SELECT vize, final, harf_notu FROM ogrenci_notlari WHERE ders_adi = ?", (ders,))
                        kayit = cursor.fetchone()

                        if not kayit:
                            cursor.execute("INSERT INTO ogrenci_notlari VALUES (?,?,?,?)", (ders, vize, final, harf))
                            if vize != "-" or final != "-":
                                self.send_notification(f"🚨 YENİ NOT GİRİLDİ!\n📚 Ders: {ders}\n📝 Vize: {vize}\n🎯 Final: {final}")
                        else:
                            if (vize, final, harf) != kayit:
                                self.send_notification(f"🔄 NOT GÜNCELLEMESİ!\n📚 Ders: {ders}\n📝 Yeni Vize: {vize}\n🎯 Yeni Final: {final}\n🏆 Harf: {harf}")
                                cursor.execute("UPDATE ogrenci_notlari SET vize=?, final=?, harf_notu=? WHERE ders_adi=?", (vize, final, harf, ders))
                
                conn.commit()

            self.send_notification("✅ Not denetimi tamamlandı, her şey güncel!") 
            logging.info("Denetim bitti, özet mesajı gönderildi.")

        except Exception as e:
            logging.error(f"Notları çekerken bir hata oluştu: {e}")

    def start(self, interval=30):
        """Botun ana çalışma döngüsü."""
        self.login()
        while True:
            self.check_grades()
            logging.info(f"{interval} saniye sonra tekrar kontrol edilecek...")
            time.sleep(interval)

if __name__ == "__main__":
    bot = UniversityBot()
    bot.start()