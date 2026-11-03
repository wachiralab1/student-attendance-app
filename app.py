import streamlit as st
import pandas as pd
import numpy as np

# 1. ตั้งค่าหน้าเพจ
st.set_page_config(page_title="ระบบเช็กชื่อเข้าแถว", page_icon="🚩", layout="wide")
st.title("🚩 ระบบเช็กชื่อกิจกรรมหน้าเสาธง")
st.markdown("วิเคราะห์สถิติการร่วมกิจกรรม และประเมินเกณฑ์ผ่าน (80%)")

# 2. เมนูด้านข้างสำหรับอัปโหลดไฟล์
st.sidebar.header("ตั้งค่าข้อมูล")
uploaded_file = st.sidebar.file_uploader("อัปโหลดไฟล์รายชื่อ (CSV/Excel)", type=["csv", "xlsx"])

# 3. ตรวจสอบว่ามีไฟล์อัปโหลดมาหรือไม่ (ถ้าไม่มีให้ใช้ข้อมูลสมมติทดลองรัน)
if uploaded_file is None:
    st.info("👈 กรุณาอัปโหลดไฟล์รายชื่อที่เมนูด้านซ้าย หรือกดปุ่มด้านล่างเพื่อดูตัวอย่าง")
    if st.button("คลิกเพื่อโหลดข้อมูลตัวอย่าง (Demo Data)"):
        # สร้างข้อมูลจำลอง
        data = {
            "รหัสนักเรียน": ["1001", "1002", "1003", "1004", "1005"],
            "ชื่อ-นามสกุล": ["ด.ช. สมชาย รักดี", "ด.ช. สมเกียรติ ขยัน", "ด.ญ. สมใจ มุ่งมั่น", "ด.ญ. สมฤดี ดีงาม", "ด.ช. สมยศ เกเร"],
            "วันเปิดเรียนสะสม": [20, 20, 20, 20, 20],
            "จำนวนวันที่มาสะสม": [20, 18, 15, 14, 10]
        }
        df = pd.DataFrame(data)
        st.session_state['df'] = df
else:
    # ถ้ามีการอัปโหลดไฟล์ ให้ดึงข้อมูลมาใช้
    if uploaded_file.name.endswith('csv'):
        df = pd.read_csv(uploaded_file)
    else:
        df = pd.read_excel(uploaded_file)
    st.session_state['df'] = df

# 4. ส่วนแสดงผลหลัก (แบ่งเป็น 2 หน้าต่าง/Tab)
if 'df' in st.session_state:
    df = st.session_state['df']
    
    # คำนวณเปอร์เซ็นต์
    if 'เปอร์เซ็นต์ (%)' not in df.columns:
        df['เปอร์เซ็นต์ (%)'] = (df['จำนวนวันที่มาสะสม'] / df['วันเปิดเรียนสะสม']) * 100
        
    # สร้าง Tab
    tab1, tab2 = st.tabs(["📋 เช็กชื่อประจำวัน", "📊 สรุปผลรายเดือน"])

    # --- TAB 1: ระบบเช็กชื่อ ---
    with tab1:
        st.subheader("เช็กชื่อประจำวัน")
        st.write("เลือกสถานะการมาเข้าแถวของนักเรียน (ระบบตั้งค่าเริ่มต้นเป็น 'มา' ให้ทุกคน)")
        
        # คัดลอกข้อมูลมาเพื่อทำช่องเช็กชื่อ
        df_edit = df[['รหัสนักเรียน', 'ชื่อ-นามสกุล']].copy()
        df_edit['สถานะวันนี้'] = "มา" # ค่าเริ่มต้น Quick Check
        
        # ตารางที่สามารถกดแก้ไข dropdown ได้
        edited_df = st.data_editor(
            df_edit,
            column_config={
                "สถานะวันนี้": st.column_config.SelectboxColumn(
                    "สถานะ (คลิกเพื่อเปลี่ยน)",
                    help="เลือกสถานะการมา",
                    options=["มา", "ลา", "สาย", "ขาด"],
                    required=True,
                )
            },
            hide_index=True,
            use_container_width=True
        )
        
        if st.button("💾 บันทึกข้อมูลของวันนี้"):
            st.success("บันทึกข้อมูลการเข้าแถวประจำวันสำเร็จ! (ในระบบจริงข้อมูลจะถูกนำไปรวมกับฐานข้อมูล)")

    # --- TAB 2: สรุปผลและแจ้งเตือนสี ---
    with tab2:
        st.subheader("สรุปสถิติและประเมินเกณฑ์ 80%")
        
        # ฟังก์ชันกำหนดสีตาม %
        def highlight_percentage(val):
            if val >= 80:
                color = '#d4edda' # สีเขียว (ผ่าน)
            elif val >= 70:
                color = '#fff3cd' # สีเหลือง (เฝ้าระวัง)
            else:
                color = '#f8d7da' # สีแดง (ไม่ผ่าน)
            return f'background-color: {color}'
        
        # สร้างคอลัมน์สถานะ
        df['ประเมินผล'] = df['เปอร์เซ็นต์ (%)'].apply(lambda x: '✅ ผ่าน' if x >= 80 else '⚠️ เฝ้าระวัง' if x >= 70 else '❌ ไม่ผ่าน')
        
        # แสดงตารางแบบลงสี
        styled_df = df.style.map(highlight_percentage, subset=['เปอร์เซ็นต์ (%)'])
        st.dataframe(styled_df, use_container_width=True, hide_index=True)
        
        # แสดงกราฟสรุป
        st.subheader("กราฟสรุปจำนวนนักเรียนตามสถานะ")
        status_count = df['ประเมินผล'].value_counts()
        st.bar_chart(status_count)
