# 🛡️ Gerçek Zamanlı AI Destekli Finansal Sahtekarlık Tespit Sistemi

Bu proje, yüksek hacimli finansal işlem verilerini gerçek zamanlı olarak işleyen, kurallara dayalı kontroller ve eğitilmiş makine öğrenmesi (Random Forest) modelleri kullanarak sahtekarlık (fraud) girişimlerini milisaniyeler içinde tespit eden uçtan uca (end-to-end) bir sistemdir.

Sistem, modern bankacılık mimarilerine uygun olarak Olay Güdümlü (Event-Driven) bir yapıda tasarlanmıştır ve mikroservis mimarisi prensiplerini kullanır.

## 🚀 Projenin Amacı ve Temel Özellikleri

Geleneksel, sonradan analiz yapan sistemlerin aksine, bu proje akan veriyi (streaming data) anlık olarak analiz ederek şüpheli işlemleri gerçekleştiği anda bloke etmeyi hedefler.

* **Gerçek Zamanlı Veri Akışı:** Apache Kafka ile saniyede yüzlerce işlemi havada yakalama ve işleme.
* **Hibrit Tespit Motoru:**
    * **Kural Motoru:** Belirli limitler ve sektörler için anında ret kararı (Örn: Gece yarısı yüksek tutarlı kuyumcu harcaması).
    * **Yapay Zeka (AI) Modeli:** Kural motorundan kaçan karmaşık ve sinsi dolandırıcılık kalıplarını yakalayan, dengesiz (imbalanced) verilerle eğitilmiş **Random Forest** modeli.
* **Canlı Dashboard:** FastAPI ve WebSockets kullanılarak geliştirilmiş, işlemlerin ve risk skorlarının anlık olarak aktığı modern bir arayüz.
* **Kalıcı Veri Depolama:** İşlenen tüm verilerin ve alınan kararların SQLite veritabanına loglanması.
* **Dockerize Edilmiş Altyapı:** Kafka ve Zookeeper servislerinin konteynerler ile kolayca ayağa kaldırılması.

## 🏗️ Sistem Mimarisi

Proje, veri üretiminden görselleştirmeye kadar 5 ana aşamadan oluşur. Aşağıdaki diyagram sistemin veri akışını göstermektedir:

<img width="1024" height="559" alt="image" src="https://github.com/user-attachments/assets/eade5286-b6da-408e-881a-d4432bea5ce2" />



1.  **Veri Simülatörü (Producer):** Gerçekçi müşteri davranışlarını taklit eden ve araya gizli sahtekarlık senaryoları serpiştiren Python tabanlı veri üretici.
2.  **Mesaj Kuyruğu (Kafka Broker):** Simülatörden gelen yoğun veri trafiğini karşılayan ve sıraya sokan, Docker üzerinde çalışan Apache Kafka kümesi.
3.  **Backend ve AI Tüketicisi (Consumer):** FastAPI ile yazılmış, Kafka'yı dinleyen ana servis. Gelen her işlemi hem kural motoruna hem de `.pkl` olarak yüklenen Random Forest modeline sokar.
4.  **Veritabanı (Storage):** İşlem sonuçlarının kaydedildiği SQLite veritabanı.
5.  **Canlı Dashboard (Frontend):** WebSocket üzerinden backend'e bağlı olan, HTML/TailwindCSS ve Chart.js ile hazırlanmış gerçek zamanlı izleme ekranı.

## 📸 Ekran Görüntüleri

**Gerçek Zamanlı İzleme Paneli ve AI Risk Tespiti**
<img width="1909" height="848" alt="Ekran görüntüsü 2026-02-21 160003" src="https://github.com/user-attachments/assets/272c6238-ac1a-4792-83d3-8a239b3d9af3" />


## 🛠️ Kullanılan Teknolojiler (Tech Stack)

* **Backend & API:** Python, FastAPI, Uvicorn
* **Veri Akışı & Mesajlaşma:** Apache Kafka, Zookeeper (Docker üzerinde)
* **Yapay Zeka & Veri Bilimi:** scikit-learn (Random Forest), pandas, joblib
* **Veritabanı:** SQLite
* **Frontend:** HTML5, Tailwind CSS, Chart.js, WebSockets
* **Araçlar:** Docker, Docker Compose

## ⚙️ Kurulum ve Çalıştırma

Projeyi yerel makinenizde çalıştırmak için aşağıdaki adımları izleyin.

### Ön Gereksinimler
* Python 3.10+
* Docker Desktop (Çalışır durumda olmalı)

### Adım 1: Repoyu Klonlayın ve Bağımlılıkları Yükleyin
```bash
git clone [https://github.com/KULLANICI_ADINIZ/REPO_ADINIZ.git](https://github.com/KULLANICI_ADINIZ/REPO_ADINIZ.git)
cd REPO_ADINIZ
pip install -r requirements.txt
```

Adım 2: Kafka Altyapısını Ayağa Kaldırın
Docker Desktop'ın çalıştığından emin olun ve aşağıdaki komutu çalıştırın. Bu işlem Kafka ve Zookeeper'ı indirecek ve başlatacaktır (İlk çalıştırmada biraz zaman alabilir).

```
docker-compose up -d
```

Adım 3: AI Modelini Eğitin
Sistemin kullanacağı yapay zeka modelini eğitmek ve .pkl dosyası olarak kaydetmek için eğitim scriptini çalıştırın.

```
python train_model.py
```

Adım 4: Sistemi Başlatın (İki Ayrı Terminalde)
Terminal 1: Veri Simülatörünü Başlat
Bu script, Kafka'ya sürekli olarak sahte işlem verisi göndermeye başlayacaktır.

```
python simulator.py
```
Terminal 2: Backend ve Dashboard Sunucusunu Başlat
Bu komut FastAPI sunucusunu başlatacak, Kafka'yı dinlemeye geçecek ve Web arayüzünü sunacaktır.

```
python dashboard.py
```

Adım 5: Dashboard'u İzleyin
Tarayıcınızdan http://localhost:8000 adresine gidin ve akan verileri izlemeye başlayın!

📁 Proje Yapısı
```
docker-compose.yml: Kafka ve Zookeeper servislerinin konfigürasyonu.

simulator.py: Kafka'ya veri üreten simülatör scripti.

train_model.py: Sentetik veri üretip Random Forest modelini eğiten ve kaydeden script.

dashboard.py: FastAPI backend, WebSocket sunucusu, AI entegrasyonu ve veritabanı kayıt işlemlerinin yapıldığı ana uygulama dosyası.

rf_fraud_model.pkl & merchant_map.pkl: Eğitilmiş AI modeli ve kategori sözlüğü dosyaları.

fraud_data.db: İşlem geçmişinin tutulduğu SQLite veritabanı dosyası (ilk çalıştırmada otomatik oluşur).

Bu proje, gerçek zamanlı veri işleme ve makine öğrenmesi entegrasyonu yeteneklerini sergilemek amacıyla geliştirilmiştir.
```
