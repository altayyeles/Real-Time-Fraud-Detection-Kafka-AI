import json
import numpy as np
from kafka import KafkaConsumer
from sklearn.ensemble import IsolationForest

print("⚙️ Fraud Engine (Yapay Zeka Tüketicisi) Başlatılıyor...")

# 1. KAFKA TÜKETİCİSİ (CONSUMER) AYARLARI
# 'transactions' kanalını dinliyoruz. Gelen byte verisini tekrar JSON'a çeviriyoruz.
consumer = KafkaConsumer(
    'transactions',
    bootstrap_servers=['localhost:9092'],
    auto_offset_reset='earliest', # Sadece yeni gelen işlemleri oku
    value_deserializer=lambda m: json.loads(m.decode('utf-8'))
)

# 2. MAKİNE ÖĞRENMESİ MODELİ (ANOMALİ TESPİTİ)
# İleride buraya: model = joblib.load('gercek_model.pkl') gelecek. 
# Şimdilik sistemi ayağa kaldırmak için anında çalışan basit bir IsolationForest kuruyoruz.
ml_model = IsolationForest(contamination=0.05, random_state=42)

# Modeli kandırmamak için çok basit bir "normal ve anormal" veri setiyle hızlıca eğitiyoruz (Isındırma)
dummy_training_data = np.array([[10], [50], [150], [200], [5000], [15000], [25000]])
ml_model.fit(dummy_training_data)


def rule_based_engine(transaction):
    """
    Kural Tabanlı Motor: Bankaların ilk savunma hattı. 
    Basit ve kesin kurallara göre çok hızlı ret verir.
    """
    amount = transaction['amount']
    merchant = transaction['merchant_category']
    
    # Kural 1: Gece yarısı kuyumcu veya kripto harcaması yüksek tutarlıysa direkt şüpheli!
    if amount > 10000 and merchant in ["Jewelry", "Crypto Exchange"]:
        return True, "Kural İhlali: Yüksek Riskli İşyeri ve Tutar"
    
    return False, "Temiz"

def ml_engine(transaction):
    """
    Makine Öğrenmesi Motoru: Kurallardan kaçan karmaşık anomalileri bulur.
    """
    # Gerçek senaryoda modele lokasyon, saat, yaş gibi tüm özellikleri (features) veririz.
    # Şimdilik sadece tutar üzerinden anomali arıyoruz.
    features = np.array([[transaction['amount']]])
    
    # 1: Normal, -1: Anomali (Fraud)
    prediction = ml_model.predict(features)
    
    if prediction[0] == -1:
        return True, f"ML Anomali Tespiti (Tutar: {transaction['amount']} TL olağandışı)"
    
    return False, "Temiz"


# 3. GERÇEK ZAMANLI VERİ İŞLEME DÖNGÜSÜ
print("📡 Kafka'dan veri bekleniyor... (Durdurmak için CTRL+C)")
print("-" * 60)

for message in consumer:
    tx = message.value
    tx_id = tx['transaction_id'][:8] # Ekrana sığsın diye ID'yi kısalttık
    is_simulated_fraud = tx['is_simulated_fraud'] # Simülatörün gizlice koyduğu etiket
    
    # Adım A: Önce kural motoruna sok
    is_fraud_rule, reason_rule = rule_based_engine(tx)
    
    # Adım B: Sonra ML motoruna sok
    is_fraud_ml, reason_ml = ml_engine(tx)
    
    # Karar Mekanizması: Herhangi biri Fraud derse işlemi durdur!
    if is_fraud_rule or is_fraud_ml:
        reason = reason_rule if is_fraud_rule else reason_ml
        
        # Eğer simülatör de bunu fraud olarak üretmişse, modelimiz doğru yakalamış demektir!
        success_icon = "🎯" if is_simulated_fraud else "⚠️"
        
        print(f"🚨 {success_icon} BLOKE EDİLDİ! | ID: {tx_id} | Sebep: {reason}")
    else:
        # Eğer gizli etiket fraud olduğu halde temiz dediysek, modelimiz kaçırmış demektir.
        if is_simulated_fraud:
            print(f"❌ KAÇIRILDI! | ID: {tx_id} | Gerçekte Fraud ama sistem temiz dedi.")
        else:
            print(f"✅ ONAYLANDI  | ID: {tx_id} | Tutar: {tx['amount']} TL")