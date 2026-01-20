import yfinance as yf
import pandas as pd
import os
from datetime import datetime

# --- ตั้งค่า Path ให้ตรงกับเพื่อนๆ ---
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) # ถอยออกไป 1 ชั้นจาก agents
DATA_DIR = os.path.join(BASE_DIR, 'data')
OUTPUT_FILE = os.path.join(DATA_DIR, 'spdr_gold_flows.csv')

def fetch_and_save_spdr():
    print(f"\n📦 Agent 005: กำลังดึงข้อมูลกองทุน SPDR (GLD)...")
    
    try:
        # 1. สร้างโฟลเดอร์ data ถ้ายังไม่มี
        if not os.path.exists(DATA_DIR):
            os.makedirs(DATA_DIR)

        # 2. ดึงข้อมูลจาก Yahoo Finance
        ticker = yf.Ticker("GLD")
        hist = ticker.history(period="5d")
        
        if hist.empty:
            print("❌ ไม่พบข้อมูล GLD (เช็คอินเทอร์เน็ต)")
            return

        # 3. คำนวณค่า
        latest = hist.iloc[-1]
        prev = hist.iloc[-2]
        
        price = latest['Close']
        change = price - prev['Close']
        volume = latest['Volume']
        
        # วิเคราะห์ง่ายๆ
        status = "🟢 BUY (เก็บของ)" if change > 0 else "🔴 SELL (เทขาย)"
        
        # 4. บันทึกลงไฟล์
        data = [{
            "Date": datetime.now().strftime("%Y-%m-%d"),
            "Price": round(price, 2),
            "Change": round(change, 2),
            "Volume": int(volume),
            "Status": status
        }]
        
        df = pd.DataFrame(data)
        df.to_csv(OUTPUT_FILE, index=False) # เขียนทับไฟล์เก่าไปเลยเพื่อความสดใหม่
        
        print(f"✅ บันทึกข้อมูลสำเร็จที่: {OUTPUT_FILE}")
        print(f"📊 ราคา: ${price:.2f} | สถานะ: {status}")

    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    fetch_and_save_spdr()