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
# 3. Custom CSS & High-Contrast Styling
# ---------------------------------------------------------
bg_style = ""
if st.session_state.bg_image:
    bg_style = f"""
    .stApp {{
        background: linear-gradient(rgba(15, 23, 42, 0.75), rgba(15, 23, 42, 0.75)), url("{st.session_state.bg_image}");
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
.metric-card {{ background-color: rgba(15, 23, 42, 0.92); border: 2px solid rgba(255,255,255,0.15); border-radius: 14px; padding: 20px; text-align: center; color: white; box-shadow: 0 8px 32px rgba(0,0,0,0.5); margin-bottom: 15px; }}
.metric-value {{ font-size: 2.5rem; font-weight: bold; margin: 10px 0; }}
.status-badge {{ padding: 6px 14px; border-radius: 20px; font-size: 0.85rem; font-weight: bold; display: inline-block; }}
.expander-box {{ background-color: rgba(30, 41, 59, 0.85); padding: 15px; border-radius: 10px; margin-bottom: 10px; border: 1px solid rgba(255,255,255,0.1); }}
</style>
"""

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
        st.sidebar.info("ℹ️ **Admin Mode:** Full management access.")
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
        st.sidebar.success("Wallpaper updated!")
        st.rerun()

# ---------------------------------------------------------
# 5. Header & Metric Cards
# ---------------------------------------------------------
st.markdown('<div class="main-title">Pakistan Cable (CCR)- Oxygen & Coil Monitoring</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-title">Real-time oxygen tracking system with individual coil thresholds and 24/7 logging.</div>', unsafe_allow_html=True)

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

# Critical Alarm & Direct Browser Sound Synthesis
critical_items = [item for item, info in st.session_state.monitoring_data.items() if info['status'] == "CRITICAL LOW ALERT"]
if critical_items:
    if st.session_state.logged_in_user:
        st.error(f"🚨 **CRITICAL EMERGENCY ALARM:** Low Oxygen Level detected on `{', '.join(critical_items)}`")
        
        # Built-in JavaScript Audio Beep Generator (Never fails, no external file needed)
        st.markdown("""
            <div style="background-color: rgba(255, 43, 43, 0.2); padding: 12px; border-radius: 8px; border: 1px solid #FF2B2B; margin-bottom: 15px;">
                <p style='color:#FF4B4B; font-weight:bold; font-size:1rem; margin-bottom: 8px;'>🔊 Emergency Siren Active!</p>
                <button onclick="
                    const ctx = new (window.AudioContext || window.webkitAudioContext)();
                    const osc = ctx.createOscillator();
                    const gain = ctx.createGain();
                    osc.type = 'square';
                    osc.frequency.value = 880;
                    osc.connect(gain);
                    gain.connect(ctx.destination);
                    osc.start();
                    setInterval(() => { osc.frequency.value = osc.frequency.value === 880 ? 587 : 880; }, 300);
                " style="background-color: #FF2B2B; color: white; border: none; padding: 8px 16px; border-radius: 5px; font-weight: bold; cursor: pointer;">
                    🔔 Click Here to Start Alarm Sound
                </button>
            </div>
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
        "⚙️ Edit Coils & Thresholds (Admin)", 
        "👥 User Management", 
        "📊 Audit Log History"
    ])

    with tab_update:
        if st.session_state.user_role == "admin":
            st.info("🚫 **Admin Notice:** Admin Manager cannot enter shift data. Use the 'Edit Coils & Thresholds' tab to manage items.")
        else:
            st.write(f"**Active Operator:** `{st.session_state.logged_in_user}`")
            with st.form("operator_entry_form"):
                selected_item = st.selectbox("Select Coil / Monitoring Point", list(st.session_state.monitoring_data.keys()))
                new_val = st.number_input("Oxygen Value (ppm)", min_value=0.0, max_value=2000.0, value=float(st.session_state.monitoring_data[selected_item]['val']), step=1.0, format="%.0f")
                
                submit_btn = st.form_submit_button("Submit & Sync Record")
                if submit_btn:
                    c_low = st.session_state.monitoring_data[selected_item]['crit_low']
                    s_max = st.session_state.monitoring_data[selected_item]['safe_max']
                    status, color = evaluate_status(new_val, c_low, s_max)
                    
                    st.session_state.monitoring_data[selected_item].update({"val": new_val, "status": status, "color": color})
                    st.success(f"Success! {selected_item} updated to {new_val} ppm ({status})")
                    st.rerun()

    with tab_settings:
        if st.session_state.user_role != "admin":
            st.warning("🔒 **Restricted Area:** Only Admin Manager can modify, add, or delete coil numbers and thresholds.")
        else:
            st.subheader("⚙️ Manage Coils & Threshold Limits")
            
            # Add New Coil Option
            with st.expander("➕ Add New Coil / Monitoring Point"):
                with st.form("add_coil_form"):
                    new_coil_name = st.text_input("Coil Number / Name (e.g., Coil 1575)")
                    init_val = st.number_input("Initial Oxygen Value (ppm)", value=250.0, step=1.0, format="%.0f")
                    c_limit = st.number_input("Critical Low Limit", value=150.0, step=1.0, format="%.0f")
                    s_limit = st.number_input("Safe Max Limit", value=500.0, step=1.0, format="%.0f")
                    add_btn = st.form_submit_button("Add New Coil")
                    if add_btn and new_coil_name:
                        status, color = evaluate_status(init_val, c_limit, s_limit)
                        st.session_state.monitoring_data[new_coil_name] = {
                            "val": init_val, "status": status, "color": color, "crit_low": c_limit, "safe_max": s_limit
                        }
                        st.success(f"Added {new_coil_name} successfully!")
                        st.rerun()

            st.markdown("---")
            st.write("✏️ **Edit or Delete Existing Coils:**")
            
            items_to_modify = list(st.session_state.monitoring_data.keys())
            for item in items_to_modify:
                data = st.session_state.monitoring_data[item]
                with st.expander(f"📌 {item} (Current: {data['val']} ppm)"):
                    col1, col2 = st.columns(2)
                    with col1:
                        new_name = st.text_input("Rename Coil", value=item, key=f"rename_{item}")
                        e_val = st.number_input("Current Value", value=float(data['val']), key=f"set_val_{item}", step=1.0, format="%.0f")
                    with col2:
                        e_crit = st.number_input("Critical Low Limit", value=float(data['crit_low']), key=f"set_crit_{item}", step=1.0, format="%.0f")
                        e_safe = st.number_input("Safe Max Limit", value=float(data['safe_max']), key=f"set_safe_{item}", step=1.0, format="%.0f")
                    
                    b_col1, b_col2 = st.columns(2)
                    with b_col1:
                        if st.button(f"Save Changes", key=f"btn_save_{item}"):
                            new_status, new_color = evaluate_status(e_val, e_crit, e_safe)
                            if new_name != item:
                                st.session_state.monitoring_data[new_name] = st.session_state.monitoring_data.pop(item)
                                item = new_name
                            st.session_state.monitoring_data[item].update({
                                "val": e_val, "crit_low": e_crit, "safe_max": e_safe, "status": new_status, "color": new_color
                            })
                            st.success(f"Updated successfully!")
                            st.rerun()
                    with b_col2:
                        if st.button(f"🗑️ Delete Coil", key=f"btn_del_{item}"):
                            if len(st.session_state.monitoring_data) > 1:
                                del st.session_state.monitoring_data[item]
                                st.warning(f"Deleted {item}!")
                                st.rerun()
                            else:
                                st.error("Cannot delete the last remaining monitoring point.")

    with tab_users:
        users_df = pd.DataFrame([
            {"Username": "admin", "Name": "Admin Manager", "Role": "Admin", "Access": "Coil Management & Monitoring"},
            {"Username": "operator1", "Name": "Shift Operator 1", "Role": "Operator", "Access": "Shift Data Logging"},
            {"Username": "operator2", "Name": "Shift Operator 2", "Role": "Operator", "Access": "Shift Data Logging"}
        ])
        st.dataframe(users_df, use_container_width=True)

    with tab_logs:
        sample_logs = pd.DataFrame([
            {"Timestamp": str(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")), "User": "OPERATOR1", "Coil Name": "Coil 1572", "Oxygen Val": 249, "Status": "SAFE ZONE"},
            {"Timestamp": "2026-09-14 17:50:49", "User": "OPERATOR2", "Coil Name": "Coil 1573", "Oxygen Val": 107, "Status": "CRITICAL LOW ALERT"}
        ])
        st.dataframe(sample_logs, use_container_width=True)
