import streamlit as st
import pandas as pd
import requests
import io
import yfinance as yf
import plotly.graph_objects as go
from datetime import datetime

# --- ตั้งค่าหน้าเว็บให้กว้างและใส่ Icon หัวเว็บ ---
st.set_page_config(page_title="Gold War Room Pro", page_icon="🏆", layout="wide")

# ================= 1. ส่วนดึงข้อมูล (Backend) =================
def get_market_data():
    # ดึงย้อนหลัง 2 วันเพื่อคำนวณว่า "บวก" หรือ "ลบ" จากเมื่อวาน
    tickers = ['GC=F', 'CL=F', 'DX-Y.NYB']
    data = yf.download(tickers, period="2d", interval="15m", progress=False)
    
    market_info = {}
    try:
        # ดึงราคาล่าสุด
        gold_now = data['Close']['GC=F'].iloc[-1]
        oil_now = data['Close']['CL=F'].iloc[-1]
        dxy_now = data['Close']['DX-Y.NYB'].iloc[-1]
        
        # ดึงราคาปิดวันก่อน (เพื่อหา Delta)
        # (ใช้วิธีง่ายๆ คือเอาตัวแรกของช่วงเวลามาเทียบ)
        gold_open = data['Open']['GC=F'].iloc[0]
        oil_open = data['Open']['CL=F'].iloc[0]
        dxy_open = data['Open']['DX-Y.NYB'].iloc[0]

        market_info = {
            'Gold': {'price': gold_now, 'change': gold_now - gold_open},
            'Oil': {'price': oil_now, 'change': oil_now - oil_open},
            'DXY': {'price': dxy_now, 'change': dxy_now - dxy_open}
        }
    except:
        # กันเหนียวเผื่อ Error
        market_info = {
            'Gold': {'price': 0, 'change': 0},
            'Oil': {'price': 0, 'change': 0},
            'DXY': {'price': 0, 'change': 0}
        }
    return market_info, data

def get_forex_data():
    url = "https://nfs.faireconomy.media/ff_calendar_thisweek.xml"
    headers = {"User-Agent": "Mozilla/5.0"}
    try:
        response = requests.get(url, headers=headers)
        df = pd.read_xml(io.BytesIO(response.content))
        if 'actual' not in df.columns: df['actual'] = ""
        df = df[(df['country'] == 'USD') & (df['impact'] == 'High')]
        return df
    except:
        return pd.DataFrame()

def analyze_news(title, forecast):
    title_lower = title.lower()
    if "cpi" in title_lower:
        return "🏷️ ดัชนีเงินเฟ้อ (CPI)", "🔥 ถ้าสูงกว่าคาด -> ทองร่วง"
    elif "ppi" in title_lower:
        return "🏭 ดัชนีผู้ผลิต (PPI)", "⚠️ ถ้าสูง -> ต้นทุนพุ่ง -> ทองกดดัน"
    elif "employment" in title_lower or "non-farm" in title_lower:
        return "👷 การจ้างงาน (Non-Farm)", "🚀 ถ้าจ้างงานแย่ -> ทองพุ่ง!"
    elif "fed" in title_lower:
        return "🏦 ดอกเบี้ย FED", "💀 ข่าวใหญ่: ระวังความผันผวนสูง"
    else:
        return f"📰 {title}", "👀 รอติดตามตัวเลขจริง"

# ================= 2. ส่วนแสดงผล (Frontend) =================

# --- A. Sidebar (เมนูด้านข้าง) ---
with st.sidebar:
    st.title("🏆 Gold War Room")
    st.caption("System: Online ✅")
    st.markdown("---")
    st.info("👋 สวัสดีครับ! นี่คือระบบวิเคราะห์ทองคำส่วนตัวของคุณ")
    st.markdown("**Last Update:**")
    st.text(datetime.now().strftime("%H:%M:%S"))
    
# --- B. ส่วนหัว (Metrics) ---
st.markdown("### 🌍 ภาพรวมตลาด Real-time")
prices, chart_data = get_market_data()

m1, m2, m3 = st.columns(3)
with m1:
    st.metric("🥇 ทองคำ (Gold)", f"${prices['Gold']['price']:.2f}", f"{prices['Gold']['change']:.2f}")
with m2:
    st.metric("🛢️ น้ำมัน (WTI)", f"${prices['Oil']['price']:.2f}", f"{prices['Oil']['change']:.2f}")
with m3:
    st.metric("💵 ดอลลาร์ (DXY)", f"{prices['DXY']['price']:.2f}", f"{prices['DXY']['change']:.2f}")

st.markdown("---")

# --- C. ส่วนเนื้อหา (Tabs) ---
tab1, tab2 = st.tabs(["📊 กราฟเทคนิค", "🤖 ข่าว & บทวิเคราะห์"])

with tab1: # แท็บที่ 1: กราฟ
    st.subheader("📈 กราฟราคาทองคำ (15 นาที)")
    if 'Close' in chart_data:
        gold_vals = chart_data['Close']['GC=F']
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=gold_vals.index, y=gold_vals.values, 
                                 mode='lines', name='Gold', 
                                 line=dict(color='#FFD700', width=2),
                                 fill='tozeroy')) # ถมสีใต้กราฟให้ดูแพง
        fig.update_layout(height=400, template="plotly_dark", margin=dict(l=0, r=0, t=30, b=0))
        st.plotly_chart(fig, use_container_width=True)

with tab2: # แท็บที่ 2: ข่าว
    st.subheader("📅 ปฏิทินเศรษฐกิจ & AI Logic")
    col_news_1, col_news_2 = st.columns([1.5, 1])
    
    df_news = get_forex_data()
    
    with col_news_1:
        st.caption("ตารางข่าว Forex Factory (เฉพาะข่าวแดง)")
        if not df_news.empty:
            st.dataframe(df_news[['date', 'time', 'title', 'forecast']], use_container_width=True)
        else:
            st.info("วันนี้ไม่มีข่าวแดงครับ นอนหลับสบายใจได้ 💤")

    with col_news_2:
        st.caption("💡 บทวิเคราะห์อัตโนมัติ")
        if not df_news.empty:
            for index, row in df_news.iterrows():
                thai_title, analysis = analyze_news(row['title'], row['forecast'])
                with st.expander(f"{thai_title}"):
                    st.write(f"**คำแนะนำ:** {analysis}")
                    st.write(f"**คาดการณ์:** {row['forecast']}")
