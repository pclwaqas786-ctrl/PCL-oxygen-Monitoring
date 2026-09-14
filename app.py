import streamlit as st
import pandas as pd
import datetime

# ---------------------------------------------------------
# 1. Page Configuration
# ---------------------------------------------------------
st.set_page_config(
    page_title="Pakistan Cable (CCR) - Oxygen Monitoring",
    page_icon="⚡",
    layout="wide"
)

# ---------------------------------------------------------
# 2. Session State Initialization
# ---------------------------------------------------------
if "logged_in_user" not in st.session_state:
    st.session_state.logged_in_user = None
if "user_role" not in st.session_state:
    st.session_state.user_role = None

if "monitoring_data" not in st.session_state:
    st.session_state.monitoring_data = {
        "Coil 1572": {"val": 249.0, "status": "SAFE ZONE", "color": "#00E676", "crit_low": 150.0, "safe_max": 500.0},
        "Coil 1573": {"val": 107.0, "status": "CRITICAL LOW ALERT", "color": "#FF2B2B", "crit_low": 150.0, "safe_max": 500.0},
        "Coil 1574": {"val": 577.0, "status": "CAUTION ZONE", "color": "#FF9100", "crit_low": 150.0, "safe_max": 500.0},
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
# 3. Simple Clean Styling
# ---------------------------------------------------------
st.markdown("""
<style>
.stApp { background-color: #0F172A; color: #FFFFFF; }
.main-title { font-size: 2rem; font-weight: 800; color: #FFFFFF; margin-bottom: 0px; }
.sub-title { font-size: 0.95rem; color: #94A3B8; margin-bottom: 20px; }
.metric-card { background-color: #1E293B; border: 1px solid #334155; border-radius: 10px; padding: 15px; text-align: center; color: white; margin-bottom: 10px; }
.metric-value { font-size: 2.2rem; font-weight: bold; margin: 8px 0; }
.status-badge { padding: 4px 10px; border-radius: 15px; font-size: 0.75rem; font-weight: bold; display: inline-block; }
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# 4. Sidebar Login
# ---------------------------------------------------------
st.sidebar.title("🔐 User Login")

if st.session_state.logged_in_user:
    st.sidebar.success(f"Logged in: **{st.session_state.logged_in_user}**")
    if st.sidebar.button("Logout", use_container_width=True):
        st.session_state.logged_in_user = None
        st.session_state.user_role = None
        st.rerun()
else:
    username_input = st.sidebar.text_input("Username").strip().lower()
    password_input = st.sidebar.text_input("Password", type="password")

    selected_shift = st.sidebar.selectbox("Select Duty Shift", ["Shift A (12 Hours)", "Shift B (12 Hours)"])

    if st.sidebar.button("Login", use_container_width=True):
        if username_input == "admin":
            st.session_state.logged_in_user = "Admin Manager"
            st.session_state.user_role = "admin"
            st.rerun()
        elif username_input in ["operator1", "operator2"]:
            st.session_state.logged_in_user = f"{username_input.upper()} ({selected_shift})"
            st.session_state.user_role = "operator"
            st.rerun()
        else:
            st.sidebar.error("Invalid Username or Password (use admin or operator1)")

# ---------------------------------------------------------
# 5. Header & Metric Cards
# ---------------------------------------------------------
st.markdown('<div class="main-title">Pakistan Cable (CCR) - Oxygen Monitoring</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-title">Real-time oxygen tracking system</div>', unsafe_allow_html=True)

cols = st.columns(len(st.session_state.monitoring_data))
for idx, (item, data) in enumerate(st.session_state.monitoring_data.items()):
    with cols[idx]:
        st.markdown(
            f"""
            <div class="metric-card">
                <div style="font-size:0.9rem; font-weight:600; color:#E2E8F0;">{item}</div>
                <div class="metric-value" style="color:{data['color']};">{data['val']} <span style="font-size:0.9rem;">ppm</span></div>
                <div class="status-badge" style="background-color:{data['color']}33; color:{data['color']}; border: 1px solid {data['color']};">
                    ● {data['status']}
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

# Simple Audio Alert
critical_items = [item for item, info in st.session_state.monitoring_data.items() if info['status'] == "CRITICAL LOW ALERT"]
if critical_items:
    st.error(f"🚨 **CRITICAL ALERT:** Low Oxygen Level detected on `{', '.join(critical_items)}`")
    st.markdown("""
        <audio controls autoplay loop style="width: 100%;">
          <source src="https://www.soundjay.com/buttons/sounds/beep-07.mp3" type="mp3">
          Your browser does not support audio.
        </audio>
    """, unsafe_allow_html=True)

st.markdown("---")

# ---------------------------------------------------------
# 6. Operations Panel
# ---------------------------------------------------------
st.subheader("📝 Operations Panel")

if not st.session_state.logged_in_user:
    st.info("🔒 Please log in from the sidebar to access data updates and settings.")
else:
    tab1, tab2 = st.tabs(["⚡ Update Values", "⚙️ Manage Coils"])
    
    with tab1:
        if st.session_state.user_role == "admin":
            st.info("Admin mode: Use Manage Coils tab to add/edit points.")
        else:
            with st.form("op_form"):
                sel_coil = st.selectbox("Select Coil", list(st.session_state.monitoring_data.keys()))
                val = st.number_input("Oxygen Value (ppm)", value=float(st.session_state.monitoring_data[sel_coil]['val']))
                if st.form_submit_button("Update Value"):
                    c_low = st.session_state.monitoring_data[sel_coil]['crit_low']
                    s_max = st.session_state.monitoring_data[sel_coil]['safe_max']
                    status, color = evaluate_status(val, c_low, s_max)
                    st.session_state.monitoring_data[sel_coil].update({"val": val, "status": status, "color": color})
                    st.success("Updated successfully!")
                    st.rerun()

    with tab2:
        if st.session_state.user_role != "admin":
            st.warning("Restricted to Admin.")
        else:
            with st.form("add_form"):
                new_name = st.text_input("New Coil Name")
                init_v = st.number_input("Initial Value", value=200.0)
                if st.form_submit_button("Add Coil") and new_name:
                    st.session_state.monitoring_data[new_name] = {"val": init_v, "status": "SAFE ZONE", "color": "#00E676", "crit_low": 150.0, "safe_max": 500.0}
                    st.success("Added!")
                    st.rerun()
