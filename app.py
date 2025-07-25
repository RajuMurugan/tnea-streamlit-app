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

st.info("Last updated on: 25 July 2025")

# --- Page Config ---
st.set_page_config(page_title="TNEA Full App", layout="wide")

# --- Always show labels with icons (even on mobile) ---
st.markdown("""
    <style>
    @media (max-width: 768px) {
        .nav-link span {
            display: inline !important;
        }
    }
    </style>
""", unsafe_allow_html=True)

# --- Style for DataFrame text ---
st.markdown("""
    <style>
    .stDataFrame div { color: black !important; }
    </style>
""", unsafe_allow_html=True)

# --- File Paths ---
base_path = "./"
config_path = base_path + "config.yaml"
device_session_path = base_path + "device_session.yaml"

SESSION_TIMEOUT = 180  # 3 minutes

# --- Load config.yaml ---
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

# --- Session Check ---
if st.session_state.logged_in:
    user = session_data["active_users"].get(st.session_state.mobile, {})
    last_time = user.get("timestamp", 0)
    remaining_time = max(0, SESSION_TIMEOUT - int(time.time() - last_time))

    if is_session_expired(st.session_state.mobile, st.session_state.device_id):
        logout_user()
        st.warning("⚠️ Session expired. Please log in again.")
        st.stop()
    else:
        update_session(st.session_state.mobile, st.session_state.device_id)
        with st.expander("🔐 Session Info", expanded=False):
            st.info(f"⏳ Session expires in: {str(timedelta(seconds=remaining_time))}")
            st.success(f"👤 Logged in as: {st.session_state.mobile}")
            if st.button("🚪 Logout"):
                logout_user()
                st.rerun()

# --- Login Form ---
if not st.session_state.logged_in:
    st.title("🔐 Login to Access TNEA App")
    mobile = st.text_input("📱 Mobile Number")
    password = st.text_input("🔑 Password", type="password")
    if st.button("Login"):
        if mobile in user_data and user_data[mobile]["password"] == password:
            existing = session_data["active_users"].get(mobile)
            if existing and existing["device_id"] != st.session_state.device_id and (time.time() - existing["timestamp"]) < SESSION_TIMEOUT:
                st.error("⚠️ Already logged in on another device. Logout there first.")
                st.stop()
            update_session(mobile, st.session_state.device_id)
            st.session_state.logged_in = True
            st.session_state.mobile = mobile
            st.success(f"✅ Welcome, {mobile}!")
            st.rerun()
        else:
            st.error("❌ Invalid mobile number or password")
    st.stop()

# --- Navigation Title ---
st.markdown("""
    <h2 style='text-align: center; color: #0d6efd; font-weight: bold;'>
        🔽 Select a Feature Below 🔽
    </h2>
""", unsafe_allow_html=True)

# --- Option Menu (Mobile + Laptop Friendly) ---
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    selected = option_menu(
        menu_title=None,
        options=["Home", "Create TNEA Choice List", "TNEA Vacancy Seat Matrix"],
        icons=["house", "list-check", "table"],
        default_index=0,
        orientation="horizontal",
        styles={
            "container": {
                "padding": "0!important",
                "background-color": "#ffffff"
            },
            "icon": {
                "color": "#3399ff",
                "font-size": "18px"  # Slightly smaller icon
            },
            "nav-link": {
                "font-size": "13px",  # ✅ Reduced font size for mobile
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
    # --- Main Heading ---
    st.markdown(
        "<h1 style='text-align: center; font-weight: bold;'>📘 Welcome to TNEA Info Web App</h1>",
       
        unsafe_allow_html=True
    )

    # --- Feature Description ---
    st.markdown(
        """
        <div style='text-align: center; font-size: 18px; margin-top: 20px;'>
            <b>✅ Create TNEA Choice List</b> – Filter colleges by cutoff, department, and community<br><br>
            <b>📊 TNEA Vacancy Seat Matrix</b> – Analyze vacant seats by branch, college, and community<br><br>
            📞 Contact: +91-8248696926<br>
            📧 Email: rajumurugannp@gmail.com<br>
            👨‍💻 Developed by Dr. Raju Murugan<br><br>
            &copy; 2025 TNEA Info App. All rights reserved.
        </div>
        """,
        unsafe_allow_html=True
    )



# Add logic for other pages like "Create TNEA Choice List", etc. here if needed.


# --- PAGE 2: TNEA CHOICE LIST ---
elif selected == "Create TNEA Choice List":
    excel_url = "https://docs.google.com/spreadsheets/d/1rASGgYC9RZA0vgmtuFYRG0QO3DOGH_jW/export?format=xlsx"
    response = requests.get(excel_url)
    df = pd.read_excel(io.BytesIO(response.content))

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

    # ✅ Download Excel from Google Drive
    excel_url = "https://docs.google.com/spreadsheets/d/17otzGFO0AhKzx5ChSUhW18HnqA8Ed2sY/export?format=xlsx"
    response = requests.get(excel_url)
    excel_file = io.BytesIO(response.content)

    def load_excel_sheets_safe(file_bytes):
        wb = load_workbook(file_bytes, data_only=True)
        sheet_names = wb.sheetnames
        data_dict = {}

        for sheet in sheet_names:
            ws = wb[sheet]
            data = list(ws.values)
            if not data:
                continue
            header = data[0]
            rows = data[1:]
            df = pd.DataFrame(rows, columns=header)
            data_dict[sheet] = df

        return sheet_names, data_dict

    sheet_names, data_dict = load_excel_sheets_safe(excel_file)

    # ----------------------------- CATEGORY 1 -----------------------------
    st.markdown("## 🗂️ Select Branch and Community")
    col_cat1_1, col_cat1_2, col_cat1_3 = st.columns(3)

    with col_cat1_1:
        selected_sheet_1 = st.selectbox("📂 Select Vacancy - Category", sheet_names, key="cat1_sheet")
        df1 = data_dict[selected_sheet_1]

    if df1.empty:
        st.error("❌ No data found in the selected sheet.")
        st.stop()

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

    required_id_vars = ['College Name', 'College Code', 'Branch Code', 'Branch Name']
    community_cols = ['OC', 'BC', 'BCM', 'MBC', 'SC', 'SCA', 'ST']
    df1 = df1[[col for col in df1.columns if col in required_id_vars + community_cols]]
    df1_melted = df1.melt(id_vars=required_id_vars, value_vars=community_cols, var_name='Community', value_name='Seats')
    df1_melted['Seats'] = pd.to_numeric(df1_melted['Seats'], errors='coerce').fillna(0).astype(int)

    with col_cat1_2:
        branch_codes = sorted(df1_melted['Branch Code'].dropna().unique())
        selected_branch_1 = st.selectbox("🔍 Select Branch Code", branch_codes)

    with col_cat1_3:
        community_options = ['All'] + sorted(df1_melted['Community'].dropna().unique())
        selected_community_1 = st.selectbox("🧑‍🤝‍🧑 Filter by Community (Optional)", community_options)

    branch_df = df1_melted[df1_melted['Branch Code'] == selected_branch_1]
    if selected_community_1 != "All":
        branch_df = branch_df[branch_df['Community'] == selected_community_1]

    if not branch_df.empty:
        branch_name = branch_df['Branch Name'].iloc[0]
        st.header(f"📘 Summary for Branch: {selected_branch_1} - {branch_name}")
        summary_df = branch_df.groupby('Community')['Seats'].sum().reset_index().sort_values(by='Seats', ascending=False)
        total_seats = summary_df['Seats'].sum()
        summary_df.loc[len(summary_df.index)] = ['Total', total_seats]

        # ✅ Bar chart with values on top
        fig = px.bar(
            summary_df[summary_df['Community'] != 'Total'],
            x='Community',
            y='Seats',
            color='Community',
            title=f"Community-wise Seat Distribution (Total: {total_seats} seats)",
            labels={'Seats': 'Number of Seats'},
            text='Seats',
            height=450
        )
        fig.update_traces(textposition='outside')
        fig.update_layout(
            uniformtext_minsize=8,
            uniformtext_mode='show',
            margin=dict(t=50, b=40),
            yaxis=dict(title='Number of Seats', range=[0, summary_df['Seats'].max() * 1.25])
        )
        st.plotly_chart(fig, use_container_width=True)

        st.subheader("🧾 College-wise Seat Data")
        st.dataframe(branch_df, use_container_width=True)

        excel_buffer = io.BytesIO()
        branch_df.to_excel(excel_buffer, index=False, engine='openpyxl')
        excel_buffer.seek(0)

        st.download_button(
            label="📥 Download Branch Summary",
            data=excel_buffer,
            file_name=f"{selected_branch_1}_Community_Seats.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
    else:
        st.warning("⚠️ No data found for the selected branch/community.")

    # ----------------------------- CATEGORY 2 -----------------------------
    st.markdown("---")
    st.markdown("## 🏫 Select College and Branch")
    col_cat2_1, col_cat2_2, col_cat2_3 = st.columns(3)

    with col_cat2_1:
        selected_sheet_2 = st.selectbox("📂 Select Vacancy - Category", sheet_names, key="cat2_sheet")
        df2 = data_dict[selected_sheet_2]

    if df2.empty:
        st.error("❌ No data found in the selected sheet.")
        st.stop()

    df2.columns = [str(col).strip().upper().replace("  ", " ").replace("\n", " ") for col in df2.columns]
    df2.rename(columns=rename_map, inplace=True)

    df2 = df2[[col for col in df2.columns if col in required_id_vars + community_cols]]
    df2_melted = df2.melt(id_vars=required_id_vars, value_vars=community_cols, var_name='Community', value_name='Seats')
    df2_melted['Seats'] = pd.to_numeric(df2_melted['Seats'], errors='coerce').fillna(0).astype(int)
    df2_melted['College Combined'] = df2_melted['College Code'].astype(str) + ' - ' + df2_melted['College Name']
    unique_colleges = sorted(df2_melted['College Combined'].dropna().unique())

    with col_cat2_2:
        selected_college_combined = st.selectbox("🏫 Select College (Code - Name)", ['All'] + unique_colleges)

    with col_cat2_3:
        branch_codes_2 = sorted(df2_melted['Branch Code'].dropna().unique())
        selected_branch_code = st.selectbox("🔍 Filter by Branch Code (Optional)", ['All'] + branch_codes_2)

    selected_code, selected_name = "All", "All"
    college_df = df2_melted.copy()

    if selected_college_combined != "All":
        selected_code, selected_name = selected_college_combined.split(" - ", 1)
        college_df = college_df[
            (college_df['College Code'].astype(str) == selected_code.strip()) &
            (college_df['College Name'].str.strip() == selected_name.strip())
        ]

    if selected_branch_code != "All":
        college_df = college_df[college_df['Branch Code'] == selected_branch_code]

    if not college_df.empty:
        st.subheader("🏫 College-wise Community Seat Distribution")
        st.dataframe(college_df, use_container_width=True)

        summary2 = college_df.groupby('Community')['Seats'].sum().reset_index()
        total2 = summary2['Seats'].sum()
        summary2.loc[len(summary2.index)] = ['Total', total2]

        # ✅ Bar chart with values on top
        fig2 = px.bar(
            summary2[summary2['Community'] != 'Total'],
            x='Community',
            y='Seats',
            color='Community',
            title=f"Community-wise Seat Distribution for College (Total: {total2} seats)",
            labels={'Seats': 'Number of Seats'},
            text='Seats',
            height=450
        )
        fig2.update_traces(textposition='outside')
        fig2.update_layout(
            uniformtext_minsize=8,
            uniformtext_mode='show',
            margin=dict(t=50, b=40),
            yaxis=dict(title='Number of Seats', range=[0, summary2['Seats'].max() * 1.25])
        )
        st.plotly_chart(fig2, use_container_width=True)

        excel_buffer2 = io.BytesIO()
        college_df.to_excel(excel_buffer2, index=False, engine='openpyxl')
        excel_buffer2.seek(0)

        st.download_button(
            label="📥 Download College Summary",
            data=excel_buffer2,
            file_name=f"{selected_code.strip()}_{selected_name.strip().replace(' ', '_')}_Seats.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
    else:
        st.warning("⚠️ No data found for the selected college or branch.")
