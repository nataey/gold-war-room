import streamlit as st
import requests
import json
import pandas as pd
from newsapi import NewsApiClient
from datetime import datetime, timedelta
import re
import os

# --- ตั้งค่าหน้าเว็บตามสไตล์ท่าน ---
st.set_page_config(page_title="Gold AI Specialist v2.5", page_icon="💰", layout="wide")

st.title("💰 Gold Market Intelligence Agent")
st.caption("ยุทธศาสตร์วิเคราะห์ข่าวกรอง (ฉบับเสถียรสูง: บันทึกข้อมูลเข้า War Room)")

# ==============================================================================
# 🔴 ส่วนดึงรหัสจาก Secrets (ดึงจาก .streamlit/secrets.toml)
# ==============================================================================
try:
    GEMINI_API_KEY = st.secrets["GEMINI_API_KEY"]
    NEWS_API_KEY = st.secrets["NEWS_API_KEY"]
except:
    st.error("❌ ไม่พบ API Key! กรุณาตั้งค่าใน .streamlit/secrets.toml")
    st.stop()

# Path สำหรับบันทึกข้อมูล
OUTPUT_FILE = "data/news_intelligence.csv"
if not os.path.exists("data"): os.makedirs("data")

# ==============================================================================
# ฟังก์ชันการทำงาน (คงโครงสร้างเดิมของท่าน แต่เพิ่มเกราะป้องกัน)
# ==============================================================================

def find_best_model():
    # บังคับใช้ 1.5-flash เพื่อความเสถียรตามโค้ดเดิมท่าน
    return "models/gemini-1.5-flash"

def get_detailed_analysis(model_name, news_list):
    clean_model_name = model_name.replace("models/", "")
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{clean_model_name}:generateContent?key={GEMINI_API_KEY}"
    headers = {'Content-Type': 'application/json'}
    
    news_input = ""
    for i, n in enumerate(news_list):
        news_input += f"ข่าวที่ {i+1} [เวลา: {n['publishedAt']}]: {n['title']} - {n.get('description', '')}\n\n"

    prompt = f"""
    ในฐานะนักกลยุทธ์ทองคำ วิเคราะห์ข่าวต่อไปนี้ โดยเน้นนโยบาย Trump (Tariff/Greenland)
    และตอบในรูปแบบ JSON ภาษาไทยเท่านั้น:
    {news_input}
    
    รูปแบบที่ต้องการ:
    {{
        "individual_news": [
            {{
                "title": "หัวข้อข่าวภาษาไทย",
                "summary": "สรุปเนื้อหาสำคัญสั้นๆ",
                "weight": "คะแนนผลกระทบต่อทอง (0-100)"
            }}
        ],
        "overall_sentiment_score": "คะแนนเฉลี่ยภาพรวม",
        "overall_summary": "สรุปสภาวะตลาด",
        "action_plan": "คำแนะนำการลงทุน"
    }}
    """
    
    # 🛡️ นี่คือ "เกราะ" ที่เพิ่มเข้าไปเพื่อให้รันในเครื่องผ่านเหมือนบน Cloud
    data = {
        "contents": [{"parts": [{"text": prompt}]}],
        "safetySettings": [
            {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"},
            {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"},
            {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"},
            {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE"}
        ]
    }
    
    try:
        response = requests.post(url, headers=headers, json=data)
        if response.status_code == 200:
            return response.json()['candidates'][0]['content']['parts'][0]['text']
        return None
    except:
        return None

def clean_json_text(text):
    if not text: return None
    text = re.sub(r'```json\s*', '', text)
    text = re.sub(r'```', '', text)
    return text.strip()

# ==============================================================================
# ส่วนแสดงผล Dashboard
# ==============================================================================

if st.button("🚀 เริ่มการวิเคราะห์เชิงลึก (Sync Mode)", type="primary"):
    with st.spinner('📡 กำลังดึงข่าวกรองและบันทึกฐานข้อมูล...'):
        newsapi = NewsApiClient(api_key=NEWS_API_KEY)
        
        keywords = ["Gold Price impact Trump", "Trump tariff", "US Federal Reserve"]
        query_text = " OR ".join([f'"{k}"' for k in keywords])
        
        all_articles = newsapi.get_everything(
            q=query_text,
            from_param=(datetime.now() - timedelta(days=2)).strftime('%Y-%m-%d'),
            language='en',
            sort_by='publishedAt',
            page_size=7 # ลดจำนวนข่าวลงนิดเพื่อความเร็วและแม่นยำ
        )
        articles = all_articles.get('articles', [])

        if articles:
            best_model = find_best_model()
            raw_res = get_detailed_analysis(best_model, articles)
            
            if raw_res:
                try:
                    analysis = json.loads(clean_json_text(raw_res))
                    
                    # --- แสดงผลหน้าเว็บ (สไตล์เดิมที่ท่านชอบ) ---
                    st.divider()
                    col_a, col_b = st.columns([1, 2])
                    with col_a:
                        st.metric("Overall Score", f"{analysis.get('overall_sentiment_score')}/100")
                    with col_b:
                        st.info(f"**วิเคราะห์ภาพรวม:** {analysis.get('overall_summary')}")
                        st.success(f"**กลยุทธ์แนะนำ:** {analysis.get('action_plan')}")

                    # --- 💾 ส่วนบันทึกลง CSV (หัวใจของ Agent 001) ---
                    rows = []
                    for news in analysis.get('individual_news', []):
                        rows.append({
                            "Date": datetime.now().strftime("%Y-%m-%d %H:%M"),
                            "Title": news.get('title'),
                            "Summary": news.get('summary'),
                            "Weight": news.get('weight'),
                            "Overall_Score": analysis.get('overall_sentiment_score')
                        })
                    pd.DataFrame(rows).to_csv(OUTPUT_FILE, index=False, encoding='utf-8-sig')
                    st.toast("✅ บันทึกข้อมูลเข้า War Room แล้ว")

                    st.subheader("📰 รายงานการวิเคราะห์รายข่าว")
                    for news in analysis.get('individual_news', []):
                        with st.container(border=True):
                            c1, c2 = st.columns([4, 1])
                            with c1:
                                st.write(f"**{news.get('title')}**")
                                st.write(news.get('summary'))
                            with c2:
                                weight = int(news.get('weight', 50))
                                st.subheader(f"{weight}")

                except Exception as e:
                    st.error(f"การถอดรหัสข้อมูลผิดพลาด: {e}")
        else:
            st.warning("ไม่พบข่าวใหม่")

if os.path.exists(OUTPUT_FILE):
    if st.checkbox("📁 ตรวจสอบไฟล์ CSV ในเครื่อง"):
        st.dataframe(pd.read_csv(OUTPUT_FILE))

