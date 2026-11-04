import streamlit as st
import pandas as pd
import numpy as np
import datetime
import plotly.express as px

# 1. ตั้งค่าหน้าเพจ
st.set_page_config(page_title="ระบบเช็กชื่อเข้าแถว", page_icon="🚩", layout="wide")
st.title("🚩 ระบบเช็กชื่อกิจกรรมหน้าเสาธง")
st.markdown("วิเคราะห์สถิติการร่วมกิจกรรม และประเมินเกณฑ์ผ่าน (80%)")

st.sidebar.header("ตั้งค่าข้อมูล")
uploaded_file = st.sidebar.file_uploader("อัปโหลดไฟล์รายชื่อ (CSV/Excel)", type=["csv", "xlsx"])

# 2. สร้างหน่วยความจำสำหรับประวัติ
if 'history' not in st.session_state:
    st.session_state['history'] = pd.DataFrame(columns=['วันที่', 'รหัสนักเรียน', 'ชื่อ-นามสกุล', 'สถานะ'])

# 3. นำเข้าข้อมูล
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

# 4. ส่วนแสดงผล
if 'df' in st.session_state:
    df = st.session_state['df']
    
    # สร้าง 3 Tab
    tab1, tab2, tab3 = st.tabs(["📋 เช็กชื่อประจำวัน", "📊 สรุปผลรายเดือน", "🕒 ประวัติที่บันทึกไว้"])

    # --- TAB 1: ระบบเช็กชื่อ ---
    with tab1:
        st.subheader("เช็กชื่อประจำวัน")
        check_date = st.date_input("📅 เลือกวันที่เช็กชื่อ", datetime.date.today())
        
        df_edit = df[['รหัสนักเรียน', 'ชื่อ-นามสกุล']].copy()
        df_edit['สถานะวันนี้'] = "มา" 
        
        edited_df = st.data_editor(
            df_edit,
            column_config={
                "สถานะวันนี้": st.column_config.SelectboxColumn(
                    "สถานะ (คลิกเพื่อเปลี่ยน)",
                    options=["มา", "ลาป่วย", "ลากิจ", "สาย", "ขาด"],
                    required=True,
                )
            },
            hide_index=True,
            use_container_width=True
        )
        
        if st.button("💾 บันทึกข้อมูลของวันนี้"):
            today_data = edited_df.copy()
            today_data['วันที่'] = check_date.strftime('%d/%m/%Y')
            today_data = today_data.rename(columns={'สถานะวันนี้': 'สถานะ'})
            
            st.session_state['history'] = pd.concat([st.session_state['history'], today_data], ignore_index=True)
            st.success(f"บันทึกข้อมูลวันที่ {check_date.strftime('%d/%m/%Y')} สำเร็จ! (สรุปสถิติจะถูกคำนวณอัตโนมัติในแท็บ 2)")

    # --- TAB 2: สรุปผลและสถิติ (ระบบประมวลผลตามจริง) ---
    with tab2:
        st.subheader("สรุปสถิติและประเมินเกณฑ์ 80%")
        history_df = st.session_state['history']
        
        if history_df.empty:
            st.info("⚠️ ยังไม่มีประวัติการเช็กชื่อในระบบ กรุณาบันทึกเช็กชื่อในแท็บแรกก่อน เพื่อให้ระบบนำมาคำนวณสถิติครับ")
        else:
            # 1. คำนวณวันเปิดเรียนสะสม จากวันที่เคยบันทึกไว้ทั้งหมด
            total_days = history_df['วันที่'].nunique()
            st.write(f"🔄 **ระบบประมวลผลสถิติจากประวัติการเช็กชื่อทั้งหมด: `{total_days}` วัน**")
            
            # 2. สร้างตารางสรุป
            summary_list = []
            for student_id in history_df['รหัสนักเรียน'].unique():
                student_data = history_df[history_df['รหัสนักเรียน'] == student_id]
                name = student_data['ชื่อ-นามสกุล'].iloc[0]
                
                # นับสถานะมา (ถ้านับสายด้วย สามารถบวกเพิ่มได้)
                present_count = (student_data['สถานะ'] == 'มา').sum()
                
                # คำนวณเปอร์เซ็นต์
                pct = (present_count / total_days) * 100 if total_days > 0 else 0
                
                summary_list.append({
                    'รหัสนักเรียน': student_id,
                    'ชื่อ-นามสกุล': name,
                    'วันเปิดเรียนสะสม': total_days,
                    'จำนวนวันที่มาสะสม': present_count,
                    'เปอร์เซ็นต์ (%)': pct
                })
                
            summary_df = pd.DataFrame(summary_list)
            summary_df['ประเมินผล'] = summary_df['เปอร์เซ็นต์ (%)'].apply(lambda x: '✅ ผ่าน' if x >= 80 else '⚠️ เฝ้าระวัง' if x >= 70 else '❌ ไม่ผ่าน')
            
            # 3. ปุ่มดาวน์โหลดผลสถิติสรุป
            csv_summary = summary_df.to_csv(index=False).encode('utf-8-sig')
            st.download_button(
                label=f"📥 ดาวน์โหลดไฟล์สรุปสถิติ ({total_days} วัน)",
                data=csv_summary,
                file_name=f"summary_stats_total_{total_days}days.csv",
                mime="text/csv",
            )
            st.markdown("---")
            
            # 4. ตัวเลขสรุป (โชว์จำนวนคน)
            total_students = len(summary_df)
            pass_count = len(summary_df[summary_df['ประเมินผล'] == '✅ ผ่าน'])
            warn_count = len(summary_df[summary_df['ประเมินผล'] == '⚠️ เฝ้าระวัง'])
            fail_count = len(summary_df[summary_df['ประเมินผล'] == '❌ ไม่ผ่าน'])

            col1, col2, col3, col4 = st.columns(4)
            col1.metric("👥 นักเรียนทั้งหมด", f"{total_students} คน")
            col2.metric("✅ ผ่านเกณฑ์", f"{pass_count} คน")
            col3.metric("⚠️ เฝ้าระวัง", f"{warn_count} คน")
            col4.metric("❌ ไม่ผ่านเกณฑ์", f"{fail_count} คน")
            
            st.markdown("---")
            
            # 5. ตารางลงสี
            def highlight_percentage(val):
                if val >= 80:
                    color = '#d4edda' 
                elif val >= 70:
                    color = '#fff3cd' 
                else:
                    color = '#f8d7da' 
                return f'background-color: {color}'
            
            styled_df = summary_df.style.map(highlight_percentage, subset=['เปอร์เซ็นต์ (%)'])
            st.dataframe(styled_df, use_container_width=True, hide_index=True)
            
            st.markdown("---")
            
            # 6. กราฟวิเคราะห์
            st.subheader("📊 กราฟวิเคราะห์ข้อมูล")
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

    # --- TAB 3: ประวัติการเช็กชื่อ ---
    with tab3:
        st.subheader("🕒 ประวัติการเช็กชื่อที่บันทึกไว้")
        history_df = st.session_state['history']
        
        if not history_df.empty:
            available_dates = history_df['วันที่'].unique().tolist()
            options = ["แสดงทั้งหมด"] + available_dates
            
            selected_date = st.selectbox("📅 เลือกดูข้อมูลตามวันที่:", options)
            
            if selected_date == "แสดงทั้งหมด":
                filtered_history = history_df
                file_name = "attendance_history_all.csv"
            else:
                filtered_history = history_df[history_df['วันที่'] == selected_date]
                date_str = selected_date.replace('/', '')
                file_name = f"attendance_history_{date_str}.csv"
            
            st.write(f"**กำลังแสดงข้อมูลของ:** {selected_date}")
            st.dataframe(filtered_history, use_container_width=True, hide_index=True)
            
            csv_history = filtered_history.to_csv(index=False).encode('utf-8-sig')
            st.download_button(
                label=f"📥 ดาวน์โหลดข้อมูลที่แสดง (CSV)",
                data=csv_history,
                file_name=file_name,
                mime="text/csv",
            )
        else:
            st.info("ยังไม่มีข้อมูลการบันทึกในระบบ (ลองกดบันทึกในหน้า 'เช็กชื่อประจำวัน' ก่อนครับ)")
