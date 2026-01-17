import streamlit as st
from streamlit_option_menu import option_menu
import pandas as pd
import yaml
import requests
import io
import uuid
import time
from datetime import timedelta, datetime
import os
import plotly.express as px
from openpyxl import load_workbook
import json
from zoneinfo import ZoneInfo

# -------------------------------------------------
# ✅ Page Config (MUST BE FIRST Streamlit command)
# -------------------------------------------------
st.set_page_config(page_title="TNEA Full App", layout="wide")

# -------------------------------------------------
# ✅ PREMIUM FLAG (from URL)
# -------------------------------------------------
premium_flag = "0"
try:
    premium_flag = st.query_params.get("premium", "0")  # new streamlit
except:
    premium_flag = st.experimental_get_query_params().get("premium", ["0"])[0]  # old streamlit

is_premium = str(premium_flag) == "1"

# -------------------------------------------------
# ✅ MODE DISPLAY + BUTTON (same row)
# -------------------------------------------------
col_mode, col_btn = st.columns([3, 1])

with col_mode:
    if is_premium:
        st.success("✅ PREMIUM MODE ENABLED")
    else:
        st.info("🆓 NORMAL MODE (Free User)")

with col_btn:
    st.markdown("<br>", unsafe_allow_html=True)
    if not is_premium:
        st.link_button("💳 Go Premium", "https://tnea-choice-list.streamlit.app/?premium=1")

# -------------------------------------------------
# ✅ Style Settings
# -------------------------------------------------
st.markdown("""
    <style>
    @media (max-width: 768px) {
        .nav-link span { display: inline !important; }
    }
    .stDataFrame div { color: black !important; }
    </style>
""", unsafe_allow_html=True)

# -------------------------------------------------
# ✅ File Paths
# -------------------------------------------------
base_path = "./"
config_path = base_path + "config.yaml"
device_session_path = base_path + "device_session.yaml"
chat_path = base_path + "chat_messages.json"

SESSION_TIMEOUT = 180  # 3 minutes

# -------------------------------------------------
# ✅ Load Config.yaml (Login optional)
# -------------------------------------------------
try:
    with open(config_path) as file:
        config = yaml.safe_load(file)
    user_data = config["credentials"]["users"]
except Exception:
    user_data = {}
    st.warning("⚠️ config.yaml not loaded (Login will not work)")

# -------------------------------------------------
# ✅ Load device_session.yaml
# -------------------------------------------------
try:
    with open(device_session_path) as session_file:
        session_data = yaml.safe_load(session_file)
except Exception:
    session_data = {"active_users": {}}

# -------------------------------------------------
# ✅ Load chat_messages.json
# -------------------------------------------------
if not os.path.exists(chat_path):
    with open(chat_path, "w") as f:
        json.dump([], f)

# -------------------------------------------------
# ✅ Session init
# -------------------------------------------------
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "mobile" not in st.session_state:
    st.session_state.mobile = "Guest"
if "device_id" not in st.session_state:
    st.session_state.device_id = str(uuid.uuid4())

# =================================================
# ✅ MENU
# =================================================
st.markdown("""
    <h2 style='text-align: center; color: #0d6efd; font-weight: bold;'>
        🔽 Select a Feature Below 🔽
    </h2>
""", unsafe_allow_html=True)

col1, col2, col3 = st.columns([1, 2, 1])

with col2:
    if is_premium:
        menu_options = ["Home", "Cutoff Calculator", "College List", "Create TNEA Choice List", "TNEA Vacancy Seat Matrix"]
        menu_icons = ["house", "calculator", "building", "list-check", "table"]
    else:
        menu_options = ["Home", "Cutoff Calculator", "College List"]
        menu_icons = ["house", "calculator", "building"]


    selected = option_menu(
        menu_title=None,
        options=menu_options,
        icons=menu_icons,
        default_index=0,
        orientation="horizontal"
    )

# =================================================
# ✅ PAGE 1: HOME
# =================================================
if selected == "Home":

    # ✅ Welcome Text (ONLY ONE TIME)
    st.markdown("""
        <h1 style='text-align: center; font-weight: bold;'>📘 Welcome to TNEA Info Web App</h1>
        <div style='text-align: center; font-size: 18px; margin-top: 20px;'>
            <b>✅ Create TNEA Choice List</b> – Filter colleges by cutoff, department, and community<br><br>
            <b>📊 TNEA Vacancy Seat Matrix</b> – Analyze vacant seats by branch, college, and community<br><br>
            📞 Contact: +91-8248696926<br>
            📧 Email: rajumurugannp@gmail.com<br>
            👨‍💻 Developed by Dr. Raju Murugan<br><br>
            &copy; 2026 TNEA Info App. All rights reserved.
        </div>
    """, unsafe_allow_html=True)

    # ✅ Premium Offer (ONLY Free)
    if not is_premium:
        st.markdown("---")
        st.markdown("## 🔒 Premium Features")
        st.warning("Premium unlocks: ✅ Choice List + ✅ Vacancy Seat Matrix")
        st.markdown("💳 Lifetime Premium: **₹299 (One Time Payment)**")
        st.info("👉 Click 💳 Go Premium button (top right) to unlock Premium ✅")

    # ✅ Previous Year Question Papers (FREE for all)
    st.markdown("---")
    st.markdown("### 📚 Previous Year Question Papers")

    st.markdown("""
    <div style='background-color: #f9f9f9; padding: 15px; border-left: 8px solid #4CAF50; border-radius: 10px; font-size: 16px;'>
    📘 <a href='https://globaleduhub4u.blogspot.com/2025/03/anna-university-previous-year-questions.html' target='_blank' style='text-decoration: none; color: #007bff; font-weight: bold;'>Anna University Previous Year Question Papers</a><br>
    📗 <a href='https://globaleduhub4u.blogspot.com/p/gate-previous-year-qps.html' target='_blank' style='text-decoration: none; color: #007bff; font-weight: bold;'>GATE Previous Year Question Papers</a><br>
    📘 <a href='https://globaleduhub4u.blogspot.com/2025/03/numberiq.html' target='_blank' style='text-decoration: none; color: #007bff; font-weight: bold;'>Check Your Maths IQ</a><br>
    </div>
    """, unsafe_allow_html=True)

    # ✅ Chat Feature
    st.markdown("---")
    st.subheader("💬 Community Chat Room")

    with open(chat_path, "r") as f:
        chat_data = json.load(f)

    for entry in chat_data[-100:]:
        st.markdown(f"**{entry.get('user','Guest')}**: {entry.get('message','')}")

    new_message = st.text_input("Type your message...", key="chat_message_input")

    if st.button("Send", key="chat_send_btn") and new_message.strip():
        chat_data.append({"user": st.session_state.mobile, "message": new_message.strip()})
        with open(chat_path, "w") as f:
            json.dump(chat_data, f, indent=2)
        st.rerun()

# =================================================
# ✅ PAGE 2: CUTOFF CALCULATOR (FREE + PREMIUM)
# =================================================
elif selected == "Cutoff Calculator":
    from PIL import Image, ImageDraw, ImageFont
    from reportlab.pdfgen import canvas
    from reportlab.lib.pagesizes import A4

    st.markdown("## 📚 TNEA 2026 Cut off Mark Calculator")

    ist_time_str = datetime.now(ZoneInfo("Asia/Kolkata")).strftime("%d-%m-%Y %I:%M %p")

    def reset_marks():
        st.session_state.pop("student_name", None)
        st.session_state.pop("maths_mark", None)
        st.session_state.pop("physics_mark", None)
        st.session_state.pop("chemistry_mark", None)

    st.markdown("### ✍️ Enter Student Details")

    name = st.text_input("👤 Student Name", placeholder="Enter your name", key="student_name")

    col1, col2, col3 = st.columns(3)
    with col1:
        maths = st.text_input("✏️ Maths", placeholder="Enter Maths mark", key="maths_mark")
    with col2:
        physics = st.text_input("⚡ Physics", placeholder="Enter Physics mark", key="physics_mark")
    with col3:
        chemistry = st.text_input("🧪 Chemistry", placeholder="Enter Chemistry mark", key="chemistry_mark")

    b1, b2 = st.columns([1, 1])
    with b1:
        calc_btn = st.button("✅ Calculate Cutoff", key="calc_cutoff_btn")
    with b2:
        st.button("🔄 Reset", on_click=reset_marks, key="reset_cutoff_btn")

    def generate_pdf(student_name, maths_val, physics_val, chemistry_val, cutoff_val):
        buffer = io.BytesIO()
        c = canvas.Canvas(buffer, pagesize=A4)
        width, height = A4

        c.setFont("Helvetica-Bold", 18)
        c.drawString(50, height - 70, "TNEA Cutoff Mark Result (2026)")

        c.setFont("Helvetica", 12)
        c.drawString(50, height - 110, f"Name: {student_name}")
        c.drawString(50, height - 130, f"Date & Time (IST): {ist_time_str}")

        c.line(50, height - 150, 550, height - 150)

        c.setFont("Helvetica-Bold", 13)
        c.drawString(50, height - 190, "Marks Details:")

        c.setFont("Helvetica", 12)
        c.drawString(50, height - 220, f"Maths: {maths_val:.2f} / 100")
        c.drawString(50, height - 245, f"Physics: {physics_val:.2f} / 100  →  {physics_val/2:.2f} / 50")
        c.drawString(50, height - 270, f"Chemistry: {chemistry_val:.2f} / 100  →  {chemistry_val/2:.2f} / 50")

        c.setFont("Helvetica-Bold", 16)
        c.drawString(50, height - 320, f"Final Cutoff: {cutoff_val:.2f} / 200")

        c.showPage()
        c.save()
        buffer.seek(0)
        return buffer

    def generate_image(student_name, maths_val, physics_val, chemistry_val, cutoff_val):
        img = Image.new("RGB", (900, 520), "white")
        draw = ImageDraw.Draw(img)

        try:
            font_title = ImageFont.truetype("arial.ttf", 36)
            font_text = ImageFont.truetype("arial.ttf", 22)
        except:
            font_title = ImageFont.load_default()
            font_text = ImageFont.load_default()

        draw.text((30, 20), "TNEA Cutoff Mark Result (2026)", font=font_title, fill="black")
        draw.text((30, 90), f"Name: {student_name}", font=font_text, fill="black")
        draw.text((30, 120), f"Date & Time (IST): {ist_time_str}", font=font_text, fill="black")

        draw.line((30, 160, 870, 160), fill="black", width=2)

        draw.text((30, 190), f"Maths: {maths_val:.2f} / 100", font=font_text, fill="black")
        draw.text((30, 230), f"Physics: {physics_val:.2f} / 100  →  {physics_val/2:.2f} / 50", font=font_text, fill="black")
        draw.text((30, 270), f"Chemistry: {chemistry_val:.2f} / 100  →  {chemistry_val/2:.2f} / 50", font=font_text, fill="black")

        draw.line((30, 320, 870, 320), fill="black", width=2)
        draw.text((30, 350), f"Final Cutoff: {cutoff_val:.2f} / 200", font=font_title, fill="black")

        buffer = io.BytesIO()
        img.save(buffer, format="PNG")
        buffer.seek(0)
        return buffer

    if calc_btn:
        try:
            if name.strip() == "":
                st.error("❌ Please enter Student Name.")
            else:
                maths_val = float(maths)
                physics_val = float(physics)
                chemistry_val = float(chemistry)

                if not (0 <= maths_val <= 100 and 0 <= physics_val <= 100 and 0 <= chemistry_val <= 100):
                    st.error("❌ Please enter marks between 0 and 100 only.")
                else:
                    cutoff_val = maths_val + (physics_val / 2) + (chemistry_val / 2)

                    st.success(f"🎯 {name} - Your TNEA Cutoff Mark is: **{cutoff_val:.2f} / 200**")
                    st.caption(f"🕒 Generated Time (IST): {ist_time_str}")

                    st.markdown("### 📥 Download Result")

                    pdf_file = generate_pdf(name, maths_val, physics_val, chemistry_val, cutoff_val)
                    img_file = generate_image(name, maths_val, physics_val, chemistry_val, cutoff_val)

                    d1, d2 = st.columns(2)
                    with d1:
                        st.download_button(
                            "⬇️ Download PDF",
                            data=pdf_file,
                            file_name=f"TNEA_Cutoff_2026_{name.replace(' ', '_')}.pdf",
                            mime="application/pdf"
                        )
                    with d2:
                        st.download_button(
                            "⬇️ Download Image (PNG)",
                            data=img_file,
                            file_name=f"TNEA_Cutoff_2026_{name.replace(' ', '_')}.png",
                            mime="image/png"
                        )
        except:
            st.error("❌ Please enter valid numbers in Maths / Physics / Chemistry.")



elif selected == "College List":

    st.markdown("## 🏫 Tamil Nadu College List (Free)")
    st.caption("Search colleges and open official websites ✅")

    college_data = [
        {"College": "Madras Institute of Technology (MIT)", "City": "Chennai", "Website": "https://mitindia.edu/"},
        {"College": "College of Engineering Guindy (CEG)", "City": "Chennai", "Website": "https://ceg.annauniv.edu/"},
        {"College": "Alagappa College of Technology (ACT)", "City": "Chennai", "Website": "https://www.annauniv.edu/"},
        {"College": "Anna University Regional Campus Coimbatore", "City": "Coimbatore", "Website": "https://www.aurcc.ac.in/"},
        {"College": "Anna University Regional Campus Tirunelveli", "City": "Tirunelveli", "Website": "https://www.auttvl.ac.in/"},
        {"College": "PSG College of Technology", "City": "Coimbatore", "Website": "https://www.psgtech.edu/"},
        {"College": "Coimbatore Institute of Technology (CIT)", "City": "Coimbatore", "Website": "https://www.cit.edu.in/"},
        {"College": "Government College of Technology (GCT)", "City": "Coimbatore", "Website": "https://www.gct.ac.in/"},
        {"College": "Thiagarajar College of Engineering (TCE)", "City": "Madurai", "Website": "https://www.tce.edu/"},
        {"College": "SSN College of Engineering", "City": "Chennai", "Website": "https://www.ssn.edu.in/"},
        {"College": "SRM Institute of Science and Technology", "City": "Chennai", "Website": "https://www.srmist.edu.in/"},
        {"College": "VIT Vellore", "City": "Vellore", "Website": "https://vit.ac.in/"},
        {"College": "SASTRA Deemed University", "City": "Thanjavur", "Website": "https://www.sastra.edu/"},
        {"College": "Kumaraguru College of Technology", "City": "Coimbatore", "Website": "https://www.kct.ac.in/"},
        {"College": "Kongu Engineering College", "City": "Erode", "Website": "https://kongu.ac.in/"},
        {"College": "Rajalakshmi Engineering College", "City": "Chennai", "Website": "https://www.rajalakshmi.org/"},
    ]

    df_colleges = pd.DataFrame(college_data)

    colS1, colS2 = st.columns([2, 1])

    with colS1:
        search_text = st.text_input("🔍 Search College", placeholder="Type college name...")

    with colS2:
        city_list = ["All"] + sorted(df_colleges["City"].unique().tolist())
        selected_city = st.selectbox("📍 Filter by City", city_list)

    filtered_df = df_colleges.copy()

    if selected_city != "All":
        filtered_df = filtered_df[filtered_df["City"] == selected_city]

    if search_text.strip():
        filtered_df = filtered_df[filtered_df["College"].str.contains(search_text, case=False, na=False)]

    st.write(f"✅ Total Colleges Found: **{len(filtered_df)}**")

    st.markdown("---")

    for i, row in filtered_df.iterrows():
        with st.container():
            st.markdown(f"### 🏫 {row['College']}")
            st.write(f"📍 City: **{row['City']}**")
            st.link_button("🌐 Open Official Website", row["Website"])
            st.markdown("---")

# =================================================
# ✅ PAGE 3: CHOICE LIST (PREMIUM)
# =================================================
elif selected == "Create TNEA Choice List":
    st.title("📊 TNEA 2025 Cutoff & Rank Finder")
    st.success("✅ Premium Feature Enabled ✅")
    st.info("👉 Paste your full Choice List code here ✅")

# =================================================
# ✅ PAGE 4: SEAT MATRIX (PREMIUM)
# =================================================
elif selected == "TNEA Vacancy Seat Matrix":
    st.title("📊 TNEA Vacancy Seat Matrix")
    st.success("✅ Premium Feature Enabled ✅")
    st.info("👉 Paste your full Seat Matrix code here ✅")


    # --- MAIN FILTERED DATA ---
    show_data = False
    filtered_df = df.copy()

    if selected_college != "All":
        show_data = True
        selected_cl = selected_college.split(" - ")[0].strip()
        filtered_df = filtered_df[filtered_df['CL'].astype(str) == selected_cl]
    else:
        if 'zone' in locals() and zone != "All":
            filtered_df = filtered_df[filtered_df['zone'] == zone]
            show_data = True
        if 'department' in locals() and department != "All":
            filtered_df = filtered_df[filtered_df['Br'] == department]
            show_data = True

    if selected_college == "All" and 'community' in locals() and community != "All":
        cols_to_show = ['CL', 'College', 'Br', f'{community}_C', f'{community}_GR', 'zone']
    else:
        cols_to_show = ['CL', 'College', 'Br', 'zone'] + [col for col in df.columns if col.endswith("_C") or col.endswith("_GR")]

    format_dict = {
        col: '{:.2f}' if '_C' in col else '{:.0f}'
        for col in cols_to_show
        if '_C' in col or '_GR' in col
    }

    st.markdown("### 🔎 Filtered Results")
    if show_data:
        st.dataframe(
            filtered_df[cols_to_show]
            .style
            .format(format_dict)
            .hide(axis='index'),
            height=600
        )
    else:
        st.info("Please apply filters to see the results.")


# --- PAGE 3: TNEA VACANCY SEAT MATRIX ---
elif selected == "TNEA Vacancy Seat Matrix":
    import plotly.express as px
    from openpyxl import load_workbook
    import requests
    import io

    # ✅ All Google Sheet URLs
    excel_urls = {
        "Round 1": "https://docs.google.com/spreadsheets/d/17otzGFO0AhKzx5ChSUhW18HnqA8Ed2sY/export?format=xlsx",
        "Round 2": "https://docs.google.com/spreadsheets/d/1H1pLjbsvaOl1UMBAJbtfWz1B-KZQ24iB/export?format=xlsx",
        "Round 3": "https://docs.google.com/spreadsheets/d/1VPfuYg6cNtm_x4gnGkEndssR8CqfCDJT/export?format=xlsx",
        "Supplymentry_Counselling": "https://docs.google.com/spreadsheets/d/1NEf4pHVjO1m0Lz1g3Lua3emXT39opYbV/export?format=xlsx",
        "After_Supplymentry_Counselling": "https://docs.google.com/spreadsheets/d/1qnsPSyCd-myYnsOcF8vv_H-gPwn6psL8/export?format=xlsx",
        "After_SCA_to_SC": "https://docs.google.com/spreadsheets/d/1yqCtM98OC0GJSaAt-gbcVy8eTcWKc5pD/export?format=xlsx",
    }

    @st.cache_data(ttl=600)
    def load_all_rounds():
        all_data = {}
        for round_name, excel_url in excel_urls.items():
            try:
                response = requests.get(excel_url)
                excel_file = io.BytesIO(response.content)
                wb = load_workbook(excel_file, data_only=True)

                data_dict = {}
                for sheet in wb.sheetnames:
                    ws = wb[sheet]
                    data = list(ws.values)
                    if not data:
                        continue
                    header = data[0]
                    rows = data[1:]
                    df = pd.DataFrame(rows, columns=header)
                    data_dict[sheet] = df

                all_data[round_name] = data_dict
            except Exception as e:
                st.error(f"⚠️ Error loading {round_name}: {e}")
        return all_data

    all_rounds_data = load_all_rounds()

    community_cols = ['OC', 'BC', 'BCM', 'MBC', 'SC', 'SCA', 'ST']
    required_id_vars = ['College Name', 'College Code', 'Branch Code', 'Branch Name']

    # ----------------------------- CATEGORY 1 -----------------------------
    st.markdown("## 📂 Select Round, Branch and Community")
    col_cat1_0, col_cat1_1, col_cat1_2, col_cat1_3 = st.columns(4)

    with col_cat1_0:
        selected_round_1 = st.selectbox("📂 Select Counselling Round", list(all_rounds_data.keys()), key="cat1_round")

    with col_cat1_1:
        selected_sheet_1 = st.selectbox("📂 Select Vacancy - Category", list(all_rounds_data[selected_round_1].keys()), key="cat1_sheet")
        df1 = all_rounds_data[selected_round_1][selected_sheet_1]

    if df1.empty:
        st.error("❌ No data found in the selected sheet.")
        st.stop()

    # ✅ Clean dataframe
    df1.columns = [str(col).strip().upper().replace("  ", " ").replace("\n", " ") for col in df1.columns]
    rename_map = {}
    for col in df1.columns:
        if "COLLEGE CODE" in col:
            rename_map[col] = 'College Code'
        elif "COLLEGE NAME" in col:
            rename_map[col] = 'College Name'
        elif "BRANCH CODE" in col:
            rename_map[col] = 'Branch Code'
        elif "BRANCH NAME" in col:
            rename_map[col] = 'Branch Name'

    df1.rename(columns=rename_map, inplace=True)
    df1 = df1[[col for col in df1.columns if col in required_id_vars + community_cols]]
    df1[community_cols] = df1[community_cols].apply(pd.to_numeric, errors='coerce').fillna(0).astype(int)

    # ✅ Total Seats (Round-wise)
    total_round_seats = df1[community_cols].sum().sum()

    # ✅ Total per Branch
    branch_totals = df1.groupby("Branch Code")[community_cols].sum()
    branch_totals["Total Vacant"] = branch_totals.sum(axis=1)

    # Show metrics at top
    st.metric(label=f"🎯 Total Seats in {selected_round_1}", value=f"{total_round_seats:,}")

    # Optional: show branch summary as table
    with st.expander("📊 Branch-wise Vacancy Summary"):
        st.dataframe(branch_totals.reset_index(), use_container_width=True)

    # ----------------- Filters -----------------
    with col_cat1_2:
        branch_codes = sorted(df1['Branch Code'].dropna().unique())
        selected_branch_1 = st.selectbox("🔍 Select Branch Code", ['All'] + branch_codes)

    with col_cat1_3:
        selected_community_1 = st.selectbox("🧑‍🤝‍🧑 Select Community", ['All'] + community_cols)

    if selected_branch_1 == 'All':
        branch_df = df1.copy()
    else:
        branch_df = df1[df1['Branch Code'] == selected_branch_1].copy()

    if selected_community_1 == 'All':
        branch_df['Total Seats (All Communities)'] = branch_df[community_cols].sum(axis=1)
        branch_df = branch_df[[*required_id_vars, 'Total Seats (All Communities)']]
    else:
        branch_df = branch_df[[*required_id_vars, selected_community_1]]
        branch_df = branch_df.rename(columns={selected_community_1: 'Selected Community Seats'})
        branch_df.insert(4, 'Selected Community', selected_community_1)

    if not branch_df.empty:
        title_text = f"📘 Round: {selected_round_1} | Branch: {selected_branch_1} | Community: {selected_community_1}"
        st.header(title_text)
        st.dataframe(branch_df, use_container_width=True)

        if selected_branch_1 != 'All':
            bar1 = df1[df1['Branch Code'] == selected_branch_1]
            community_summary = bar1[community_cols].sum().reset_index()
            community_summary.columns = ['Community', 'Seats']

            # ✅ Calculate total seats for this branch
            total_branch_seats = community_summary['Seats'].sum()

            # ✅ Add total seats info in chart title
            chart_title = (
                f"{selected_round_1} - {selected_sheet_1} - {selected_branch_1} "
                f"- Total Seats Across Communities (Total = {total_branch_seats:,})"
            )

            fig1 = px.bar(
                community_summary, x='Community', y='Seats', color='Community', text='Seats',
                title=chart_title,
                labels={'Community': 'Community Category', 'Seats': 'Number of Seats'}, height=450
            )
            fig1.update_layout(xaxis_title="Community", yaxis_title="Number of Seats")
            fig1.update_traces(textposition='outside')
            st.plotly_chart(fig1, use_container_width=True)

    # ----------------------------- CATEGORY 2 -----------------------------
    st.markdown("---")
    st.markdown("## 🏧 Select Round, College and Branch")
    col_cat2_0, col_cat2_1, col_cat2_2, col_cat2_3 = st.columns(4)

    with col_cat2_0:
        selected_round_2 = st.selectbox("📂 Select Counselling Round", list(all_rounds_data.keys()), key="cat2_round")

    with col_cat2_1:
        selected_sheet_2 = st.selectbox("📂 Select Vacancy - Category", list(all_rounds_data[selected_round_2].keys()), key="cat2_sheet")
        df2 = all_rounds_data[selected_round_2][selected_sheet_2]

    if df2.empty:
        st.error("❌ No data found in the selected sheet.")
        st.stop()

    df2.columns = [str(col).strip().upper().replace("  ", " ").replace("\n", " ") for col in df2.columns]
    df2.rename(columns=rename_map, inplace=True)
    df2 = df2[[col for col in df2.columns if col in required_id_vars + community_cols]]
    df2[community_cols] = df2[community_cols].apply(pd.to_numeric, errors='coerce').fillna(0).astype(int)
    df2['College Combined'] = df2['College Code'].astype(str) + ' - ' + df2['College Name']

    unique_colleges = sorted(df2['College Combined'].dropna().unique())

    with col_cat2_2:
        selected_college_combined = st.selectbox("🏧 Select College (Code - Name)", ['All'] + unique_colleges)

    with col_cat2_3:
        branch_codes_2 = sorted(df2['Branch Code'].dropna().unique())
        selected_branch_code = st.selectbox("🔍 Filter by Branch Code (Optional)", ['All'] + branch_codes_2)

    selected_community_2 = st.selectbox("🧑‍🤝‍🧑 Select Community", ['All'] + community_cols, key="cat2_community")

    college_df = df2.copy()

    if selected_college_combined != "All":
        selected_code, selected_name = selected_college_combined.split(" - ", 1)
        college_df = college_df[
            (college_df['College Code'].astype(str) == selected_code.strip()) &
            (college_df['College Name'].str.strip() == selected_name.strip())
        ]

    if selected_branch_code != "All":
        college_df = college_df[college_df['Branch Code'] == selected_branch_code]

    # Chart 1: All Community Seats per Branch
    fig2_data_all = college_df.copy()
    fig2_data_all['Total Seats (All Communities)'] = fig2_data_all[community_cols].sum(axis=1)
    fig_all = px.bar(
        fig2_data_all,
        x='Branch Code', y='Total Seats (All Communities)', color='Branch Code',
        text='Total Seats (All Communities)',
        title=f"{selected_round_2} - {selected_college_combined} - Total Seats per Branch (All Communities)",
        labels={'Branch Code': 'Branch', 'Total Seats (All Communities)': 'Number of Seats'}, height=450
    )
    fig_all.update_layout(xaxis_title="Branch", yaxis_title="Number of Seats")
    fig_all.update_traces(textposition='outside')
    st.plotly_chart(fig_all, use_container_width=True)

    # Chart 2: Selected Community Seats per Branch
    if selected_community_2 != 'All':
        college_df = college_df[[*required_id_vars, selected_community_2]]
        college_df = college_df.rename(columns={selected_community_2: 'Selected Community Seats'})
        college_df.insert(4, 'Selected Community', selected_community_2)
        fig2 = px.bar(
            college_df,
            x='Branch Code', y='Selected Community Seats', color='Branch Code',
            text='Selected Community Seats',
            title=f"{selected_round_2} - {selected_college_combined} - {selected_community_2} Seats per Branch",
            labels={'Branch Code': 'Branch', 'Selected Community Seats': 'Number of Seats'}, height=450
        )
        fig2.update_layout(xaxis_title="Branch", yaxis_title="Number of Seats")
        fig2.update_traces(textposition='outside')
        st.plotly_chart(fig2, use_container_width=True)

    if college_df.empty:
        st.warning("⚠️ No data found for the selected college or branch.")


































