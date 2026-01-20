import streamlit as st
import requests
import json
import pandas as pd
import os
from newsapi import NewsApiClient
from datetime import datetime, timedelta
import re

# ตั้งค่าหน้าเว็บ
st.set_page_config(page_title="Gold AI Specialist v2.5", page_icon="💰", layout="wide")

st.title("💰 Gold Market Intelligence Agent (Gemini 2.5)")
st.caption("วิเคราะห์เจาะลึกนโยบาย Trump & Greenland เพื่อเป้าหมาย Mega Project")

# ==============================================================================
# 🔴 ส่วนตั้งค่า API Keys (รองรับทั้ง Streamlit Secrets และใส่เอง)
# ==============================================================================
GEMINI_API_KEY = "AIzaSyBuKjq9VmJQPA5-c0FAaVl84gcniI0ugpM"
NEWS_API_KEY = "0a47175d76d1481596c418e474739272"

# Path สำหรับบันทึกข้อมูลเข้า War Room
OUTPUT_FILE = "data/news_intelligence.csv"
if not os.path.exists("data"): os.makedirs("data")

# ==============================================================================
# ฟังก์ชันการทำงาน
# ==============================================================================

def get_detailed_analysis(news_list):
    # เปลี่ยนมาใช้โมเดลล่าสุด Gemini 2.5 Flash
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={GEMINI_API_KEY}"
    headers = {'Content-Type': 'application/json'}
    
    news_input = ""
    for i, n in enumerate(news_list):
        news_input += f"ข่าวที่ {i+1} [เวลา: {n['publishedAt']}]: {n['title']} - {n['description']}\n\n"

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
                "weight": 0-100
            }}
        ],
        "overall_sentiment_score": 0-100,
        "overall_summary": "สรุปสภาวะตลาด",
        "action_plan": "คำแนะนำการลงทุน"
    }}
    """
    
    data = {
        "contents": [{"parts": [{"text": prompt}]}],
        "safetySettings": [
            {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"},
            {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"}
        ]
    }
    
    try:
        response = requests.post(url, headers=headers, json=data)
        if response.status_code == 200:
            res_data = response.json()
            return res_data['candidates'][0]['content']['parts'][0]['text']
        return None
    except Exception as e:
        st.error(f"AI Error: {e}")
        return None

def clean_json_text(text):
    if not text: return None
    text = re.sub(r'```json\s*', '', text)
    text = re.sub(r'```', '', text)
    return text.strip()

# ==============================================================================
# ส่วนแสดงผล Dashboard
# ==============================================================================

if st.button("🚀 เริ่มการวิเคราะห์เชิงลึก (Gemini 2.5 Engine)", type="primary"):
    with st.spinner('📡 กำลังดึงข้อมูลข่าวกรองล่าสุด...'):
        newsapi = NewsApiClient(api_key=NEWS_API_KEY)
        
        keywords = [
            "Gold Price impact Trump",
            "Trump Greenland", 
            "Trump 10 percent tariff", 
            "Trump trade war",
            "Federal Reserve interest rate"
        ]
        
        query_text = " OR ".join([f'"{k}"' for k in keywords])
        
        all_articles = newsapi.get_everything(
            q=query_text,
            from_param=(datetime.now() - timedelta(days=2)).strftime('%Y-%m-%d'),
            language='en',
            sort_by='publishedAt',
            page_size=10
        )
        articles = all_articles.get('articles', [])

        if articles:
            raw_res = get_detailed_analysis(articles)
            
            if raw_res:
                try:
                    analysis = json.loads(clean_json_text(raw_res))
                    
                    # --- แสดงผลหน้าเว็บ ---
                    st.divider()
                    col_a, col_b = st.columns([1, 2])
                    with col_a:
                        st.metric("Overall Score", f"{analysis.get('overall_sentiment_score')}/100")
                    with col_b:
                        st.info(f"**วิเคราะห์ภาพรวม:** {analysis.get('overall_summary')}")
                        st.success(f"**กลยุทธ์แนะนำ:** {analysis.get('action_plan')}")

                    # --- 💾 ส่วนบันทึกลง CSV เพื่อ Mega Project ---
                    rows = []
                    for news in analysis.get('individual_news', []):
                        rows.append({
                            "Date": datetime.now().strftime("%Y-%m-%d %H:%M"),
                            "Title": news.get('title'),
                            "Summary": news.get('summary'),
                            "Weight": news.get('weight'),
                            "Overall_Score": analysis.get('overall_sentiment_score'),
                            "Action": analysis.get('action_plan')
                        })
                    
                    df = pd.DataFrame(rows)
                    df.to_csv(OUTPUT_FILE, index=False, encoding='utf-8-sig')
                    st.toast("✅ บันทึกข้อมูลเข้า War Room เรียบร้อย!", icon="💾")

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
                                if weight >= 60: st.write("🟢 Bullish")
                                elif weight <= 40: st.write("🔴 Bearish")
                                else: st.write("🟡 Neutral")

                except Exception as e:
                    st.error(f"การถอดรหัสข้อมูลผิดพลาด: {e}")
        else:
            st.warning("ไม่พบข่าวใหม่ในฐานข้อมูล")