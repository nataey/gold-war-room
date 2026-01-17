import streamlit as st
import pandas as pd
import requests
import io
import yfinance as yf
import plotly.graph_objects as go

st.set_page_config(page_title="Gold War Room", layout="wide")

st.title("🏆 Gold Mega Project: War Room")
st.markdown("### ศูนย์บัญชาการข้อมูลทองคำและเศรษฐกิจโลก")
st.markdown("---")

# --- 1. ฟังก์ชันดึงราคาตลาดโลก ---
def get_market_data():
    tickers = ['GC=F', 'CL=F', 'DX-Y.NYB']
    data = yf.download(tickers, period="1d", interval="15m", progress=False)
    last_prices = {}
    try:
        last_prices['Gold'] = data['Close']['GC=F'].iloc[-1]
        last_prices['Oil'] = data['Close']['CL=F'].iloc[-1]
        last_prices['DXY'] = data['Close']['DX-Y.NYB'].iloc[-1]
    except:
        last_prices = {'Gold': 0, 'Oil': 0, 'DXY': 0}
    return last_prices, data

# --- 2. ฟังก์ชันดึงข่าว ---
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

# --- 3. สมองกลวิเคราะห์ข่าว ---
def analyze_news(title, forecast):
    title_lower = title.lower()
    if "cpi" in title_lower:
        return "ดัชนีราคาผู้บริโภค (CPI)", "🔥 เงินเฟ้อ: ถ้าสูงกว่าคาด -> ทองร่วง"
    elif "ppi" in title_lower:
        return "ดัชนีราคาผู้ผลิต (PPI)", "🏭 ต้นทุนผลิต: ถ้าสูง -> กดดันทอง"
    elif "employment" in title_lower or "claims" in title_lower:
        return "ยอดคนว่างงาน", "👷 ว่างงาน: ถ้าคนตกงานเยอะ -> ทองพุ่ง!"
    elif "fed" in title_lower:
        return "ดอกเบี้ย FED", "🏦 ดอกเบี้ย: ถ้าขึ้น -> ทองร่วง, ถ้าลด -> ทองบิน"
    else:
        return title, "⚠️ รอติดตามตัวเลขจริง"

# ================= ส่วนแสดงผล =================
prices, chart_data = get_market_data()
m1, m2, m3 = st.columns(3)
with m1: st.metric("🥇 ทองคำ", f"${prices['Gold']:.2f}")
with m2: st.metric("🛢️ น้ำมัน", f"${prices['Oil']:.2f}")
with m3: st.metric("💵 ดอลลาร์", f"{prices['DXY']:.2f}")

st.markdown("---")
col1, col2 = st.columns([1.5, 1])

with col1:
    st.subheader("📈 กราฟราคา")
    if 'Close' in chart_data:
        gold_series = chart_data['Close']['GC=F']
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=gold_series.index, y=gold_series.values, mode='lines+markers', name='Gold', line=dict(color='#FFD700')))
        fig.update_layout(title="Gold Price (15m)", height=350, template="plotly_dark")
        st.plotly_chart(fig, use_container_width=True)
    
    st.caption("ปฏิทินข่าว")
    df_news = get_forex_data()
    if not df_news.empty:
        st.dataframe(df_news[['time', 'title', 'forecast']], use_container_width=True)

with col2:
    st.subheader("🤖 วิเคราะห์")
    if not df_news.empty:
        for index, row in df_news.iterrows():
            thai_name, analysis = analyze_news(row['title'], row['forecast'])
            with st.expander(f"📌 {thai_name}"):
                st.write(analysis)
                st.caption(f"Forecast: {row['forecast']}")
    else:
        st.write("ไม่มีข่าวแดงสำคัญเร็วๆ นี้")
