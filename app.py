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
# 3. Custom CSS & Wallpaper Styling
# ---------------------------------------------------------
bg_style = ""
if st.session_state.bg_image:
    bg_style = f"""
    .stApp {{
        background: linear-gradient(rgba(15, 23, 42, 0.82), rgba(15, 23, 42, 0.82)), url("{st.session_state.bg_image}");
        background-size: cover;
        background-position: center;
        background-attachment: fixed;
    }}
    """
else:
    bg_style = ".stApp { background-color: #0F172A; }"

custom_css = f"""
<style>
{bg_style}
.main-title {{ font-size: 2.2rem; font-weight: 800; color: #FFFFFF; margin-bottom: 0px; text-shadow: 0 2px 4px rgba(0,0,0,0.8); }}
.sub-title {{ font-size: 1rem; color: #E2E8F0; margin-bottom: 25px; font-weight: 500; text-shadow: 0 1px 2px rgba(0,0,0,0.8); }}
.metric-card {{ background-color: rgba(15, 23, 42, 0.95); border: 2px solid rgba(255,255,255,0.2); border-radius: 14px; padding: 20px; text-align: center; color: white; box-shadow: 0 8px 32px rgba(0,0,0,0.6); margin-bottom: 15px; }}
.metric-value {{ font-size: 2.5rem; font-weight: bold; margin: 10px 0; }}
.status-badge {{ padding: 6px 14px; border-radius: 20px; font-size: 0.85rem; font-weight: bold; display: inline-block; }}
</style>
"""

st.markdown(custom_css, unsafe_allow_html=True)

# ---------------------------------------------------------
# 4. Sidebar Controls, Logo & Wallpaper Upload
# ---------------------------------------------------------
st.sidebar.title("🔐 User Login & Controls")

if st.session_state.logged_in_user:
    st.sidebar.success(f"Logged in: **{st.session_state.logged_in_user}**")
    if st.sidebar.button("Logout", use_container_width=True):
        st.session_state.logged_in_user = None
        st.session_state.user_role = None
        st.rerun()
else:
    username_input = st.sidebar.text_input("Username", key="login_username").strip().lower()
    password_input = st.sidebar.text_input("Password", type="password", key="login_password")
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

st.sidebar.markdown("---")
st.sidebar.subheader("🎨 Customization Panel")

uploaded_logo = st.sidebar.file_uploader("Upload Company Logo", type=["png", "jpg", "jpeg"], key="logo_uploader")
if uploaded_logo is not None:
    st.session_state.logo_image = f"data:image/png;base64,{base64.b64encode(uploaded_logo.read()).decode()}"

if st.session_state.logo_image:
    st.sidebar.image(st.session_state.logo_image, width=140, caption="Company Logo")

uploaded_wallpaper = st.sidebar.file_uploader("Upload Background Wallpaper", type=["png", "jpg", "jpeg"], key="bg_uploader")
if uploaded_wallpaper is not None:
    st.session_state.bg_image = f"data:image/png;base64,{base64.b64encode(uploaded_wallpaper.read()).decode()}"
    st.rerun()

# ---------------------------------------------------------
# 5. Header with Logo & Metric Cards
# ---------------------------------------------------------
header_col1, header_col2 = st.columns([1, 10])
with header_col1:
    if st.session_state.logo_image:
        st.image(st.session_state.logo_image, width=90)
with header_col2:
    st.markdown('<div class="main-title">Pakistan Cable (CCR) - Oxygen & Coil Monitoring</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-title">Real-time oxygen tracking system with individual coil thresholds.</div>', unsafe_allow_html=True)

cols = st.columns(len(st.session_state.monitoring_data))
for idx, (item, data) in enumerate(st.session_state.monitoring_data.items()):
    with cols[idx]:
        st.markdown(
            f"""
            <div class="metric-card">
                <div style="font-size:0.95rem; font-weight:700; color:#FFFFFF;">{item}</div>
                <div class="metric-value" style="color:{data['color']};">{data['val']} <span style="font-size:1rem;">ppm</span></div>
                <div class="status-badge" style="background-color:{data['color']}33; color:{data['color']}; border: 1px solid {data['color']};">
                    ● {data['status']}
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

# Critical Alarm & 100% Working Built-in Browser Synthesizer Siren
critical_items = [item for item, info in st.session_state.monitoring_data.items() if info['status'] == "CRITICAL LOW ALERT"]
if critical_items:
    st.error(f"🚨 **CRITICAL EMERGENCY ALARM:** Low Oxygen Level detected on `{', '.join(critical_items)}`")
    
    st.markdown("""
        <div style="background-color: rgba(255, 43, 43, 0.25); padding: 18px; border-radius: 12px; border: 2px solid #FF2B2B; margin-bottom: 20px; text-align: center;">
            <p style='color:#FF4B4B; font-weight:bold; font-size:1.1rem; margin-bottom: 12px;'>🔊 Emergency Siren Active! Click button below to start alarm sound:</p>
            <button onclick="
                const audioCtx = new (window.AudioContext || window.webkitAudioContext)();
                if (audioCtx.state === 'suspended') { audioCtx.resume(); }
                const oscillator = audioCtx.createOscillator();
                const gainNode = audioCtx.createGain();
                oscillator.type = 'square';
                oscillator.frequency.setValueAtTime(880, audioCtx.currentTime);
                oscillator.connect(gainNode);
                gainNode.connect(audioCtx.destination);
                oscillator.start();
                window.sirenInterval = setInterval(() => {
                    oscillator.frequency.setValueAtTime(oscillator.frequency.value === 880 ? 587 : 880, audioCtx.currentTime);
                }, 300);
            " style="background-color: #FF2B2B; color: white; border: none; padding: 12px 24px; border-radius: 8px; font-weight: bold; font-size: 1rem; cursor: pointer; box-shadow: 0 4px 12px rgba(255,43,43,0.5);">
                🔔 Start Alarm Sound
            </button>
            <button onclick="if(window.sirenInterval) clearInterval(window.sirenInterval); location.reload();" style="background-color: #334155; color: white; border: none; padding: 12px 20px; border-radius: 8px; font-weight: bold; font-size: 1rem; cursor: pointer; margin-left: 10px;">
                🔕 Stop Alarm
            </button>
        </div>
    """, unsafe_allow_html=True)

st.markdown("---")

# ---------------------------------------------------------
# 6. Operations Panel
# ---------------------------------------------------------
st.subheader("📝 Operations Panel")

if not st.session_state.logged_in_user:
    st.info("🔒 **Access Locked:** Please log in from the sidebar using username `admin` or `operator1` to access management features.")
else:
    tab_update, tab_settings, tab_logs = st.tabs(["⚡ Update Values", "⚙️ Manage Coils (Admin)", "📊 Audit Logs"])

    with tab_update:
        if st.session_state.user_role == "admin":
            st.info("Admin Manager: Use the 'Manage Coils' tab to add or edit monitoring points.")
        else:
            with st.form("op_form"):
                sel_coil = st.selectbox("Select Coil", list(st.session_state.monitoring_data.keys()))
                val = st.number_input("Oxygen Value (ppm)", value=float(st.session_state.monitoring_data[sel_coil]['val']))
                if st.form_submit_button("Update Value"):
                    c_low = st.session_state.monitoring_data[sel_coil]['crit_low']
                    s_max = st.session_state.monitoring_data[sel_coil]['safe_max']
                    status, color = evaluate_status(val, c_low, s_max)
                    st.session_state.monitoring_data[sel_coil].update({"val": val, "status": status, "color": color})
                    st.success("Value updated successfully!")
                    st.rerun()

    with tab_settings:
        if st.session_state.user_role != "admin":
            st.warning("Restricted to Admin Manager only.")
        else:
            with st.form("add_form"):
                new_name = st.text_input("New Coil Name (e.g. Coil 1575)")
                init_v = st.number_input("Initial Oxygen Value", value=200.0)
                if st.form_submit_button("Add New Coil") and new_name:
                    st.session_state.monitoring_data[new_name] = {
                        "val": init_v, "status": "SAFE ZONE", "color": "#00E676", "crit_low": 150.0, "safe_max": 500.0
                    }
                    st.success(f"Added {new_name} successfully!")
                    st.rerun()

            st.markdown("---")
            st.write("✏️ **Edit or Delete Existing Coils:**")
            for item in list(st.session_state.monitoring_data.keys()):
                data = st.session_state.monitoring_data[item]
                with st.expander(f"📌 {item} (Current: {data['val']} ppm)"):
                    with st.form(f"edit_form_{item}"):
                        new_coil_name = st.text_input("Rename Coil", value=item)
                        new_val = st.number_input("Oxygen Value", value=float(data['val']))
                        c_limit = st.number_input("Critical Low Limit", value=float(data['crit_low']))
                        s_limit = st.number_input("Safe Max Limit", value=float(data['safe_max']))
                        
                        save_btn = st.form_submit_button("Save Changes")
                        if save_btn:
                            new_status, new_color = evaluate_status(new_val, c_limit, s_limit)
                            if new_coil_name != item:
                                st.session_state.monitoring_data[new_coil_name] = st.session_state.monitoring_data.pop(item)
                                item = new_coil_name
                            st.session_state.monitoring_data[item].update({
                                "val": new_val, "crit_low": c_limit, "safe_max": s_limit, "status": new_status, "color": new_color
                            })
                            st.success("Coil updated successfully!")
                            st.rerun()

    with tab_logs:
        sample_logs = pd.DataFrame([
            {"Timestamp": str(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")), "User": st.session_state.logged_in_user, "Action": "Dashboard Active"}
        ])
        st.dataframe(sample_logs, use_container_width=True)
