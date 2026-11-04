import streamlit as st
import pandas as pd
import numpy as np
import datetime
import plotly.express as px # เพิ่มไลบรารีสร้างกราฟที่สวยงามขึ้น

# 1. ตั้งค่าหน้าเพจ
st.set_page_config(page_title="ระบบเช็กชื่อเข้าแถว", page_icon="🚩", layout="wide")
st.title("🚩 ระบบเช็กชื่อกิจกรรมหน้าเสาธง")
st.markdown("วิเคราะห์สถิติการร่วมกิจกรรม และประเมินเกณฑ์ผ่าน (80%)")

# 2. เมนูด้านข้างสำหรับอัปโหลดไฟล์
st.sidebar.header("ตั้งค่าข้อมูล")
uploaded_file = st.sidebar.file_uploader("อัปโหลดไฟล์รายชื่อ (CSV/Excel)", type=["csv", "xlsx"])

# 3. ตรวจสอบไฟล์อัปโหลด / ข้อมูลตัวอย่าง
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

# 4. ส่วนแสดงผลหลัก
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
        
        check_date = st.date_input("📅 เลือกวันที่เช็กชื่อ", datetime.date.today())
        st.write(f"เลือกสถานะการมาเข้าแถวของนักเรียน ประจำวันที่ **{check_date.strftime('%d/%m/%Y')}**")
        
        df_edit = df[['รหัสนักเรียน', 'ชื่อ-นามสกุล']].copy()
        df_edit['สถานะวันนี้'] = "มา" 
        
        edited_df = st.data_editor(
            df_edit,
            column_config={
                "สถานะวันนี้": st.column_config.SelectboxColumn(
                    "สถานะ (คลิกเพื่อเปลี่ยน)",
                    help="เลือกสถานะการมา",
                    options=["มา", "ลาป่วย", "ลากิจ", "สาย", "ขาด"],
                    required=True,
                )
            },
            hide_index=True,
            use_container_width=True
        )
        
        if st.button("💾 บันทึกข้อมูลของวันนี้"):
            st.success(f"บันทึกข้อมูลการเข้าแถวประจำวันที่ {check_date.strftime('%d/%m/%Y')} สำเร็จ!")

    # --- TAB 2: สรุปผลและสถิติ (รูปแบบใหม่) ---
    with tab2:
        st.subheader("สรุปสถิติและประเมินเกณฑ์ 80%")
        
        # จัดกลุ่มสถานะ
        df['ประเมินผล'] = df['เปอร์เซ็นต์ (%)'].apply(lambda x: '✅ ผ่าน' if x >= 80 else '⚠️ เฝ้าระวัง' if x >= 70 else '❌ ไม่ผ่าน')
        
        # --- ส่วนที่ 1: การ์ดสรุปตัวเลข (Metric Cards) ---
        total_students = len(df)
        pass_count = len(df[df['ประเมินผล'] == '✅ ผ่าน'])
        warn_count = len(df[df['ประเมินผล'] == '⚠️ เฝ้าระวัง'])
        fail_count = len(df[df['ประเมินผล'] == '❌ ไม่ผ่าน'])

        col1, col2, col3, col4 = st.columns(4)
        col1.metric("👥 นักเรียนทั้งหมด", f"{total_students} คน")
        col2.metric("✅ ผ่านเกณฑ์", f"{pass_count} คน")
        col3.metric("⚠️ เฝ้าระวัง", f"{warn_count} คน")
        col4.metric("❌ ไม่ผ่านเกณฑ์", f"{fail_count} คน")
        
        st.markdown("---")
        
        # --- ส่วนที่ 2: ตารางข้อมูลลงสี ---
        def highlight_percentage(val):
            if val >= 80:
                color = '#d4edda' 
            elif val >= 70:
                color = '#fff3cd' 
            else:
                color = '#f8d7da' 
            return f'background-color: {color}'
        
        styled_df = df.style.map(highlight_percentage, subset=['เปอร์เซ็นต์ (%)'])
        st.dataframe(styled_df, use_container_width=True, hide_index=True)
        
        st.markdown("---")
        
        # --- ส่วนที่ 3: กราฟสถิติแบบแยกสี (Plotly) ---
        st.subheader("📊 กราฟวิเคราะห์ข้อมูล")
        
        status_df = df['ประเมินผล'].value_counts().reset_index()
        status_df.columns = ['สถานะ', 'จำนวน']
        
        # กำหนดสีให้ตรงกับสถานะ (เขียว, เหลือง, แดง)
        color_map = {'✅ ผ่าน': '#28a745', '⚠️ เฝ้าระวัง': '#ffc107', '❌ ไม่ผ่าน': '#dc3545'}
        
        col_chart1, col_chart2 = st.columns(2)
        
        # กราฟโดนัท (สัดส่วน)
        with col_chart1:
            fig_pie = px.pie(status_df, values='จำนวน', names='สถานะ', 
                             title='สัดส่วนสถานะนักเรียน',
                             color='สถานะ', color_discrete_map=color_map, hole=0.4)
            st.plotly_chart(fig_pie, use_container_width=True)
            
        # กราฟแท่ง (จำนวนคน)
        with col_chart2:
            fig_bar = px.bar(status_df, x='สถานะ', y='จำนวน', 
                             title='จำนวนนักเรียนแยกตามสถานะ',
                             color='สถานะ', color_discrete_map=color_map, text='จำนวน')
            fig_bar.update_traces(textposition='outside')
            st.plotly_chart(fig_bar, use_container_width=True)
