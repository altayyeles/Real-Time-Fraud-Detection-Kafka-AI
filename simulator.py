import time
import json
import random
import uuid
from datetime import datetime
from faker import Faker
from kafka import KafkaProducer 

fake = Faker()

# Kafka Producer Ayarları 
# Veriyi JSON formatına çevirip byte olarak Kafka'ya gönderir
producer = KafkaProducer(
    bootstrap_servers=['localhost:9092'],
    value_serializer=lambda v: json.dumps(v).encode('utf-8')
)

def generate_transaction():
    is_fraud = random.random() < 0.05

    if is_fraud:
        amount = round(random.uniform(5000.0, 50000.0), 2)
        merchant = random.choice(["Jewelry", "Electronics", "Crypto Exchange"])
        ip_address = fake.ipv4(network=True) 
    else:
        amount = round(random.uniform(5.0, 500.0), 2)
        merchant = random.choice(["Coffee Shop", "Supermarket", "Gas Station", "Streaming Service", "Restaurant"])
        ip_address = "192.168.1." + str(random.randint(1, 255)) 

    transaction = {
        "transaction_id": str(uuid.uuid4()),
        "user_id": random.randint(1000, 1050),
        "card_number": fake.credit_card_number(card_type="visa"),
        "amount": amount,
        "currency": "TRY",
        "timestamp": datetime.now().isoformat(),
        "merchant_category": merchant,
        "ip_address": ip_address,
        "location": {"lat": float(fake.latitude()), "lon": float(fake.longitude())},
        "is_simulated_fraud": is_fraud 
    }
    return transaction

if __name__ == "__main__":
    print("🚀 Kafka Bağlantılı Finansal Veri Simülatörü Başlatıldı...")
    print("-" * 50)
    
    try:
        while True:
            tx_data = generate_transaction()
            
            # Veriyi terminale yazdırmak yerine Kafka'ya gönderiyoruz
            producer.send('transactions', tx_data)
            producer.flush() # Verinin anında gitmesini garantiler
            
            print(f"✅ İşlem Kafka'ya gönderildi: Tutarı {tx_data['amount']} TL olan {tx_data['merchant_category']} harcaması.")
            
            time.sleep(random.uniform(0.5, 1.5))
            
    except KeyboardInterrupt:
        print("\n🛑 Simülatör durduruldu.")
        producer.close()