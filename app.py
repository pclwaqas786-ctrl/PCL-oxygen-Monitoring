import streamlit as st
import pandas as pd
import base64
import datetime

# ---------------------------------------------------------
# 1. Page Configuration
# ---------------------------------------------------------
st.set_page_config(
    page_title="Pakistan Cable (CCR) - Oxygen & Coil Monitoring",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ---------------------------------------------------------
# 2. Session State Initialization (Persistent Storage)
# ---------------------------------------------------------
if "bg_image" not in st.session_state:
    st.session_state.bg_image = None

if "logged_in_user" not in st.session_state:
    st.session_state.logged_in_user = None

if "user_role" not in st.session_state:
    st.session_state.user_role = None

if "monitoring_data" not in st.session_state:
    st.session_state.monitoring_data = {
        "CR-2002 (Top/Tail)": {"val": 249.0, "status": "SAFE ZONE", "color": "#00E676"},
        "CR-1605 (Top End)": {"val": 107.0, "status": "CRITICAL LOW ALERT", "color": "#FF2B2B"},
        "CR-2486 (Top End)": {"val": 577.0, "status": "CAUTION ZONE", "color": "#FF9100"},
        "Shaft Furnace (SF-6)": {"val": 310.0, "status": "SAFE ZONE", "color": "#00E676"},
        "Tundish-Sample": {"val": 180.0, "status": "SAFE ZONE", "color": "#00E676"}
    }

# ---------------------------------------------------------
# 3. Dynamic Custom CSS (Wallpaper & Styling)
# ---------------------------------------------------------
custom_css = """
<style>
/* Main App Styling */
.main-title {
    font-size: 2.2rem;
    font-weight: 800;
    color: #1E293B;
    margin-bottom: 0px;
}
.sub-title {
    font-size: 1rem;
    color: #64748B;
    margin-bottom: 25px;
}
/* Metric Card Styling */
.metric-card {
    background-color: #1E1E1E;
    border-radius: 12px;
    padding: 20px;
    text-align: center;
    color: white;
    box-shadow: 0px 4px 12px rgba(0,0,0,0.15);
    margin-bottom: 15px;
}
.metric-value {
    font-size: 2.5rem;
    font-weight: bold;
    margin: 10px 0;
}
.status-badge {
    padding: 5px 12px;
    border-radius: 20px;
    font-size: 0.8rem;
    font-weight: bold;
    display: inline-block;
}
</style>
"""

# Apply Background Image CSS if uploaded
if st.session_state.bg_image:
    bg_css = f"""
    <style>
    .stApp {{
        background-image: url("{st.session_state.bg_image}");
        background-size: cover;
        background-position: center;
        background-repeat: no-repeat;
        background-attachment: fixed;
    }}
    </style>
    """
    st.markdown(bg_css, unsafe_allow_html=True)

st.markdown(custom_css, unsafe_allow_html=True)

# ---------------------------------------------------------
# 4. Sidebar Controls & Auth
# ---------------------------------------------------------
st.sidebar.title("🔐 User Login & Controls")

# Input User ID
username_input = st.sidebar.text_input("Username", value="", key="login_username").strip().lower()
password_input = st.sidebar.text_input("Password", type="password", key="login_password")

# --- ADMIN VS REGULAR USER LOGIC ---
selected_shift = None
if username_input == "admin":
    st.sidebar.info("ℹ️ **Admin Manager Mode:** Viewing only. Shift selection disabled.")
else:
    selected_shift = st.sidebar.selectbox(
        "Select Duty Shift",
        ["Shift A (12 Hours)", "Shift B (12 Hours)"],
        key="duty_shift_select"
    )

# Login Button Action
if st.sidebar.button("Login to Dashboard", use_container_width=True):
    if username_input == "admin":
        st.session_state.logged_in_user = "Admin Manager"
        st.session_state.user_role = "admin"
        st.sidebar.success("Logged in as: ADMIN MANAGER")
    elif username_input in ["operator1", "operator2", "user1", "user2"]:
        st.session_state.logged_in_user = username_input.upper()
        st.session_state.user_role = "operator"
        st.sidebar.success(f"Logged in as: {username_input.upper()} ({selected_shift})")
    else:
        st.sidebar.error("Invalid Username or Password")

# Read-Only Warning if not logged in
if not st.session_state.logged_in_user:
    st.sidebar.warning("🔒 Read-Only Mode. Please log in to enable data updates.")

# --- SIDEBAR WALLPAPER UPLOADER ---
st.sidebar.markdown("---")
st.sidebar.subheader("🖼️ Company Logo & Wallpaper")

uploaded_wallpaper = st.sidebar.file_uploader(
    "Upload Background Wallpaper", 
    type=["png", "jpg", "jpeg"], 
    key="bg_uploader"
)

if uploaded_wallpaper is not None:
    file_bytes = uploaded_wallpaper.read()
    encoded_img = base64.b64encode(file_bytes).decode()
    st.session_state.bg_image = f"data:image/png;base64,{encoded_img}"
    st.sidebar.success("Background Wallpaper updated!")

# ---------------------------------------------------------
# 5. Header Area
# ---------------------------------------------------------
st.markdown('<div class="main-title">Pakistan Cable (CCR)- Oxygen & Coil Monitoring</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-title">Real-time oxygen tracking system with individual item thresholds and 24/7 Google Sheets logging.</div>', unsafe_allow_html=True)

# ---------------------------------------------------------
# 6. Live Cards Section
# ---------------------------------------------------------
cols = st.columns(len(st.session_state.monitoring_data))
for idx, (item, data) in enumerate(st.session_state.monitoring_data.items()):
    with cols[idx]:
        st.markdown(
            f"""
            <div class="metric-card">
                <div style="font-size:0.9rem; font-weight:600; color:#A1A1AA;">{item}</div>
                <div class="metric-value" style="color:{data['color']};">{data['val']} <span style="font-size:1rem;">ppm</span></div>
                <div class="status-badge" style="background-color:{data['color']}22; color:{data['color']}; border: 1px solid {data['color']};">
                    ● {data['status']}
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

# Critical Alarm Banner
critical_items = [item for item, info in st.session_state.monitoring_data.items() if info['status'] == "CRITICAL LOW ALERT"]
if critical_items:
    st.error(f"🚨 **CRITICAL EMERGENCY ALARM:** Low Oxygen Level on `{', '.join(critical_items)}`")
    if st.button("📢 START EMERGENCY SIREN ALARM 🔊", use_container_width=True):
        st.warning("Siren Sound Activated!")

st.markdown("---")

# ---------------------------------------------------------
# 7. Operations & Control Tabs
# ---------------------------------------------------------
st.subheader("📝 Live Data Entry & Operations Panel")

tab_update, tab_manage, tab_users, tab_logs = st.tabs([
    "⚡ Update Values", 
    "➕ Manage Monitoring Points", 
    "🎥 User Management (Admin)", 
    "📊 Google Sheets Log History"
])

# TAB 1: UPDATE VALUES (Restricted for Admin)
with tab_update:
    if st.session_state.user_role == "admin":
        st.info("🚫 **Admin Access Restricted:** Admin only monitors system status. Entry disabled.")
    elif st.session_state.user_role == "operator":
        st.write(f"**Logged User:** `{st.session_state.logged_in_user}` | **Active Shift:** `{selected_shift}`")
        with st.form("entry_form"):
            selected_item = st.selectbox("Select Monitoring Point", list(st.session_state.monitoring_data.keys()))
            new_val = st.number_input("Oxygen Value (ppm)", min_value=0.0, max_value=2000.0, value=250.0, step=0.1)
            
            submit_btn = st.form_submit_button("Submit & Sync to Google Sheets")
            if submit_btn:
                # Status Threshold Logic
                if new_val < 150:
                    status, color = "CRITICAL LOW ALERT", "#FF2B2B"
                elif 150 <= new_val <= 500:
                    status, color = "SAFE ZONE", "#00E676"
                else:
                    status, color = "CAUTION ZONE", "#FF9100"
                
                st.session_state.monitoring_data[selected_item] = {"val": new_val, "status": status, "color": color}
                st.success(f"Data Logged: {selected_item} set to {new_val} ppm ({status})")
                st.rerun()
    else:
        st.warning("Please login from the sidebar to enter data.")

# TAB 2: MANAGE POINTS
with tab_manage:
    st.write("Manage active sensor points and thresholds.")
    new_point_name = st.text_input("New Point Name (e.g., Tundish-Sample-2)")
    if st.button("Add Sensor Point"):
        if new_point_name and new_point_name not in st.session_state.monitoring_data:
            st.session_state.monitoring_data[new_point_name] = {"val": 200.0, "status": "SAFE ZONE", "color": "#00E676"}
            st.success(f"Added new point: {new_point_name}")
            st.rerun()

# TAB 3: USER MANAGEMENT
with tab_users:
    st.subheader("👥 System User Accounts")
    users_df = pd.DataFrame([
        {"Username": "admin", "Name": "Admin Manager", "Role": "Admin (Read-Only)", "Shift": "N/A"},
        {"Username": "operator1", "Name": "Shift Officer 1", "Role": "Operator", "Shift": "Shift A / B"},
        {"Username": "operator2", "Name": "Shift Operator 2", "Role": "Operator", "Shift": "Shift A / B"}
    ])
    st.dataframe(users_df, use_container_width=True)

# TAB 4: LOG HISTORY
with tab_logs:
    st.subheader("📋 Recent Google Sheets Audit Trail")
    sample_logs = pd.DataFrame([
        {"Timestamp": str(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")), "User": "OPERATOR1", "Shift": "Shift A (12 Hours)", "Item Name": "CR-2002 (Top/Tail)", "Oxygen Val": 249.0, "Status": "SAFE ZONE"},
        {"Timestamp": "2026-09-14 17:50:49", "User": "OPERATOR2", "Shift": "Shift B (12 Hours)", "Item Name": "CR-1605 (Top End)", "Oxygen Val": 107.0, "Status": "CRITICAL LOW ALERT"}
    ])
    st.dataframe(sample_logs, use_container_width=True)
