import feedparser
import pandas as pd
from datetime import datetime
import os

# --- 1. ตั้งค่าเป้าหมาย (Mission Config) ---
# คำค้นหาที่เราต้องการให้สายลับจับตาดู
KEYWORDS = ["Trump", "Greenland", "NATO", "Gold", "War", "Fed", "Russia", "BRICS"]

# แหล่งข่าว (เราใช้ Google News RSS แบบเจาะจงข่าวโลก)
RSS_FEEDS = [
    "https://news.google.com/rss/search?q=Trump+Greenland+NATO&hl=en-US&gl=US&ceid=US:en",
    "https://news.google.com/rss/search?q=Gold+Price+War&hl=en-US&gl=US&ceid=US:en",
    "https://news.google.com/rss/search?q=Fed+Rate+Decision&hl=en-US&gl=US&ceid=US:en"
]

# ระบุตำแหน่งโฟลเดอร์ data (ย้อนกลับไป 1 ชั้นแล้วเข้า data)
DATA_FOLDER = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data')
OUTPUT_FILE = "political_intelligence.csv"

# --- 2. สมองของหุ่นยนต์ (Core Logic) ---
def fetch_and_filter_news():
    print(f"\n🕵️‍♂️  Agent 001 (Political Scout): กำลังออกลาดตระเวน... ({datetime.now().strftime('%H:%M:%S')})")
    print(f"🎯 เป้าหมายการค้นหา: {KEYWORDS}")
    
    collected_news = []
    
    for url in RSS_FEEDS:
        print(f"   📡 กำลังสแกนคลื่นสัญญาณ: {url[:60]}...")
        try:
            feed = feedparser.parse(url)
            
            for entry in feed.entries:
                title = entry.title
                link = entry.link
                pub_date = entry.published
                
                # กรองข่าว: ตรวจดูว่าหัวข้อข่าวมี Keyword ของเราไหม
                found_keywords = [kw for kw in KEYWORDS if kw.lower() in title.lower()]
                
                if found_keywords:
                    # ถ้าเจอข่าวที่ตรงเงื่อนไข ให้เก็บเข้ากระเป๋า
                    news_item = {
                        "Timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        "Title": title,
                        "Matched_Keywords": ", ".join(found_keywords),
                        "Link": link,
                        "Source": feed.feed.get('title', 'Unknown Source')
                    }
                    collected_news.append(news_item)
        except Exception as e:
            print(f"   ❌ เกิดข้อผิดพลาดที่ URL นี้: {e}")

    return collected_news

def save_intelligence(news_list):
    if not news_list:
        print("🤷‍♂️ Agent 001: รายงานผล - ไม่พบความเคลื่อนไหวตามเป้าหมายครับ")
        return

    # สร้างโฟลเดอร์ data ถ้ายังไม่มี
    if not os.path.exists(DATA_FOLDER):
        os.makedirs(DATA_FOLDER)
        print(f"📁 สร้างห้องเก็บข้อมูลใหม่ที่: {DATA_FOLDER}")

    file_path = os.path.join(DATA_FOLDER, OUTPUT_FILE)
    df = pd.DataFrame(news_list)
    
    # ถ้ามีไฟล์อยู่แล้ว ให้บันทึกต่อท้าย (Append)
    if os.path.exists(file_path):
        df.to_csv(file_path, mode='a', header=False, index=False)
    else:
        df.to_csv(file_path, mode='w', header=True, index=False)
        
    print(f"✅ Agent 001: บันทึกข่าวสำคัญ {len(news_list)} รายการ เรียบร้อย!")
    print(f"📂 เก็บไว้ที่: {file_path}")
    print("\n--- 📝 ตัวอย่างข่าวล่าสุด 3 หัวข้อ ---")
    print(df[['Title', 'Matched_Keywords']].head(3).to_string(index=False))
    print("-" * 50)

# --- 3. เริ่มภารกิจ (Execution) ---
if __name__ == "__main__":
    print("--- 🦅 STARTING MEGA PROJECT: AGENT 001 ---")
    news_data = fetch_and_filter_news()
    save_intelligence(news_data)
    print("--- 😴 MISSION COMPLETE (Sleeping) ---")