import requests
import pandas as pd
import io
import os
from datetime import datetime

# --- 1. ตั้งค่าเป้าหมาย ---
DATA_FOLDER = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data')
OUTPUT_FILE = "economic_calendar.csv"

# URL ของ Forex Factory (แหล่งขุมทรัพย์ของคุณ)
URL = "https://nfs.faireconomy.media/ff_calendar_thisweek.xml"

# --- 2. สมองกลวิเคราะห์ข่าว (Logic ของสหายที่เยี่ยมยอดอยู่แล้ว) ---
def analyze_impact(title, forecast):
    title_lower = title.lower()
    # เพิ่ม Logic: ถ้าไม่มี forecast ให้บอกว่าจับตาดูเฉยๆ
    forecast_text = f"(คาดการณ์: {forecast})" if forecast else ""
    
    if "cpi" in title_lower:
        return "ดัชนีราคาผู้บริโภค (CPI)", f"🔥 เงินเฟ้อ: ถ้าจริง > คาด -> ทองร่วง {forecast_text}"
    elif "ppi" in title_lower:
        return "ดัชนีราคาผู้ผลิต (PPI)", f"🏭 ต้นทุนผลิต: ถ้าจริง > คาด -> กดดันทอง {forecast_text}"
    elif "non-farm" in title_lower or "employment" in title_lower:
        return "การจ้างงาน (Non-Farm)", f"👷 จ้างงาน: ถ้าตัวเลขดี -> ทองร่วง! {forecast_text}"
    elif "claims" in title_lower:
        return "ยอดคนว่างงาน", f"⚠️ คนตกงาน: ถ้าสูง -> ทองพุ่ง {forecast_text}"
    elif "fed" in title_lower or "fomc" in title_lower:
        return "ดอกเบี้ย/แถลงการณ์ FED", f"🏦 จับตาถ้อยคำประธานเฟด! {forecast_text}"
    elif "gdp" in title_lower:
        return "GDP สหรัฐฯ", f"🇺🇸 เศรษฐกิจ: ถ้าโตแรง -> ทองร่วง {forecast_text}"
    else:
        return title, f"รอติดตามตัวเลขจริง {forecast_text}"

# --- 3. ระบบดึงข้อมูล (Core Function) ---
def fetch_economic_data():
    print(f"\n📅 Agent 003 (Macro Economist): กำลังดึงปฏิทินเศรษฐกิจ... ({datetime.now().strftime('%H:%M:%S')})")
    
    headers = {"User-Agent": "Mozilla/5.0"}
    try:
        response = requests.get(URL, headers=headers)
        # อ่าน XML แปลงเป็น DataFrame
        df = pd.read_xml(io.BytesIO(response.content))
        
        # กรองเฉพาะข่าว USD และความแรงระดับ High (ตามสูตรของสหาย)
        # และกรองเฉพาะข่าววันนี้หรืออนาคต (ไม่เอาอดีตที่ไกลเกินไป)
        today = datetime.now().date()
        
        # แปลงวันที่ใน xml เป็น format ที่ python เข้าใจ
        # หมายเหตุ: date ใน xml ของ ff เป็น format 'YYYY-MM-DD' หรือใกล้เคียง
        # ถ้ามีปัญหาเรื่อง timezone อาจจะต้องจูนเพิ่ม แต่เบื้องต้นเอาแบบนี้ก่อน
        
        relevant_news = df[
            (df['country'] == 'USD') & 
            (df['impact'] == 'High')
        ].copy()

        if relevant_news.empty:
            print("   🤷‍♂️ สัปดาห์นี้ไม่มีข่าวแดง USD ที่น่าสนใจเลยครับ")
            return []

        processed_data = []
        for index, row in relevant_news.iterrows():
            # ใช้สมองกลวิเคราะห์
            thai_title, strategy = analyze_impact(row['title'], row.get('forecast', ''))
            
            item = {
                "Date": row['date'],
                "Time": row['time'],
                "Title": row['title'],
                "Thai_Title": thai_title,
                "Forecast": row.get('forecast', '-'),
                "Previous": row.get('previous', '-'),
                "Strategy": strategy, # คำแนะนำการเทรด
                "Timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            processed_data.append(item)
            
        return processed_data

    except Exception as e:
        print(f"   ❌ เกิดข้อผิดพลาดในการดึงข้อมูล: {e}")
        return []

# --- 4. บันทึกข้อมูล ---
def save_data(data_list):
    if not data_list: return

    if not os.path.exists(DATA_FOLDER):
        os.makedirs(DATA_FOLDER)

    file_path = os.path.join(DATA_FOLDER, OUTPUT_FILE)
    df = pd.DataFrame(data_list)
    
    # เขียนทับไปเลยสำหรับปฏิทิน (เพราะมัน update เป็นรายสัปดาห์) 
    # หรือจะ append ก็ได้ แต่ปฏิทินมักจะดู "อนาคต" ผมแนะนำเขียนทับ (mode='w') จะได้ไม่ซ้ำซ้อน
    df.to_csv(file_path, mode='w', header=True, index=False)
        
    print(f"✅ Agent 003: อัปเดตปฏิทินเศรษฐกิจ {len(data_list)} รายการ เรียบร้อย!")
    print(f"📂 เก็บไว้ที่: {file_path}")
    print("\n--- 📅 ปฏิทินข่าวแดงสัปดาห์นี้ ---")
    print(df[['Date', 'Time', 'Thai_Title', 'Forecast']].to_string(index=False))
    print("-" * 50)

# --- 5. สั่งทำงาน ---
if __name__ == "__main__":
    print("--- 🏛️ STARTING AGENT 003: MACRO ECONOMIST ---")
    data = fetch_economic_data()
    save_data(data)
    print("--- 😴 MISSION COMPLETE ---")