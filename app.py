import streamlit as st
import pandas as pd
import numpy as np
import datetime
import plotly.express as px

# 1. ตั้งค่าหน้าเพจ
st.set_page_config(page_title="ระบบเช็กชื่อเข้าแถว", page_icon="🚩", layout="wide")
st.title("🚩 ระบบเช็กชื่อกิจกรรมหน้าเสาธง")
st.markdown("วิเคราะห์สถิติการร่วมกิจกรรม และประเมินเกณฑ์ผ่าน (80%) ในรูปแบบที่ง่ายกว่า")

# 2. เมนูด้านข้าง (อัปเกรดให้อัปโหลดประวัติเดิมมาทำต่อได้)
st.sidebar.header("📁 1. นำเข้าข้อมูลรายชื่อ")
uploaded_file = st.sidebar.file_uploader("อัปโหลดไฟล์รายชื่อ (CSV/Excel)", type=["csv", "xlsx"])

st.sidebar.markdown("---")
st.sidebar.header("📂 2. อัปโหลดประวัติเดิม (ถ้ามี)")
uploaded_history = st.sidebar.file_uploader("อัปโหลดไฟล์ประวัติเดิมมาทำต่อ (CSV)", type=["csv"])

# 3. จัดการข้อมูล Session State
if 'history' not in st.session_state:
    st.session_state['history'] = pd.DataFrame(columns=['วันที่', 'รหัสนักเรียน', 'ชื่อ-นามสกุล', 'สถานะ'])

if uploaded_history is not None:
    st.session_state['history'] = pd.read_csv(uploaded_history)
    st.sidebar.success("โหลดประวัติเดิมสำเร็จ!")

if uploaded_file is None:
    st.info("👈 กรุณาอัปโหลดไฟล์รายชื่อที่เมนูด้านซ้าย หรือกดปุ่มด้านล่างเพื่อดูตัวอย่าง")
    if st.button("คลิกเพื่อโหลดข้อมูลตัวอย่าง (Demo Data)"):
        data = {
            "รหัสนักเรียน": ["1001", "1002", "1003", "1004", "1005"],
            "ชื่อ-นามสกุล": ["ด.ช. สมชาย รักดี", "ด.ช. สมเกียรติ ขยัน", "ด.ญ. สมใจ มุ่งมั่น", "ด.ญ. สมฤดี ดีงาม", "ด.ช. สมยศ เกเร"]
        }
        st.session_state['df'] = pd.DataFrame(data)
else:
    if uploaded_file.name.endswith('csv'):
        st.session_state['df'] = pd.read_csv(uploaded_file)
    else:
        st.session_state['df'] = pd.read_excel(uploaded_file)

# 4. ส่วนแสดงผลหลัก
if 'df' in st.session_state:
    df = st.session_state['df']
    
    tab1, tab2, tab3 = st.tabs(["📋 เช็กชื่อประจำวัน", "📊 สรุปผลแบบ ToSchool", "✏️ จัดการประวัติย้อนหลัง"])

    # --- TAB 1: ระบบเช็กชื่อ ---
    with tab1:
        st.subheader("เช็กชื่อประจำวัน")
        check_date = st.date_input("📅 เลือกวันที่เช็กชื่อ", datetime.date.today())
        
        st.markdown("⚙️ **ตั้งค่าสถานะเริ่มต้นให้ทุกคน (เลือกเพื่อรีเซ็ตตาราง):**")
        bulk_status = st.radio(
            "เลือกสถานะ:",
            ["มา", "ลาป่วย", "ลากิจ", "สาย", "ขาด"],
            horizontal=True,
            label_visibility="collapsed"
        )
        st.markdown("---")
        
        df_edit = df[['รหัสนักเรียน', 'ชื่อ-นามสกุล']].copy()
        df_edit['สถานะวันนี้'] = bulk_status 
        
        editor_key = f"editor_{check_date}_{bulk_status}"
        
        edited_df = st.data_editor(
            df_edit,
            column_config={
                "สถานะวันนี้": st.column_config.SelectboxColumn(
                    "สถานะ (คลิกเพื่อแก้ไขรายคน)",
                    options=["มา", "ลาป่วย", "ลากิจ", "สาย", "ขาด"],
                    required=True,
                )
            },
            hide_index=True,
            use_container_width=True,
            key=editor_key
        )
        
        if st.button("💾 บันทึกข้อมูลเข้าแถว"):
            today_data = edited_df.copy()
            today_data['วันที่'] = check_date.strftime('%d/%m/%Y')
            today_data = today_data.rename(columns={'สถานะวันนี้': 'สถานะ'})
            
            current_history = st.session_state['history']
            current_history = current_history[current_history['วันที่'] != check_date.strftime('%d/%m/%Y')]
            
            st.session_state['history'] = pd.concat([current_history, today_data], ignore_index=True)
            st.success(f"บันทึกข้อมูลวันที่ {check_date.strftime('%d/%m/%Y')} สำเร็จ!")

    # --- TAB 2: สรุปผลสถิติ ---
    with tab2:
        st.subheader("สรุปสถิติและประเมินเกณฑ์ 80%")
        history_df = st.session_state['history']
        
        if history_df.empty:
            st.info("⚠️ ยังไม่มีประวัติการเช็กชื่อในระบบ")
        else:
            total_days = history_df['วันที่'].nunique()
            st.write(f"🔄 **ข้อมูลสะสม: `{total_days}` วัน**")
            
            summary_list = []
            for student_id in history_df['รหัสนักเรียน'].unique():
                student_data = history_df[history_df['รหัสนักเรียน'] == student_id]
                name = student_data['ชื่อ-นามสกุล'].iloc[0]
                present_count = (student_data['สถานะ'] == 'มา').sum()
                
                pct = (present_count / total_days) * 100 if total_days > 0 else 0
                summary_list.append({
                    'รหัสนักเรียน': student_id, 'ชื่อ-นามสกุล': name,
                    'วันเปิดเรียนสะสม': total_days, 'มา (วัน)': present_count,
                    'เปอร์เซ็นต์ (%)': pct
                })
                
            summary_df = pd.DataFrame(summary_list)
            summary_df['ประเมินผล'] = summary_df['เปอร์เซ็นต์ (%)'].apply(lambda x: '✅ ผ่าน' if x >= 80 else '⚠️ เฝ้าระวัง' if x >= 70 else '❌ ไม่ผ่าน')
            
            st.markdown("### 🗓️ ตารางเช็กชื่อรายวัน (Grid View)")
            st.caption("รูปแบบตารางแสดงผลรายวัน เพื่อให้ครูกวาดสายตาดูง่ายเหมือนสมุดพก")
            
            try:
                pivot_df = history_df.pivot(index=['รหัสนักเรียน', 'ชื่อ-นามสกุล'], columns='วันที่', values='สถานะ').reset_index()
                pivot_df = pivot_df.fillna('-') 
                st.dataframe(pivot_df, use_container_width=True, hide_index=True)
            except Exception as e:
                st.warning("เกิดข้อผิดพลาดในการแสดงตารางสมุดพก กรุณาตรวจสอบข้อมูลที่ซ้ำกัน")
                
            st.markdown("---")
            st.markdown("### 📊 สรุปเปอร์เซ็นต์และกราฟ")
            
            csv_summary = summary_df.to_csv(index=False).encode('utf-8-sig')
            st.download_button("📥 ดาวน์โหลดรายงานสรุป (CSV)", data=csv_summary, file_name=f"summary_report.csv", mime="text/csv")
            
            def highlight_percentage(val):
                if val >= 80: color = '#d4edda' 
                elif val >= 70: color = '#fff3cd' 
                else: color = '#f8d7da' 
                return f'background-color: {color}'
            
            st.dataframe(summary_df.style.map(highlight_percentage, subset=['เปอร์เซ็นต์ (%)']), use_container_width=True, hide_index=True)
            
            status_df = summary_df['ประเมินผล'].value_counts().reset_index()
            status_df.columns = ['สถานะ', 'จำนวน']
            color_map = {'✅ ผ่าน': '#28a745', '⚠️ เฝ้าระวัง': '#ffc107', '❌ ไม่ผ่าน': '#dc3545'}
            
            col_chart1, col_chart2 = st.columns(2)
            with col_chart1:
                fig_pie = px.pie(status_df, values='จำนวน', names='สถานะ', title='สัดส่วนสถานะนักเรียน', color='สถานะ', color_discrete_map=color_map, hole=0.4)
                st.plotly_chart(fig_pie, use_container_width=True)
            with col_chart2:
                fig_bar = px.bar(status_df, x='สถานะ', y='จำนวน', title='จำนวนนักเรียนแยกตามสถานะ', color='สถานะ', color_discrete_map=color_map, text='จำนวน')
                fig_bar.update_traces(textposition='outside')
                st.plotly_chart(fig_bar, use_container_width=True)

    # --- TAB 3: ประวัติที่แก้ไขได้ (Edit History) ---
    with tab3:
        st.subheader("✏️ จัดการและแก้ไขประวัติย้อนหลัง")
        st.write("เลือกรวมหรือแยกวันเพื่อดูข้อมูล หากลงผิดสามารถแก้สถานะตรงนี้แล้วกดบันทึกได้เลย")
        
        history_df = st.session_state['history']
        
        if not history_df.empty:
            # 1. สร้าง Dropdown เลือกวันที่
            available_dates = history_df['วันที่'].unique().tolist()
            selected_date = st.selectbox("📅 เลือกวันที่ต้องการดู/แก้ไข:", ["แสดงทั้งหมด"] + available_dates)
            
            # 2. กรองตารางตามที่เลือก
            if selected_date == "แสดงทั้งหมด":
                df_to_edit = history_df
            else:
                df_to_edit = history_df[history_df['วันที่'] == selected_date]
            
            # 3. นำข้อมูลที่กรองแล้วมาแสดงให้แก้
            edited_history = st.data_editor(
                df_to_edit,
                num_rows="dynamic",
                use_container_width=True,
                hide_index=True
            )
            
            col_btn1, col_btn2 = st.columns(2)
            with col_btn1:
                if st.button("💾 บันทึกการแก้ไขประวัติ"):
                    # 4. ลอจิกการเซฟกลับเข้าไปในฐานข้อมูล
                    if selected_date == "แสดงทั้งหมด":
                        st.session_state['history'] = edited_history
                    else:
                        # ดึงข้อมูลวันอื่นๆ (ที่ไม่ใช่วันที่กำลังแก้) เก็บไว้ก่อน
                        kept_history = st.session_state['history'][st.session_state['history']['วันที่'] != selected_date]
                        # เอาข้อมูลวันอื่นๆ มารวมกับข้อมูลวันที่เพิ่งแก้เสร็จ
                        st.session_state['history'] = pd.concat([kept_history, edited_history], ignore_index=True)
                        
                    st.success("อัปเดตประวัติสำเร็จ! (ข้อมูลในแท็บสถิติเปลี่ยนตามแล้ว)")
                    
            with col_btn2:
                csv_history = st.session_state['history'].to_csv(index=False).encode('utf-8-sig')
                st.download_button(
                    label="📥 ดาวน์โหลดไฟล์ฐานข้อมูลประวัติ (เก็บไว้ทำต่อพรุ่งนี้)",
                    data=csv_history,
                    file_name=f"database_history_{datetime.date.today().strftime('%Y%m%d')}.csv",
                    mime="text/csv",
                )
        else:
            st.info("ยังไม่มีข้อมูลการบันทึกในระบบ")
