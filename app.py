import streamlit as st
import pandas as pd
import base64
import datetime

# ---------------------------------------------------------
# 1. Page Configuration
# ---------------------------------------------------------
st.set_page_config(page_title="Pakistan Cable (CCR) - Oxygen & Coil Monitoring", page_icon="⚡", layout="wide")

# ---------------------------------------------------------
# 2. Session State Initialization (With Thresholds)
# ---------------------------------------------------------
if "bg_image" not in st.session_state:
    st.session_state.bg_image = None
if "logged_in_user" not in st.session_state:
    st.session_state.logged_in_user = None
if "user_role" not in st.session_state:
    st.session_state.user_role = None

# Ab har item ke sath uski Safe/Critical limits bhi save hongi
if "monitoring_data" not in st.session_state:
    st.session_state.monitoring_data = {
        "CR-2002 (Top/Tail)": {"val": 249.0, "status": "SAFE ZONE", "color": "#00E676", "crit_low": 150.0, "safe_max": 500.0},
        "CR-1605 (Top End)": {"val": 107.0, "status": "CRITICAL LOW ALERT", "color": "#FF2B2B", "crit_low": 150.0, "safe_max": 500.0},
        "CR-2486 (Top End)": {"val": 577.0, "status": "CAUTION ZONE", "color": "#FF9100", "crit_low": 150.0, "safe_max": 500.0}
    }

# Function to evaluate status dynamically based on user-defined limits
def evaluate_status(val, crit_low, safe_max):
    if val < crit_low:
        return "CRITICAL LOW ALERT", "#FF2B2B"
    elif crit_low <= val <= safe_max:
        return "SAFE ZONE", "#00E676"
    else:
        return "CAUTION ZONE", "#FF9100"

# ---------------------------------------------------------
# 3. Dynamic Custom CSS
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
    bg_css = f"""<style>.stApp {{ background-image: url("{st.session_state.bg_image}"); background-size: cover; background-position: center; background-attachment: fixed; }} </style>"""
    st.markdown(bg_css, unsafe_allow_html=True)

st.markdown(custom_css, unsafe_allow_html=True)

# ---------------------------------------------------------
# 4. Sidebar Controls & Auth
# ---------------------------------------------------------
st.sidebar.title("🔐 User Login & Controls")

if st.session_state.logged_in_user:
    st.sidebar.success(f"Logged in as: **{st.session_state.logged_in_user}**")
    if st.sidebar.button("Logout", use_container_width=True):
        st.session_state.logged_in_user = None
        st.session_state.user_role = None
        st.rerun()
else:
    username_input = st.sidebar.text_input("Username").strip().lower()
    password_input = st.sidebar.text_input("Password", type="password")

    selected_shift = None
    if username_input == "admin":
        st.sidebar.info("ℹ️ **Admin Mode:** Viewing & Settings Allowed. Data Logging disabled.")
    else:
        selected_shift = st.sidebar.selectbox("Select Duty Shift", ["Shift A (12 Hours)", "Shift B (12 Hours)"])

    if st.sidebar.button("Login to Dashboard", use_container_width=True):
        if username_input == "admin":
            st.session_state.logged_in_user = "Admin Manager"
            st.session_state.user_role = "admin"
            st.rerun()
        elif username_input in ["operator1", "operator2"]:
            st.session_state.logged_in_user = f"{username_input.upper()} ({selected_shift})"
            st.session_state.user_role = "operator"
            st.rerun()
        else:
            st.sidebar.error("Invalid Username or Password")

# Background Wallpaper Uploader
st.sidebar.markdown("---")
uploaded_wallpaper = st.sidebar.file_uploader("Upload Background Wallpaper", type=["png", "jpg", "jpeg"])
if uploaded_wallpaper is not None:
    encoded_img = base64.b64encode(uploaded_wallpaper.read()).decode()
    st.session_state.bg_image = f"data:image/png;base64,{encoded_img}"
    st.sidebar.success("Wallpaper updated!")

# ---------------------------------------------------------
# 5. Dashboard Cards & Alarms
# ---------------------------------------------------------
st.markdown('<div class="main-title">Pakistan Cable (CCR)- Oxygen & Coil Monitoring</div>', unsafe_allow_html=True)

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
            """, unsafe_allow_html=True
        )

critical_items = [item for item, info in st.session_state.monitoring_data.items() if info['status'] == "CRITICAL LOW ALERT"]
if critical_items and st.session_state.logged_in_user:
    st.error(f"🚨 **CRITICAL EMERGENCY ALARM:** Low Oxygen Level on `{', '.join(critical_items)}`")
    if st.button("📢 START EMERGENCY SIREN ALARM 🔊", use_container_width=True):
        st.warning("Emergency Siren Alarm Activated!")

st.markdown("---")

# ---------------------------------------------------------
# 6. Operations Tabs
# ---------------------------------------------------------
tab_update, tab_manage = st.tabs(["⚡ Data Entry (Operators)", "⚙️ Edit Values & Thresholds (Admin/Settings)"])

# TAB 1: DATA ENTRY (Only Operators)
with tab_update:
    if not st.session_state.logged_in_user:
        st.warning("Please login to log data.")
    elif st.session_state.user_role == "admin":
        st.info("🚫 Admin can view and edit settings in the next tab, but cannot log daily shift data here.")
    elif st.session_state.user_role == "operator":
        with st.form("entry_form"):
            selected_item = st.selectbox("Select Point", list(st.session_state.monitoring_data.keys()))
            new_val = st.number_input("Oxygen Value (ppm)", value=250.0)
            if st.form_submit_button("Submit Data"):
                # Get dynamic thresholds
                c_low = st.session_state.monitoring_data[selected_item]['crit_low']
                s_max = st.session_state.monitoring_data[selected_item]['safe_max']
                status, color = evaluate_status(new_val, c_low, s_max)
                
                st.session_state.monitoring_data[selected_item].update({"val": new_val, "status": status, "color": color})
                st.success(f"Logged! {selected_item} is now {status}")
                st.rerun()

# TAB 2: EDIT VALUES & ZONES (Admin & Adjustments)
with tab_manage:
    if not st.session_state.logged_in_user:
        st.warning("Please login to manage settings.")
    else:
        st.write("Yahan se aap kisi bhi point ki value aur uski Safe Zone / Critical Zone ki limit edit kar sakte hain:")
        for item, data in st.session_state.monitoring_data.items():
            with st.expander(f"⚙️ Edit {item} Settings"):
                col1, col2, col3 = st.columns(3)
                edit_val = col1.number_input("Current Value", value=float(data['val']), key=f"val_{item}")
                edit_crit = col2.number_input("Critical Low Limit (Below this is Red)", value=float(data['crit_low']), key=f"crit_{item}")
                edit_safe = col3.number_input("Safe Max Limit (Above this is Orange)", value=float(data['safe_max']), key=f"safe_{item}")
                
                if st.button(f"Save Settings for {item}", key=f"save_{item}"):
                    new_status, new_color = evaluate_status(edit_val, edit_crit, edit_safe)
                    st.session_state.monitoring_data[item].update({
                        "val": edit_val, "crit_low": edit_crit, "safe_max": edit_safe, 
                        "status": new_status, "color": new_color
                    })
                    st.success("Settings updated successfully!")
                    st.rerun()
