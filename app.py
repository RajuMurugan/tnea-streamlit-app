import streamlit as st
from streamlit_option_menu import option_menu
import pandas as pd
import yaml
import requests
import io
import uuid
import time
from datetime import timedelta
import os
import plotly.express as px
from openpyxl import load_workbook
import random
import json

# --- Page Config ---
st.set_page_config(page_title="TNEA Full App", layout="wide")

# --- Style Settings ---
st.markdown("""
    <style>
    @media (max-width: 768px) {
        .nav-link span {
            display: inline !important;
        }
    }
    .stDataFrame div { color: black !important; }
    </style>
""", unsafe_allow_html=True)

# --- File Paths ---
base_path = "./"
config_path = base_path + "config.yaml"
device_session_path = base_path + "device_session.yaml"
chat_path = base_path + "chat_messages.json"

SESSION_TIMEOUT = 180  # 3 minutes

# --- Load Config ---
try:
    with open(config_path) as file:
        config = yaml.safe_load(file)
    user_data = config["credentials"]["users"]
except Exception as e:
    st.error(f"❌ Failed to load config.yaml: {e}")
    st.stop()

# --- Load or Init session.yaml ---
try:
    with open(device_session_path) as session_file:
        session_data = yaml.safe_load(session_file)
except Exception:
    session_data = {"active_users": {}}

# --- Load or Init chat messages ---
if not os.path.exists(chat_path):
    with open(chat_path, "w") as f:
        json.dump([], f)

def save_session():
    with open(device_session_path, "w") as f:
        yaml.dump(session_data, f)

def is_session_expired(mobile, device_id):
    user = session_data["active_users"].get(mobile, None)
    if not user:
        return True
    saved_device_id = user.get("device_id", "")
    timestamp = user.get("timestamp", 0)
    return saved_device_id != device_id or (time.time() - timestamp) > SESSION_TIMEOUT

def update_session(mobile, device_id):
    session_data["active_users"][mobile] = {
        "device_id": device_id,
        "timestamp": time.time()
    }
    save_session()

def logout_user():
    if st.session_state.mobile in session_data["active_users"]:
        session_data["active_users"].pop(st.session_state.mobile)
        save_session()
    st.session_state.logged_in = False
    st.session_state.mobile = ""
    st.session_state.device_id = str(uuid.uuid4())

# --- Init Session State ---
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "mobile" not in st.session_state:
    st.session_state.mobile = ""
if "device_id" not in st.session_state:
    st.session_state.device_id = str(uuid.uuid4())

# --- Login or Session Check ---
if st.session_state.logged_in:
    user = session_data["active_users"].get(st.session_state.mobile, {})
    last_time = user.get("timestamp", 0)
    remaining_time = max(0, SESSION_TIMEOUT - int(time.time() - last_time))

    if is_session_expired(st.session_state.mobile, st.session_state.device_id):
        logout_user()
        st.warning("⚠️ Session expired. Please log in again below.")

        # Login form again
        st.markdown("### 🔐 Login Form")
        mobile = st.text_input("📱 Mobile Number", key="relogin_mobile")
        password = st.text_input("🔑 Password", type="password", key="relogin_pass")
        if st.button("Login Again"):
            if mobile in user_data and user_data[mobile]["password"] == password:
                existing = session_data["active_users"].get(mobile)
                if existing and existing["device_id"] != st.session_state.device_id and (time.time() - existing["timestamp"]) < SESSION_TIMEOUT:
                    st.error("⚠️ Already logged in on another device.")
                else:
                    update_session(mobile, st.session_state.device_id)
                    st.session_state.logged_in = True
                    st.session_state.mobile = mobile
                    st.success(f"✅ Welcome back, {mobile}!")
                    st.rerun()
            else:
                st.error("❌ Invalid mobile number or password")
        st.stop()

    else:
        update_session(st.session_state.mobile, st.session_state.device_id)
        with st.expander("🔐 Session Info", expanded=False):
            st.info(f"⏳ Session expires in: {str(timedelta(seconds=remaining_time))}")
            st.success(f"👤 Logged in as: {st.session_state.mobile}")
            if st.button("🚪 Logout"):
                logout_user()
                st.rerun()

else:
    # --- Cut off Mark Calculation (Inside App) ---
    st.markdown("### 📚 TNEA Cut off Mark Calculation (Inside App)")

    with st.form("cutoff_form"):
        col1, col2, col3 = st.columns(3)

        with col1:
            maths = st.number_input(
                "✏️ Maths (0 - 100)",
                min_value=0.0, max_value=100.0, value=80.0, step=1.0
            )

        with col2:
            physics = st.number_input(
                "⚡ Physics (0 - 100)",
                min_value=0.0, max_value=100.0, value=70.0, step=1.0
            )

        with col3:
            chemistry = st.number_input(
                "🧪 Chemistry (0 - 100)",
                min_value=0.0, max_value=100.0, value=75.0, step=1.0
            )

        calc_btn = st.form_submit_button("✅ Calculate Cutoff")

    if calc_btn:
        cutoff = maths + (physics / 2) + (chemistry / 2)

        st.success(f"🎯 Your TNEA Cutoff Mark is: **{cutoff:.2f} / 200**")

        st.info(
            f"""
            ✅ Calculation Breakdown:
            - Maths = {maths:.2f} / 100
            - Physics = {physics:.2f} / 100 → {physics/2:.2f} / 50
            - Chemistry = {chemistry:.2f} / 100 → {chemistry/2:.2f} / 50
            """
        )

    # --- Quick Access to Previous Year Question Papers ---
    st.markdown("### 📚 Previous Year Question Papers")

    st.markdown("""
<div style='background-color: #f9f9f9; padding: 15px; border-left: 8px solid #4CAF50; border-radius: 10px; font-size: 16px;'>
📘 <a href='https://globaleduhub4u.blogspot.com/2025/03/anna-university-previous-year-questions.html' target='_blank' style='text-decoration: none; color: #007bff; font-weight: bold;'>Anna University Previous Year Question Papers</a><br>
📗 <a href='https://globaleduhub4u.blogspot.com/p/gate-previous-year-qps.html' target='_blank' style='text-decoration: none; color: #007bff; font-weight: bold;'>GATE Previous Year Question Papers</a><br>
📘 <a href='https://globaleduhub4u.blogspot.com/2025/03/numberiq.html' target='_blank' style='text-decoration: none; color: #007bff; font-weight: bold;'>Check Your Maths IQ</a><br>
</div>
    """, unsafe_allow_html=True)

    # --- Login Form ---
    st.title("🔐 Login to Access TNEA App")
    mobile = st.text_input("📱 Mobile Number")
    password = st.text_input("🔑 Password", type="password")

    if st.button("Login"):
        if mobile in user_data and user_data[mobile]["password"] == password:
            existing = session_data["active_users"].get(mobile)
            if existing and existing["device_id"] != st.session_state.device_id and (time.time() - existing["timestamp"]) < SESSION_TIMEOUT:
                st.error("⚠️ Already logged in on another device.")
                st.stop()

            update_session(mobile, st.session_state.device_id)
            st.session_state.logged_in = True
            st.session_state.mobile = mobile
            st.success(f"✅ Welcome, {mobile}!")
            st.rerun()
        else:
            st.error("❌ Invalid mobile number or password")

    st.stop()

# --- Navigation Bar ---
st.markdown("""
    <h2 style='text-align: center; color: #0d6efd; font-weight: bold;'>
        🔽 Select a Feature Below 🔽
    </h2>
""", unsafe_allow_html=True)

col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    selected = option_menu(
        menu_title=None,
        options=["Home", "Create TNEA Choice List", "TNEA Vacancy Seat Matrix"],
        icons=["house", "list-check", "table"],
        default_index=0,
        orientation="horizontal",
        styles={
            "container": {"padding": "0!important", "background-color": "#ffffff"},
            "icon": {"color": "#3399ff", "font-size": "18px"},
            "nav-link": {
                "font-size": "13px",
                "font-weight": "bold",
                "text-align": "center",
                "margin": "2px",
                "color": "#3399ff",
                "--hover-color": "#d0e7ff",
                "background-color": "#f4faff",
                "border-radius": "8px"
            },
            "nav-link-selected": {
                "background-color": "#0d6efd",
                "color": "white",
                "font-weight": "bold",
                "border-radius": "8px"
            }
        }
    )


# --- PAGE 1: HOME ---
if selected == "Home":
    st.markdown("""
        <h1 style='text-align: center; font-weight: bold;'>📘 Welcome to TNEA Info Web App</h1>
        <div style='text-align: center; font-size: 18px; margin-top: 20px;'>
            <b>✅ Create TNEA Choice List</b> – Filter colleges by cutoff, department, and community<br><br>
            <b>📊 TNEA Vacancy Seat Matrix</b> – Analyze vacant seats by branch, college, and community<br><br>
            📞 Contact: +91-8248696926<br>
            📧 Email: rajumurugannp@gmail.com<br>
            👨‍💻 Developed by Dr. Raju Murugan<br><br>
            &copy; 2025 TNEA Info App. All rights reserved.
        </div>
    """, unsafe_allow_html=True)

    # --- Chat Feature ---
    st.markdown("---")
    st.subheader("💬 Community Chat Room")

    with open(chat_path, "r") as f:
        chat_data = json.load(f)

    for entry in chat_data[-100:]:
        st.markdown(f"**{entry['user']}**: {entry['message']}")

    new_message = st.text_input("Type your message...")
    if st.button("Send") and new_message.strip():
        chat_data.append({"user": st.session_state.mobile, "message": new_message.strip()})
        with open(chat_path, "w") as f:
            json.dump(chat_data, f, indent=2)
        st.rerun()



# --- PAGE 2: TNEA CHOICE LIST ---
elif selected == "Create TNEA Choice List":

    import time

    # ✅ Performance-optimized loader with caching (10 minutes)
    @st.cache_data(ttl=600)
    def load_excel_file_from_url(url):
        response = requests.get(url)
        df_loaded = pd.read_excel(io.BytesIO(response.content))
        return df_loaded

    excel_url = "https://docs.google.com/spreadsheets/d/1rASGgYC9RZA0vgmtuFYRG0QO3DOGH_jW/export?format=xlsx"
    
    with st.spinner("📥 Loading TNEA cutoff data..."):
        df = load_excel_file_from_url(excel_url)

    for col in df.columns:
        if col.endswith("_C") or col.endswith("_GR"):
            df[col] = pd.to_numeric(df[col], errors="coerce")

    st.image("https://drive.google.com/thumbnail?id=1FPfkRH3BC1BeQRtQVpZDH3P3ilTSMYNA", width=100)
    st.title("📊 TNEA 2025 Cutoff & Rank Finder")
    st.markdown(f"🆔 **Accessed by: {st.session_state.mobile}**")

    df['College_Option'] = df['CL'].astype(str) + " - " + df['College']
    college_options = sorted(df['College_Option'].unique().tolist())
    selected_college = st.selectbox("🏛️ Select College", options=["All"] + college_options)

    st.subheader("🎯 Filter by Community, Department, Zone")
    if selected_college == "All":
        community = st.selectbox("Select Community", options=["All", "OC", "BC", "BCM", "MBC", "SC", "SCA", "ST"], key="main_community")
        department = st.selectbox("Select Department (Br)", options=["All"] + sorted(df['Br'].dropna().unique().tolist()))
        zone = st.selectbox("Select Zone", options=["All"] + sorted(df['zone'].dropna().unique().tolist()))

    st.subheader("📌 Compare Up to 5 Colleges")
    compare_colleges = st.multiselect("Select colleges to compare", options=college_options, max_selections=5)

    if compare_colleges:
        st.markdown("### 🎯 Filter Inside Compared Colleges")
        comp_dept = st.selectbox("Department", options=["All"] + sorted(df['Br'].dropna().unique().tolist()), key="compare_department")
        comp_comm = st.selectbox("Community", options=["All", "OC", "BC", "BCM", "MBC", "SC", "SCA", "ST"], key="compare_community")

        compare_cls = [c.split(" - ")[0].strip() for c in compare_colleges]
        compare_df = df[df['CL'].astype(str).isin(compare_cls)]

        if comp_dept != "All":
            compare_df = compare_df[compare_df['Br'] == comp_dept]

        color_palette = ['#f7c6c7', '#c6e2ff', '#d5f5e3', '#fff5ba', '#e0ccff']
        college_color_map = {cl: color_palette[i] for i, cl in enumerate(compare_cls)}

        def highlight_college(row):
            cl = str(row['CL'])
            bg_color = college_color_map.get(cl, '#ffffff')
            return [f'background-color: {bg_color}; color: black;' for _ in row]

        compare_cols = ['CL', 'College', 'Br', 'zone']
        if comp_comm != "All":
            compare_cols += [f"{comp_comm}_C", f"{comp_comm}_GR"]
        else:
            compare_cols += [col for col in df.columns if col.endswith("_C") or col.endswith("_GR")]

        format_dict = {col: '{:.2f}' if '_C' in col else '{:.0f}' for col in compare_cols if '_C' in col or '_GR' in col}

        st.markdown("### 🟨 College Comparison Table")
        st.dataframe(
            compare_df[compare_cols]
            .style
            .apply(highlight_college, axis=1)
            .format(format_dict)
            .hide(axis='index'),
            height=450
        )

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



