import pandas as pd
import random
import joblib
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report

print("🧠 Gerçekçi Veri üretimi ve Model Eğitimi başlatılıyor...")

data = []
merchants = ["Coffee Shop", "Supermarket", "Gas Station", "Streaming Service", "Restaurant", "Jewelry", "Electronics", "Crypto Exchange"]
merchant_map = {m: i for i, m in enumerate(merchants)}

for _ in range(20000): 
    is_fraud = random.random() < 0.05 
    
    if is_fraud:
        # %10 ihtimalle dolandırıcı "küçük meblağ" ile test yapıyor (ZORLUK SEVİYESİ ARTTI)
        if random.random() < 0.10:
            amount = round(random.uniform(5.0, 50.0), 2)
            merchant = random.choice(["Coffee Shop", "Supermarket"])
        else:
            amount = round(random.uniform(5000.0, 50000.0), 2)
            merchant = random.choice(["Jewelry", "Electronics", "Crypto Exchange"])
    else:
        # %5 ihtimalle normal müşteri "pahalı bir şey" alıyor (ZORLUK SEVİYESİ ARTTI)
        if random.random() < 0.05:
            amount = round(random.uniform(5000.0, 25000.0), 2)
            merchant = random.choice(["Jewelry", "Electronics"])
        else:
            amount = round(random.uniform(5.0, 500.0), 2)
            merchant = random.choice(["Coffee Shop", "Supermarket", "Gas Station", "Streaming Service", "Restaurant"])
            
    data.append({
        "amount": amount,
        "merchant_code": merchant_map[merchant],
        "is_fraud": 1 if is_fraud else 0
    })

df = pd.DataFrame(data)

X = df[['amount', 'merchant_code']]
y = df['is_fraud']

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)

model = RandomForestClassifier(n_estimators=100, class_weight='balanced', random_state=42)
model.fit(X_train, y_train)

y_pred = model.predict(X_test)
print("\n📊 Model Test Raporu (Gerçekçi Senaryo):")
print(classification_report(y_test, y_pred, target_names=['Temiz (0)', 'Fraud (1)']))

joblib.dump(model, 'rf_fraud_model.pkl')
joblib.dump(merchant_map, 'merchant_map.pkl') 

print("\n💾 Model 'rf_fraud_model.pkl' olarak kaydedildi!")