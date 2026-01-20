import yfinance as yf
import pandas as pd
import os
from datetime import datetime

# --- ตั้งค่า Path ---
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, 'data')
OUTPUT_FILE = os.path.join(DATA_DIR, 'intermarket_analysis.csv')

def analyze_intermarket():
    print(f"\n🔗 Agent 002: กำลังเชื่อมโยงข้อมูลจักรวาลการเงิน (Inter-market)...")
    
    try:
        if not os.path.exists(DATA_DIR):
            os.makedirs(DATA_DIR)

        # 1. กำหนดเป้าหมาย (Tickers)
        tickers = {
            'Gold': 'GC=F',
            'Dollar_DXY': 'DX-Y.NYB',
            'US10Y_Bond': '^TNX',
            'Crude_Oil': 'CL=F',
            'Bitcoin': 'BTC-USD'
        }
        
        results = {}
        
        # 2. วนลูปดึงข้อมูล
        for name, symbol in tickers.items():
            print(f"   ...กำลังดึงข้อมูล {name} ({symbol})")
            try:
                t = yf.Ticker(symbol)
                hist = t.history(period="5d")
                
                if hist.empty:
                    print(f"      ⚠️ ไม่พบข้อมูล {name}")
                    results[name] = {'price': 0, 'change_pct': 0}
                    continue
                    
                current = hist['Close'].iloc[-1]
                prev = hist['Close'].iloc[-2]
                change_pct = ((current - prev) / prev) * 100
                
                results[name] = {
                    'price': current,
                    'change_pct': change_pct
                }
            except Exception as e:
                print(f"      ❌ Error {name}: {e}")
                results[name] = {'price': 0, 'change_pct': 0}

        # 3. ตรวจสอบว่ามีข้อมูลทองคำไหม
        if 'Gold' not in results or results['Gold']['price'] == 0:
            print("❌ ไม่สามารถดึงราคาทองคำได้ จบการทำงาน")
            return

        # 4. วิเคราะห์ความสัมพันธ์
        print("\n🧠 วิเคราะห์ความสัมพันธ์ต่อทองคำ:")
        gold_chg = results['Gold']['change_pct']
        dxy_chg = results['Dollar_DXY']['change_pct']
        yield_chg = results['US10Y_Bond']['change_pct']
        
        # กฎ DXY
        if (dxy_chg > 0 and gold_chg > 0) or (dxy_chg < 0 and gold_chg < 0):
            dxy_status = "⚠️ ผิดปกติ (วิ่งทางเดียวกัน)"
        else:
            dxy_status = "ปกติ (สวนทางกัน)"

        # กฎ Yield
        if (yield_chg > 0 and gold_chg > 0):
            yield_status = "⚠️ ผิดปกติ (ยีลด์พุ่งแต่ทองไม่ลง)"
        else:
            yield_status = "ปกติ"

        print(f"   1. Gold vs DXY:   {dxy_status}")
        print(f"   2. Gold vs Yield: {yield_status}")

        # 5. เตรียมข้อมูลสำหรับบันทึก (จุดที่ Error คราวที่แล้ว)
        data_row = {
            "Date": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "Gold_Price": results['Gold']['price'],
            "Gold_Chg": results['Gold']['change_pct'],
            "DXY_Price": results['Dollar_DXY']['price'],
            "DXY_Chg": results['Dollar_DXY']['change_pct'],
            "Yield_Price": results['US10Y_Bond']['price'],
            "Yield_Chg": results['US10Y_Bond']['change_pct'],
            "Oil_Price": results['Crude_Oil']['price'],
            "BTC_Price": results['Bitcoin']['price'],
            "DXY_Correlation": dxy_status,
            "Yield_Correlation": yield_status
        }
        
        # สร้าง List ของ Dictionary
        data_list = [data_row]
        
        # บันทึกเป็น CSV
        df = pd.DataFrame(data_list)
        df.to_csv(OUTPUT_FILE, index=False)
        print("-" * 50)
        print(f"✅ บันทึกข้อมูลเรียบร้อยที่: {OUTPUT_FILE}")

    except Exception as e:
        print(f"❌ Critical Error: {e}")

if __name__ == "__main__":
    analyze_intermarket()