import pandas as pd
import os
import sys
from datetime import datetime

os.system('cls' if os.name == 'nt' else 'clear')

# --- Path ข้อมูล ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, 'data')

def load_data(filename):
    path = os.path.join(DATA_DIR, filename)
    if os.path.exists(path):
        try:
            return pd.read_csv(path)
        except:
            return None
    return None

def start_war_room():
    print("\n" + "═"*75)
    print("      🚀 GOLD WAR ROOM: ULTIMATE INTELLIGENCE SYSTEM")
    print(f"      📅 ข้อมูล ณ วันที่: {datetime.now().strftime('%d %B %Y | %H:%M:%S')}")
    print("═"*75 + "\n")

    score = 0
    
    # --- 1. Agent 004: เจ้ามือ (น้ำหนัก 4 คะแนน) ---
    print("🐳 [1] Agent 004: รายใหญ่ (COT Report) - [น้ำหนัก 40%]")
    whale = load_data('whale_cot_report.csv')
    if whale is not None and not whale.empty:
        latest = whale.iloc[-1]
        print(f"   ► สถานะ: {latest['Status']}")
        print(f"   ► Net Position: {float(latest['Net_Position']):,.0f} สัญญา")
        
        if "BULLISH" in latest['Status']: score += 4
        elif "BEARISH" in latest['Status']: score -= 4
    else:
        print("   ⚠️ ไม่มีข้อมูล (รัน agent_004 ก่อน)")
    print("-" * 50)

    # --- 2. Agent 005: กองทุน SPDR (น้ำหนัก 3 คะแนน) ---
    print("📦 [2] Agent 005: กองทุนโลก (SPDR ETF) - [น้ำหนัก 30%]")
    spdr = load_data('spdr_gold_flows.csv')
    if spdr is not None and not spdr.empty:
        latest = spdr.iloc[-1]
        print(f"   ► ราคา GLD: ${latest['Price']}")
        print(f"   ► อาการวันนี้: {latest['Status']}")
        
        if "BUY" in latest['Status']: score += 3
        elif "SELL" in latest['Status']: score -= 3
    else:
        print("   ⚠️ ไม่มีข้อมูล (รัน agent_005 ก่อน)")
    print("-" * 50)

    # --- 3. Agent 002: กราฟเทคนิค (น้ำหนัก 3 คะแนน) ---
    print("📈 [3] Agent 002: กราฟเทคนิค (Technical Trend) - [น้ำหนัก 30%]")
    price = load_data('market_price_data.csv')
    if price is not None and not price.empty:
        latest = price.iloc[-1]
        print(f"   ► ราคา Spot: ${latest['Price']}")
        print(f"   ► แนวโน้ม: {latest['Trend']}")
        
        if "UPTREND" in latest['Trend']: score += 3
        elif "RECOVERY" in latest['Trend']: score += 1
        elif "DOWNTREND" in latest['Trend']: score -= 3
        elif "CORRECTION" in latest['Trend']: score -= 1
    else:
        print("   ⚠️ ไม่มีข้อมูล (รัน agent_002 ก่อน)")
    print("-" * 50)

    # --- สรุปผลการรบ (Final Verdict) ---
    print("\n" + "═"*75)
    print(f"             🎖️  คะแนนรวมสัญญาณรบ: {score} / 10  🎖️")
    print("═"*75)

    if score >= 7:
        print("\n    🚀 EXTREME BULLISH (กระทิงดุ) - บุกเต็มกำลัง!")
        print("    [Action]: เน้นเปิดสถานะ BUY / ถือ Run Trend ยาวๆ")
    elif 3 <= score < 7:
        print("\n    ✅ MODERATE BULLISH (กระทิงหนุ่ม) - ย่อซื้อ")
        print("    [Action]: รอราคาย่อตัวแล้วค่อยเข้า Buy (อย่าไล่ราคา)")
    elif -3 < score < 3:
        print("\n    ✋ NEUTRAL / SIDEWAY (ตลาดเลือกทาง)")
        print("    [Action]: นั่งทับมือรอ หรือเทรดสั้นๆ ในกรอบ")
    elif score <= -3:
        print("\n    🔻 BEARISH (หมีตะปบ) - เด้งขาย")
        print("    [Action]: หาจังหวะเปิดสถานะ SELL หรือลดพอร์ต")
    
    print("\n" + "═"*75)

if __name__ == "__main__":
    start_war_room()