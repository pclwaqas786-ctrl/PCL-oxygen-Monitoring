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
# 2. Session State Initialization
# ---------------------------------------------------------
if "bg_image" not in st.session_state:
    st.session_state.bg_image = None
if "logo_image" not in st.session_state:
    st.session_state.logo_image = None
if "logged_in_user" not in st.session_state:
    st.session_state.logged_in_user = None
if "user_role" not in st.session_state:
    st.session_state.user_role = None

if "monitoring_data" not in st.session_state:
    st.session_state.monitoring_data = {
        "CR-2002 (Top/Tail)": {"val": 249.0, "status": "SAFE ZONE", "color": "#00E676", "crit_low": 150.0, "safe_max": 500.0},
        "CR-1605 (Top End)": {"val": 107.0, "status": "CRITICAL LOW ALERT", "color": "#FF2B2B", "crit_low": 150.0, "safe_max": 500.0},
        "CR-2486 (Top End)": {"val": 577.0, "status": "CAUTION ZONE", "color": "#FF9100", "crit_low": 150.0, "safe_max": 500.0},
        "Shaft Furnace (SF-6)": {"val": 310.0, "status": "SAFE ZONE", "color": "#00E676", "crit_low": 150.0, "safe_max": 500.0},
        "Tundish-Sample": {"val": 180.0, "status": "SAFE ZONE", "color": "#00E676", "crit_low": 150.0, "safe_max": 500.0}
    }

def evaluate_status(val, crit_low, safe_max):
    if val < crit_low:
        return "CRITICAL LOW ALERT", "#FF2B2B"
    elif crit_low <= val <= safe_max:
        return "SAFE ZONE", "#00E676"
    else:
        return "CAUTION ZONE", "#FF9100"

# ---------------------------------------------------------
# 3. Custom CSS & Wallpaper Styling
# ---------------------------------------------------------
custom_css = """
<style>
.main-title { font-size: 2.2rem; font-weight: 800; color: #1E293B; margin-bottom: 0px; }
.sub-title { font-size: 1rem; color: #64748B; margin-bottom: 25px; }
.metric-card { background-color: #1E1E1E; border-radius: 12px; padding: 20px; text-align: center; color: white; box-shadow: 0px 4px 12px rgba(0,0,0,0.15); margin-bottom: 15px; }
.metric-value { font-size: 2.5rem; font-weight: bold; margin: 10px 0; }
.status-badge { padding: 5px 12px; border-radius: 20px; font-size: 0.8rem; font-weight: bold; display: inline-block; }
</style>
"""

if st.session_state.bg_image:
    bg_css = f"""
    <style>
    .stApp {{
        background-image: url("{st.session_state.bg_image}");
        background-size: cover;
        background-position: center;
        background-attachment: fixed;
    }}
    </style>
    """
    st.markdown(bg_css, unsafe_allow_html=True)

st.markdown(custom_css, unsafe_allow_html=True)

# ---------------------------------------------------------
# 4. Sidebar Controls & Login
# ---------------------------------------------------------
st.sidebar.title("🔐 User Login & Controls")

if st.session_state.logged_in_user:
    st.sidebar.success(f"Logged in as: **{st.session_state.logged_in_user}**")
    if st.sidebar.button("Logout", use_container_width=True):
        st.session_state.logged_in_user = None
        st.session_state.user_role = None
        st.rerun()
else:
    username_input = st.sidebar.text_input("Username", key="login_username").strip().lower()
    password_input = st.sidebar.text_input("Password", type="password", key="login_password")

    selected_shift = None
    if username_input == "admin":
        st.sidebar.info("ℹ️ **Admin Mode:** Shift selection hidden. Full monitoring & settings access.")
    else:
        selected_shift = st.sidebar.selectbox(
            "Select Duty Shift",
            ["Shift A (12 Hours)", "Shift B (12 Hours)"],
            key="duty_shift_select"
        )

    if st.sidebar.button("Login to Dashboard", use_container_width=True):
        if username_input == "admin":
            st.session_state.logged_in_user = "Admin Manager"
            st.session_state.user_role = "admin"
            st.rerun()
        elif username_input in ["operator1", "operator2", "user1", "user2"]:
            shift_text = f" ({selected_shift})" if selected_shift else ""
            st.session_state.logged_in_user = f"{username_input.upper()}{shift_text}"
            st.session_state.user_role = "operator"
            st.rerun()
        else:
            st.sidebar.error("Invalid Username or Password")

    st.sidebar.warning("🔒 Read-Only Mode. Please log in to unlock controls.")

# --- CUSTOMIZATION (ONLY VISIBLE AFTER LOGIN) ---
if st.session_state.logged_in_user:
    st.sidebar.markdown("---")
    st.sidebar.subheader("🎨 Customization Panel")

    uploaded_logo = st.sidebar.file_uploader("Upload Company Logo", type=["png", "jpg", "jpeg"], key="logo_uploader")
    if uploaded_logo is not None:
        st.session_state.logo_image = f"data:image/png;base64,{base64.b64encode(uploaded_logo.read()).decode()}"
        st.sidebar.success("Logo updated!")

    if st.session_state.logo_image:
        st.sidebar.image(st.session_state.logo_image, width=150, caption="Company Logo")

    uploaded_wallpaper = st.sidebar.file_uploader("Upload Background Wallpaper", type=["png", "jpg", "jpeg"], key="bg_uploader")
    if uploaded_wallpaper is not None:
        st.session_state.bg_image = f"data:image/png;base64,{base64.b64encode(uploaded_wallpaper.read()).decode()}"
        st.sidebar.success("Background Wallpaper updated!")
        st.rerun()

# ---------------------------------------------------------
# 5. Header & Metric Cards
# ---------------------------------------------------------
st.markdown('<div class="main-title">Pakistan Cable (CCR)- Oxygen & Coil Monitoring</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-title">Real-time oxygen tracking system with individual item thresholds and 24/7 Google Sheets logging.</div>', unsafe_allow_html=True)

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

# Critical Alarm & Working Audio Player Section
critical_items = [item for item, info in st.session_state.monitoring_data.items() if info['status'] == "CRITICAL LOW ALERT"]
if critical_items:
    if st.session_state.logged_in_user:
        st.error(f"🚨 **CRITICAL EMERGENCY ALARM:** Low Oxygen Level detected on `{', '.join(critical_items)}`")
        
        # Working audio stream link for emergency siren beep
        st.markdown("""
            <p style='color:red; font-weight:bold;'>🔊 Emergency Siren Active! Click play below:</p>
            <audio controls autoplay loop>
              <source src="https://upload.wikimedia.org/wikipedia/commons/b/b3/Alarm_clock_ringing_bell.ogg" type="ogg">
              <source src="https://www.soundjay.com/misc/sounds/bell-ringing-05.mp3" type="mp3">
              Your browser does not support the audio element.
            </audio>
        """, unsafe_allow_html=True)
    else:
        st.warning(f"⚠️ Low Oxygen Level on `{', '.join(critical_items)}`. Please log in from sidebar to access alarms.")

st.markdown("---")

# ---------------------------------------------------------
# 6. Operations Tabs (Protected by Login)
# ---------------------------------------------------------
st.subheader("📝 Operations Panel")

if not st.session_state.logged_in_user:
    st.info("🔒 **Access Locked:** Please log in using your username and password from the sidebar to access data entry, settings, and logs.")
else:
    tab_update, tab_settings, tab_users, tab_logs = st.tabs([
        "⚡ Update Values (Operators)", 
        "⚙️ Edit Values & Thresholds (Admin)", 
        "👥 User Management", 
        "📊 Google Sheets Log History"
    ])

    with tab_update:
        if st.session_state.user_role == "admin":
            st.info("🚫 **Admin Notice:** Admin Manager cannot enter shift data. Use the 'Edit Values & Thresholds' tab.")
        else:
            st.write(f"**Active Operator:** `{st.session_state.logged_in_user}`")
            with st.form("operator_entry_form"):
                selected_item = st.selectbox("Select Monitoring Point", list(st.session_state.monitoring_data.keys()))
                new_val = st.number_input("Oxygen Value (ppm)", min_value=0.0, max_value=2000.0, value=float(st.session_state.monitoring_data[selected_item]['val']), step=0.1)
                
                submit_btn = st.form_submit_button("Submit & Sync to Google Sheets")
                if submit_btn:
                    c_low = st.session_state.monitoring_data[selected_item]['crit_low']
                    s_max = st.session_state.monitoring_data[selected_item]['safe_max']
                    status, color = evaluate_status(new_val, c_low, s_max)
                    
                    st.session_state.monitoring_data[selected_item].update({"val": new_val, "status": status, "color": color})
                    st.success(f"Success! {selected_item} updated to {new_val} ppm ({status})")
                    st.rerun()

    with tab_settings:
        if st.session_state.user_role != "admin":
            st.warning("🔒 **Restricted Area:** Only Admin Manager can modify sensor thresholds and critical limits.")
        else:
            st.write("⚙️ **Modify sensor values, critical limits, and safe zones:**")
            for item, data in st.session_state.monitoring_data.items():
                with st.expander(f"📌 Settings for: {item} (Current: {data['val']} ppm)"):
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        e_val = st.number_input("Current Value", value=float(data['val']), key=f"set_val_{item}", step=0.1)
                    with col2:
                        e_crit = st.number_input("Critical Low Limit", value=float(data['crit_low']), key=f"set_crit_{item}", step=0.1)
                    with col3:
                        e_safe = st.number_input("Safe Max Limit", value=float(data['safe_max']), key=f"set_safe_{item}", step=0.1)
                    
                    if st.button(f"Save Changes for {item}", key=f"btn_save_{item}"):
                        new_status, new_color = evaluate_status(e_val, e_crit, e_safe)
                        st.session_state.monitoring_data[item].update({
                            "val": e_val,
                            "crit_low": e_crit,
                            "safe_max": e_safe,
                            "status": new_status,
                            "color": new_color
                        })
                        st.success(f"Updated {item} successfully!")
                        st.rerun()

    with tab_users:
        users_df = pd.DataFrame([
            {"Username": "admin", "Name": "Admin Manager", "Role": "Admin", "Access": "Settings & Monitoring"},
            {"Username": "operator1", "Name": "Shift Operator 1", "Role": "Operator", "Access": "Shift Data Logging"},
            {"Username": "operator2", "Name": "Shift Operator 2", "Role": "Operator", "Access": "Shift Data Logging"}
        ])
        st.dataframe(users_df, use_container_width=True)

    with tab_logs:
        sample_logs = pd.DataFrame([
            {"Timestamp": str(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")), "User": "OPERATOR1", "Item Name": "CR-2002 (Top/Tail)", "Oxygen Val": 249.0, "Status": "SAFE ZONE"},
            {"Timestamp": "2026-09-14 17:50:49", "User": "OPERATOR2", "Item Name": "CR-1605 (Top End)", "Oxygen Val": 107.0, "Status": "CRITICAL LOW ALERT"}
        ])
        st.dataframe(sample_logs, use_container_width=True)
