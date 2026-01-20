import yfinance as yf
import pandas as pd
import os
from datetime import datetime

# --- ตั้งค่า Path ---
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, 'data')
# ชื่อไฟล์ต้องตรงกับที่ War Room รออ่าน
OUTPUT_FILE = os.path.join(DATA_DIR, 'market_price_data.csv') 

def analyze_market_price():
    print(f"\n📊 Agent 002 (Financial): กำลังเล็งเป้ากราฟเทคนิค...")
    
    try:
        if not os.path.exists(DATA_DIR):
            os.makedirs(DATA_DIR)

        # 1. ดึงข้อมูลทองคำ (Gold Futures)
        # ใช้ GC=F (Gold Futures) หรือ GLD ก็ได้ แต่ GC=F จะใกล้เคียง Spot มากกว่า
        ticker = yf.Ticker("GC=F")
        hist = ticker.history(period="60d") # ดึงย้อนหลัง 60 วันเพื่อให้ชัวร์เรื่องเส้น MA
        
        if hist.empty:
            print("❌ ไม่พบข้อมูลราคา (เช็คเน็ต)")
            return

        # 2. คำนวณตัวเลขทางเทคนิค
        current_price = hist['Close'].iloc[-1]
        prev_price = hist['Close'].iloc[-2]
        change = current_price - prev_price
        pct_change = (change / prev_price) * 100
        
        # Moving Averages (เส้นค่าเฉลี่ย)
        ma10 = hist['Close'].tail(10).mean() # เส้นระยะสั้น (10 วัน)
        ma50 = hist['Close'].tail(50).mean() # เส้นระยะกลาง (50 วัน)

        # 3. วิเคราะห์เทรนด์ (Sniper Logic)
        trend = "SIDEWAY"
        signal = "WAIT"
        
        if current_price > ma10 and current_price > ma50:
            trend = "UPTREND (ขาขึ้นแข็งแกร่ง)"
            signal = "BUY"
        elif current_price < ma10 and current_price < ma50:
            trend = "DOWNTREND (ขาลงชัดเจน)"
            signal = "SELL"
        elif current_price > ma10:
            trend = "RECOVERY (ฟื้นตัวระยะสั้น)"
            signal = "WAIT/BUY"
        else:
            trend = "CORRECTION (ย่อตัวระยะสั้น)"
            signal = "WAIT"

        # 4. แสดงผล
        print(f"   💰 ราคาทอง (Spot): ${current_price:.2f}")
        print(f"   📈 เส้นค่าเฉลี่ย: MA10=${ma10:.1f} | MA50=${ma50:.1f}")
        print(f"   🚩 สถานะกราฟ: {trend}")

        # 5. บันทึกข้อมูลส่งต่อให้ War Room
        data = [{
            "Date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "Asset": "Gold",
            "Price": round(current_price, 2),
            "Change": round(change, 2),
            "Pct_Change": round(pct_change, 2),
            "Trend": trend,
            "Signal": signal
        }]
        
        df = pd.DataFrame(data)
        df.to_csv(OUTPUT_FILE, index=False)
        print(f"✅ ส่งข้อมูลเข้าศูนย์บัญชาการเรียบร้อยที่: {OUTPUT_FILE}")

    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    analyze_market_price()