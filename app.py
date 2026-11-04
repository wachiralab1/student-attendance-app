import streamlit as st
import pandas as pd
import numpy as np
import datetime # 1. เพิ่มไลบรารีสำหรับจัดการวันที่

# ตั้งค่าหน้าเพจ
st.set_page_config(page_title="ระบบเช็กชื่อเข้าแถว", page_icon="🚩", layout="wide")
st.title("🚩 ระบบเช็กชื่อกิจกรรมหน้าเสาธง")
st.markdown("วิเคราะห์สถิติการร่วมกิจกรรม และประเมินเกณฑ์ผ่าน (80%)")

# เมนูด้านข้างสำหรับอัปโหลดไฟล์
st.sidebar.header("ตั้งค่าข้อมูล")
uploaded_file = st.sidebar.file_uploader("อัปโหลดไฟล์รายชื่อ (CSV/Excel)", type=["csv", "xlsx"])

# ตรวจสอบว่ามีไฟล์อัปโหลดมาหรือไม่
if uploaded_file is None:
    st.info("👈 กรุณาอัปโหลดไฟล์รายชื่อที่เมนูด้านซ้าย หรือกดปุ่มด้านล่างเพื่อดูตัวอย่าง")
    if st.button("คลิกเพื่อโหลดข้อมูลตัวอย่าง (Demo Data)"):
        data = {
            "รหัสนักเรียน": ["1001", "1002", "1003", "1004", "1005"],
            "ชื่อ-นามสกุล": ["ด.ช. สมชาย รักดี", "ด.ช. สมเกียรติ ขยัน", "ด.ญ. สมใจ มุ่งมั่น", "ด.ญ. สมฤดี ดีงาม", "ด.ช. สมยศ เกเร"],
            "วันเปิดเรียนสะสม": [20, 20, 20, 20, 20],
            "จำนวนวันที่มาสะสม": [20, 18, 15, 14, 10]
        }
        df = pd.DataFrame(data)
        st.session_state['df'] = df
else:
    if uploaded_file.name.endswith('csv'):
        df = pd.read_csv(uploaded_file)
    else:
        df = pd.read_excel(uploaded_file)
    st.session_state['df'] = df

# ส่วนแสดงผลหลัก
if 'df' in st.session_state:
    df = st.session_state['df']
    
    if 'เปอร์เซ็นต์ (%)' not in df.columns:
        df['เปอร์เซ็นต์ (%)'] = (df['จำนวนวันที่มาสะสม'] / df['วันเปิดเรียนสะสม']) * 100
        
    tab1, tab2 = st.tabs(["📋 เช็กชื่อประจำวัน", "📊 สรุปผลรายเดือน"])

    # --- TAB 1: ระบบเช็กชื่อ ---
    with tab1:
        st.subheader("เช็กชื่อประจำวัน")
        
        # 2. เพิ่มปฏิทินเลือกวันที่ (ค่าเริ่มต้นคือวันปัจจุบัน)
        check_date = st.date_input("📅 เลือกวันที่เช็กชื่อ", datetime.date.today())
        st.write(f"เลือกสถานะการมาเข้าแถวของนักเรียน ประจำวันที่ **{check_date.strftime('%d/%m/%Y')}**")
        
        df_edit = df[['รหัสนักเรียน', 'ชื่อ-นามสกุล']].copy()
        df_edit['สถานะวันนี้'] = "มา" 
        
        # 3. อัปเดตตัวเลือกสถานะการลา
        edited_df = st.data_editor(
            df_edit,
            column_config={
                "สถานะวันนี้": st.column_config.SelectboxColumn(
                    "สถานะ (คลิกเพื่อเปลี่ยน)",
                    help="เลือกสถานะการมา",
                    options=["มา", "ลาป่วย", "ลากิจ", "สาย", "ขาด"], # เปลี่ยนตรงนี้
                    required=True,
                )
            },
            hide_index=True,
            use_container_width=True
        )
        
        if st.button("💾 บันทึกข้อมูลของวันนี้"):
            st.success(f"บันทึกข้อมูลการเข้าแถวประจำวันที่ {check_date.strftime('%d/%m/%Y')} สำเร็จ!")

    # --- TAB 2: สรุปผลและแจ้งเตือนสี ---
    with tab2:
        st.subheader("สรุปสถิติและประเมินเกณฑ์ 80%")
        
        def highlight_percentage(val):
            if val >= 80:
                color = '#d4edda' 
            elif val >= 70:
                color = '#fff3cd' 
            else:
                color = '#f8d7da' 
            return f'background-color: {color}'
        
        df['ประเมินผล'] = df['เปอร์เซ็นต์ (%)'].apply(lambda x: '✅ ผ่าน' if x >= 80 else '⚠️ เฝ้าระวัง' if x >= 70 else '❌ ไม่ผ่าน')
        
        styled_df = df.style.map(highlight_percentage, subset=['เปอร์เซ็นต์ (%)'])
        st.dataframe(styled_df, use_container_width=True, hide_index=True)
        
        st.subheader("กราฟสรุปจำนวนนักเรียนตามสถานะ")
        status_count = df['ประเมินผล'].value_counts()
        st.bar_chart(status_count)
