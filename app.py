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
        st.warning("⚠️ Session expired. Please log in again below.")

        # Inline Login Form
        st.markdown("### 🔐 Login Form")
        mobile = st.text_input("📱 Mobile Number", key="relogin_mobile")
        password = st.text_input("🔑 Password", type="password", key="relogin_pass")
        if st.button("Login Again"):
            if mobile in user_data and user_data[mobile]["password"] == password:
                existing = session_data["active_users"].get(mobile)
                if existing and existing["device_id"] != st.session_state.device_id and (time.time() - existing["timestamp"]) < SESSION_TIMEOUT:
                    st.error("⚠️ Already logged in on another device. Logout there first.")
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

# --- Login Form ---
if not st.session_state.logged_in:
    # 🔥 Offer Banner (before login title)
    st.markdown(
        """
        <div style='
            background-color: #e6f2ff;
            padding: 20px;
            border-left: 8px solid #007bff;
            border-radius: 10px;
            margin-bottom: 20px;
            box-shadow: 2px 2px 12px rgba(0,0,0,0.05);
            text-align: center;
        '>
            <h2 style='color: #d91c1c; font-weight: bold;'>🔥 Today Only Offer!</h2>
            <p style='font-size: 20px; font-weight: 600; color: #333;'>
                Get full access to the TNEA Web App for just <span style="color: green;">₹199</span> <br>
                <del>₹399</del> – <span style="color: orange;">Save ₹200 Now!</span><br><br>
                🕒 Limited Time Deal – Grab it before it's gone!
            </p>
            <p style='margin-top: 20px;'>
                <a href='https://wa.me/918248696926' target='_blank' style='
                    font-size: 24px;
                    color: #25D366;
                    font-weight: bold;
                    text-decoration: none;
                    display: inline-block;
                    margin-top: 10px;
                '>
                    📞 Chat on WhatsApp: 8248696926
                </a>
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )


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
    # 🔥 Offer Banner on Home Page
    st.markdown(
        """
        <div style='
            background-color: #e6f2ff;
            padding: 20px;
            border-left: 8px solid #007bff;
            border-radius: 10px;
            margin-bottom: 20px;
            box-shadow: 2px 2px 12px rgba(0,0,0,0.05);
            text-align: center;
        '>
            <h2 style='color: #d91c1c; font-weight: bold;'>🔥 Today Only Offer!</h2>
            <p style='font-size: 20px; font-weight: 600; color: #333;'>
                Get full access to the TNEA Web App for just <span style="color: green;">₹199</span> <br>
                <del>₹399</del> – <span style="color: orange;">Save ₹200 Now!</span><br><br>
                🕒 Limited Time Deal – Grab it before it's gone!
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )

    # 🎁 Referral Bonus Block
    st.markdown(
        """
        <div style='
            background-color: #fff3cd;
            border-left: 10px solid #ffc107;
            border-radius: 10px;
            padding: 20px 30px;
            margin: 20px auto;
            width: 95%;
            text-align: center;
            box-shadow: 0 4px 8px rgba(0,0,0,0.1);
        '>
            <h2 style='color: #b31b1b; font-weight: bold;'>🎁 Big Referral Bonus Alert!</h2>
            <p style='font-size: 18px; color: #333; font-weight: 500;'>
                💡 Sell this app to your friends, students, etc..<br><br>
                💰 <strong style="color:green;">Earn a referral bonus for each sale!</strong><br><br>
                🔁 No limits. More sales = More rewards!<br><br>
                📢 Start referring today and grow your earnings!
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )

    # Main Heading
    st.markdown(
        "<h1 style='text-align: center; font-weight: bold;'>📘 Welcome to TNEA Info Web App</h1>",
        unsafe_allow_html=True
    )

    # Feature Description
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

    @st.cache_data(ttl=600)
    def load_excel_sheets_safe():
        excel_url = "https://docs.google.com/spreadsheets/d/1H1pLjbsvaOl1UMBAJbtfWz1B-KZQ24iB/export?format=xlsx"
        response = requests.get(excel_url)
        excel_file = io.BytesIO(response.content)

        wb = load_workbook(excel_file, data_only=True)
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

    sheet_names, data_dict = load_excel_sheets_safe()

    community_cols = ['OC', 'BC', 'BCM', 'MBC', 'SC', 'SCA', 'ST']
    required_id_vars = ['College Name', 'College Code', 'Branch Code', 'Branch Name']

    # ----------------------------- CATEGORY 1 -----------------------------
    st.markdown("## 📂 Select Branch and Community")
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
    df1 = df1[[col for col in df1.columns if col in required_id_vars + community_cols]]
    df1[community_cols] = df1[community_cols].apply(pd.to_numeric, errors='coerce').fillna(0).astype(int)

    with col_cat1_2:
        branch_codes = sorted(df1['Branch Code'].dropna().unique())
        selected_branch_1 = st.selectbox("🔍 Select Branch Code", ['All'] + branch_codes, key="cat1_branch")

    with col_cat1_3:
        selected_community_1 = st.selectbox("🧑‍🤝‍👨 Select Community", ['All'] + community_cols, key="cat1_community")

    # Branch filter
    if selected_branch_1 == 'All':
        branch_df = df1.copy()
    else:
        branch_df = df1[df1['Branch Code'] == selected_branch_1].copy()

    # Community filter
    if selected_community_1 == 'All':
        branch_df = branch_df[[*required_id_vars, *community_cols]]
    else:
        branch_df = branch_df[[*required_id_vars, selected_community_1]]
        branch_df = branch_df.rename(columns={selected_community_1: 'Selected Community Seats'})
        branch_df.insert(4, 'Selected Community', selected_community_1)

    if not branch_df.empty:
        title_text = f"📘 Branch: {selected_branch_1} | Community: {selected_community_1}"
        st.header(title_text)
        st.dataframe(branch_df, use_container_width=True)

        # Download
        excel_buffer = io.BytesIO()
        branch_df.to_excel(excel_buffer, index=False, engine='openpyxl')
        excel_buffer.seek(0)

        file_name = (
            f"Branch_{selected_branch_1}_All_Seats.xlsx"
            if selected_community_1 == 'All'
            else f"Branch_{selected_branch_1}_{selected_community_1}_Seats.xlsx"
        )

        st.download_button(
            label="📥 Download Branch-wise Community Seats",
            data=excel_buffer,
            file_name=file_name,
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
    else:
        st.warning("⚠️ No data found for the selected branch/community.")

    # ----------------------------- CATEGORY 2 -----------------------------
    st.markdown("---")
    st.markdown("## 🏫 Select College and Branch")
    col2_1, col2_2, col2_3 = st.columns(3)

    with col2_1:
        selected_sheet_2 = st.selectbox("📂 Select Vacancy - Category", sheet_names, key="cat2_sheet")
        df2 = data_dict[selected_sheet_2]

    if df2.empty:
        st.error("❌ No data found in the selected sheet.")
        st.stop()

    df2.columns = [str(col).strip().upper().replace("  ", " ").replace("\n", " ") for col in df2.columns]
    df2.rename(columns=rename_map, inplace=True)
    df2 = df2[[col for col in df2.columns if col in required_id_vars + community_cols]]
    df2[community_cols] = df2[community_cols].apply(pd.to_numeric, errors='coerce').fillna(0).astype(int)
    df2['College Combined'] = df2['College Code'].astype(str) + ' - ' + df2['College Name']

    unique_colleges = sorted(df2['College Combined'].dropna().unique())

    with col2_2:
        selected_college_combined = st.selectbox("🏫 Select College (Code - Name)", ['All'] + unique_colleges, key="cat2_college")

    with col2_3:
        branch_codes_2 = sorted(df2['Branch Code'].dropna().unique())
        selected_branch_code = st.selectbox("🔍 Select Branch Code", ['All'] + branch_codes_2, key="cat2_branch")

    selected_community_2 = st.selectbox("🧑‍🤝‍👨 Select Community", ['All'] + community_cols, key="cat2_community")

    college_df = df2.copy()

    if selected_college_combined != "All":
        selected_code, selected_name = selected_college_combined.split(" - ", 1)
        college_df = college_df[
            (college_df['College Code'].astype(str) == selected_code.strip()) &
            (college_df['College Name'].str.strip() == selected_name.strip())
        ]

    if selected_branch_code != "All":
        college_df = college_df[college_df['Branch Code'] == selected_branch_code]

    if selected_community_2 == 'All':
        college_df['Total Seats (All Communities)'] = college_df[community_cols].sum(axis=1)
        y_col = 'Total Seats (All Communities)'
    else:
        college_df = college_df[[*required_id_vars, selected_community_2]]
        college_df = college_df.rename(columns={selected_community_2: 'Selected Community Seats'})
        college_df.insert(4, 'Selected Community', selected_community_2)
        y_col = 'Selected Community Seats'

    if not college_df.empty:
        st.subheader("🏫 College-wise Community Seat Distribution")
        st.dataframe(college_df, use_container_width=True)

        chart_title_1 = f"{y_col} across Branches in {selected_college_combined if selected_college_combined != 'All' else 'Selected Colleges'}"
        fig1 = px.bar(
            college_df,
            x='Branch Name',
            y=y_col,
            color='Branch Code',
            text=y_col,
            title=chart_title_1,
            height=450
        )
        fig1.update_traces(textposition='outside')
        st.plotly_chart(fig1, use_container_width=True)

        summary_df = df2.copy()
        if selected_college_combined != "All":
            summary_df = summary_df[
                (summary_df['College Code'].astype(str) == selected_code.strip()) &
                (summary_df['College Name'].str.strip() == selected_name.strip())
            ]

        if selected_branch_code != "All":
            summary_df = summary_df[summary_df['Branch Code'] == selected_branch_code]

        community_plot_df = summary_df.melt(id_vars=required_id_vars, value_vars=community_cols,
                                             var_name='Community', value_name='Seats')

        chart_title_2 = f"Community-wise Distribution in {selected_college_combined}"
        fig2 = px.bar(
            community_plot_df,
            x='Community',
            y='Seats',
            color='Community',
            text='Seats',
            title=chart_title_2,
            height=450
        )
        fig2.update_traces(textposition='outside')
        st.plotly_chart(fig2, use_container_width=True)

        excel_buffer2 = io.BytesIO()
        college_df.to_excel(excel_buffer2, index=False, engine='openpyxl')
        excel_buffer2.seek(0)

        fallback_code = college_df['College Code'].astype(str).iloc[0]
        fallback_comm = selected_community_2 if selected_community_2 != 'All' else 'All'
        file_name2 = f"College_{fallback_code}_{fallback_comm}_Seats.xlsx"

        st.download_button(
            label="📥 Download College-wise Community Seats",
            data=excel_buffer2,
            file_name=file_name2,
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
    else:
        st.warning("⚠️ No data found for the selected college or branch.")
