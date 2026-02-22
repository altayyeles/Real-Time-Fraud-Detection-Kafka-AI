import json
import asyncio
import random
import sqlite3
import pandas as pd
import joblib
from datetime import datetime
from fastapi import FastAPI, WebSocket
from fastapi.responses import HTMLResponse
from kafka import KafkaConsumer
import uvicorn

print("🚀 FastAPI Dashboard ve GERÇEK Yapay Zeka Hazırlanıyor...")

app = FastAPI()

# --- 1. VERİTABANI (SQLITE) KURULUMU ---
conn = sqlite3.connect('fraud_data.db', check_same_thread=False)
cursor = conn.cursor()
cursor.execute('''
    CREATE TABLE IF NOT EXISTS transactions (
        id TEXT PRIMARY KEY,
        amount REAL,
        merchant TEXT,
        status TEXT,
        reason TEXT,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
    )
''')
conn.commit()

# --- 2. GERÇEK MAKİNE ÖĞRENMESİ MODELİNİ YÜKLE ---
print("🧠 Eğitilmiş Random Forest modeli yükleniyor...")
try:
    rf_model = joblib.load('rf_fraud_model.pkl')
    merchant_map = joblib.load('merchant_map.pkl')
    print("✅ Model ve Sözlük başarıyla yüklendi!")
except Exception as e:
    print(f"❌ Model yüklenemedi! Önce train_model.py'yi çalıştırdığından emin ol. Hata: {e}")

def evaluate_transaction(tx):
    amount = tx['amount']
    merchant = tx['merchant_category']
    
    # 1. Hızlı Kural Motoru (İlk Savunma Hattı)
    if amount > 10000 and merchant in ["Jewelry", "Crypto Exchange"]:
        return "BLOKE", "Kural: Çok Yüksek Riskli İşlem"
    
    # 2. Random Forest Makine Öğrenmesi Modeli
    # Gelen kategoriyi sayıya çevir, listede yoksa güvenli liman olarak 0 kabul et
    merchant_code = merchant_map.get(merchant, 0) 
    
    # Modeli beslemek için veriyi DataFrame'e çeviriyoruz
    features = pd.DataFrame([[amount, merchant_code]], columns=['amount', 'merchant_code'])
    
    prediction = rf_model.predict(features)
    
    if prediction[0] == 1: # 1 ise Fraud demektir
        # İşlemin % kaç oranında şüpheli olduğunu hesaplatıyoruz
        fraud_prob = rf_model.predict_proba(features)[0][1] * 100
        return "BLOKE", f"🤖 AI Tespit Etti (Risk: %{fraud_prob:.1f})"
        
    return "ONAYLANDI", "Temiz"

# --- 3. ÖNYÜZ (HTML + CSS + CHART.JS) ---
# (Burası bir önceki kodla tamamen aynı, vitrinimiz kusursuzdu zaten)
html_content = """
<!DOCTYPE html>
<html lang="tr">
<head>
    <meta charset="UTF-8">
    <title>AI Fraud Dashboard</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        .no-scrollbar::-webkit-scrollbar { display: none; }
        .no-scrollbar { -ms-overflow-style: none; scrollbar-width: none; }
    </style>
</head>
<body class="bg-gray-900 text-white h-screen p-6 flex flex-col font-sans">
    
    <header class="mb-4 border-b border-gray-700 pb-4 flex justify-between items-center">
        <h1 class="text-3xl font-bold text-blue-400">🛡️ Gerçek Zamanlı Fraud İzleme Paneli</h1>
        <div class="flex items-center gap-2">
            <span class="relative flex h-3 w-3">
              <span class="animate-ping absolute inline-flex h-full w-full rounded-full bg-green-400 opacity-75"></span>
              <span class="relative inline-flex rounded-full h-3 w-3 bg-green-500"></span>
            </span>
            <span class="text-sm text-gray-400">Random Forest AI Aktif</span>
        </div>
    </header>

    <div class="bg-gray-800 rounded-xl border border-gray-700 p-4 mb-6 flex items-center justify-between shadow-lg h-40">
        <div class="w-1/3 flex justify-center h-full">
            <canvas id="statsChart"></canvas>
        </div>
        <div class="w-1/3 text-center">
            <p class="text-gray-400 text-lg">Toplam İşlenen Veri</p>
            <p id="total-tx" class="text-5xl font-bold text-blue-500 mt-2">0</p>
        </div>
        <div class="w-1/3 text-center">
            <p class="text-gray-400 text-lg">Yakalanan Sahtekarlık</p>
            <p id="blocked-tx" class="text-5xl font-bold text-red-500 mt-2">0</p>
        </div>
    </div>

    <div class="grid grid-cols-2 gap-6 flex-1 overflow-hidden">
        <div class="flex flex-col h-full bg-gray-800 rounded-xl border border-gray-700 p-4 shadow-lg">
            <h2 class="text-xl font-semibold text-green-400 mb-4 sticky top-0 bg-gray-800 pb-2 z-10 border-b border-gray-700">✅ Onaylanan İşlemler</h2>
            <ul id="approved-list" class="space-y-3 overflow-y-auto no-scrollbar pb-4 flex-1"></ul>
        </div>

        <div class="flex flex-col h-full bg-gray-800 rounded-xl border border-red-900/50 p-4 shadow-[0_0_15px_rgba(220,38,38,0.1)]">
            <h2 class="text-xl font-semibold text-red-400 mb-4 sticky top-0 bg-gray-800 pb-2 z-10 border-b border-gray-700">🚨 Bloke Edilen İşlemler</h2>
            <ul id="blocked-list" class="space-y-3 overflow-y-auto no-scrollbar pb-4 flex-1"></ul>
        </div>
    </div>

    <script>
        let approvedCount = 0;
        let blockedCount = 0;
        const ctx = document.getElementById('statsChart').getContext('2d');
        const statsChart = new Chart(ctx, {
            type: 'doughnut',
            data: {
                labels: ['Temiz', 'Fraud'],
                datasets: [{
                    data: [0, 0],
                    backgroundColor: ['#10B981', '#EF4444'],
                    borderWidth: 0,
                    hoverOffset: 4
                }]
            },
            options: { 
                responsive: true, 
                maintainAspectRatio: false, 
                plugins: { legend: { position: 'right', labels: {color: '#9CA3AF', font: {size: 14}} } },
                cutout: '70%'
            }
        });

        var ws = new WebSocket("ws://localhost:8000/ws");
        
        ws.onmessage = function(event) {
            var data = JSON.parse(event.data);
            
            var li = document.createElement("li");
            li.className = "p-3 rounded-lg bg-gray-700/50 border border-gray-600 shadow-sm animate-pulse text-sm transition-all duration-500";
            setTimeout(() => li.classList.remove("animate-pulse"), 500);
            
            var time = new Date().toLocaleTimeString('tr-TR');
            
            if(data.status === "BLOKE") {
                blockedCount++;
                document.getElementById('blocked-tx').innerText = blockedCount;
                
                li.classList.add("border-l-4", "border-red-500", "bg-red-900/20");
                li.innerHTML = `
                    <div class="flex justify-between text-gray-400 text-xs mb-1"><span>ID: ${data.id}</span><span>${time}</span></div>
                    <div class="font-semibold text-lg mb-1">${data.amount} TL <span class="text-sm font-normal text-gray-300">(${data.merchant})</span></div>
                    <div class="text-red-400 text-xs font-bold">${data.reason}</div>
                `;
                var list = document.getElementById('blocked-list');
                list.insertBefore(li, list.firstChild);
                if(list.childElementCount > 40) list.removeChild(list.lastChild);
            } else {
                approvedCount++;
                
                li.classList.add("border-l-4", "border-green-500");
                li.innerHTML = `
                    <div class="flex justify-between text-gray-400 text-xs mb-1"><span>ID: ${data.id}</span><span>${time}</span></div>
                    <div class="font-semibold text-lg text-gray-200">${data.amount} TL <span class="text-sm font-normal text-gray-400">(${data.merchant})</span></div>
                `;
                var list = document.getElementById('approved-list');
                list.insertBefore(li, list.firstChild);
                if(list.childElementCount > 40) list.removeChild(list.lastChild);
            }

            document.getElementById('total-tx').innerText = approvedCount + blockedCount;
            statsChart.data.datasets[0].data = [approvedCount, blockedCount];
            statsChart.update();
        };
    </script>
</body>
</html>
"""

@app.get("/")
async def get():
    return HTMLResponse(html_content)

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    
    consumer = KafkaConsumer(
        'transactions',
        bootstrap_servers=['localhost:9092'],
        auto_offset_reset='latest',
        group_id='dashboard-group-' + str(random.randint(1, 10000)),
        value_deserializer=lambda m: json.loads(m.decode('utf-8'))
    )
    
    try:
        while True:
            records = consumer.poll(timeout_ms=100) 
            
            for topic_partition, messages in records.items():
                for message in messages:
                    tx = message.value
                    status, reason = evaluate_transaction(tx)
                    
                    cursor.execute(
                        "INSERT INTO transactions (id, amount, merchant, status, reason) VALUES (?, ?, ?, ?, ?)",
                        (tx['transaction_id'], tx['amount'], tx['merchant_category'], status, reason)
                    )
                    conn.commit()
                    
                    payload = {
                        "id": tx['transaction_id'][:8],
                        "amount": tx['amount'],
                        "merchant": tx['merchant_category'],
                        "status": status,
                        "reason": reason
                    }
                    await websocket.send_json(payload)
            
            await asyncio.sleep(0.01) 
            
    except Exception as e:
        print(f"Bağlantı koptu: {e}")
    finally:
        consumer.close()

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
    print("🚀 Dashboard sunucusu başlatıldı! http://localhost:8000 adresine gidin.")