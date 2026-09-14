import streamlit as st
import pandas as pd
import datetime
import base64
import json
import streamlit.components.v1 as components

st.set_page_config(
    page_title="Pakistan Cable (CCR) - Oxygen & Coil Monitoring",
    page_icon="🏭",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ---------------------------------------------------------
# GLOBAL SHARED STORE
# ---------------------------------------------------------
@st.cache_resource
def get_global_store():
    return {
        "app_title": "Pakistan Cable (CCR)- Oxygen & Coil Monitoring",
        "app_subtitle": "Real-time oxygen tracking system with individual item thresholds and 24/7 Google Sheets logging.",
        "bg_image": "",
        "logo_image": "",
        "user_db": {
            "admin": {"pass": "admin123", "name": "Admin Manager", "role": "admin", "email": "admin@pcable.com"},
            "operator1": {"pass": "user123", "name": "Shift Officer 1", "role": "operator", "email": "op1@pcable.com"},
            "operator2": {"pass": "user223", "name": "Shift Operator 2", "role": "operator", "email": "op2@pcable.com"}
        },
        "monitoring_points": [
            {"name": "CR-2002 (Top/Tail)", "val": 249.01, "norm_min": 200.0, "norm_max": 400.0, "caution_max": 600.0},
            {"name": "CR-1605 (Top End)", "val": 107.00, "norm_min": 150.0, "norm_max": 350.0, "caution_max": 500.0},
            {"name": "CR-2486 (Top End)", "val": 577.00, "norm_min": 200.0, "norm_max": 400.0, "caution_max": 600.0},
            {"name": "Shaft Furnace (SF-6)", "val": 292.00, "norm_min": 180.0, "norm_max": 380.0, "caution_max": 550.0},
            {"name": "Tundish-Sample", "val": 512.00, "norm_min": 200.0, "norm_max": 450.0, "caution_max": 650.0}
        ],
        "log_history": [
            {"Timestamp": "2026-09-14 10:00:00", "Duty Shift": "Shift A (12 Hours)", "Item": "CR-2002 (Top/Tail)", "Oxygen Level (ppm)": 249.01, "Status": "SAFE ZONE", "Updated By": "System"},
            {"Timestamp": "2026-09-14 10:15:00", "Duty Shift": "Shift A (12 Hours)", "Item": "CR-1605 (Top End)", "Oxygen Level (ppm)": 107.00, "Status": "CRITICAL LOW ALERT", "Updated By": "operator1"},
            {"Timestamp": "2026-09-14 10:30:00", "Duty Shift": "Shift A (12 Hours)", "Item": "CR-2486 (Top End)", "Oxygen Level (ppm)": 577.00, "Status": "CAUTION ZONE", "Updated By": "admin"}
        ]
    }

store = get_global_store()

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "username" not in st.session_state:
    st.session_state.username = ""
if "user_role" not in st.session_state:
    st.session_state.user_role = ""
if "duty_shift" not in st.session_state:
    st.session_state.duty_shift = "Shift A (12 Hours)"

# ---------------------------------------------------------
# WALLPAPER CSS FIX FOR STREAMLIT
# ---------------------------------------------------------
if store["bg_image"]:
    st.markdown(f"""
    <style>
    [data-testid="stAppViewContainer"] {{
        background: url("{store['bg_image']}") no-repeat center center fixed !important;
        background-size: cover !important;
    }}
    [data-testid="stHeader"] {{
        background: rgba(0,0,0,0) !important;
    }}
    .main .block-container {{
        background: rgba(255, 255, 255, 0.94);
        border-radius: 16px;
        padding: 2rem;
        margin-top: 1rem;
        box-shadow: 0 8px 32px rgba(0,0,0,0.2);
    }}
    </style>
    """, unsafe_allow_html=True)

st.markdown("""
<style>
.main-card {
    background-color: #262626;
    border-radius: 12px;
    padding: 20px;
    margin-bottom: 20px;
    color: white;
    box-shadow: 0 4px 10px rgba(0,0,0,0.15);
}
.card-title {
    font-weight: 700;
    font-size: 18px;
    margin-bottom: 12px;
    color: #ffffff;
    text-align: center;
}
.card-val-green { font-size: 42px; font-weight: 800; color: #2ecc71; text-align: center; margin: 10px 0; }
.card-val-orange { font-size: 42px; font-weight: 800; color: #f39c12; text-align: center; margin: 10px 0; }
.card-val-red { font-size: 42px; font-weight: 800; color: #e74c3c; text-align: center; margin: 10px 0; }

.badge-safe { background-color: rgba(46, 204, 113, 0.2); color: #2ecc71; padding: 6px 12px; border-radius: 20px; font-weight: bold; font-size: 13px; display: inline-block; }
.badge-caution { background-color: rgba(243, 156, 18, 0.2); color: #f39c12; padding: 6px 12px; border-radius: 20px; font-weight: bold; font-size: 13px; display: inline-block; }
.badge-critical { background-color: rgba(231, 76, 60, 0.2); color: #e74c3c; padding: 6px 12px; border-radius: 20px; font-weight: bold; font-size: 13px; display: inline-block; }
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# SIDEBAR CONTROLS & BRANDING
# ---------------------------------------------------------
st.sidebar.markdown("### 🔐 User Login & Controls")

if not st.session_state.logged_in:
    st.sidebar.warning("🔒 Read-Only Mode. Please log in to enable data updates.")
    input_user = st.sidebar.text_input("Username", key="login_user")
    input_pass = st.sidebar.text_input("Password", type="password", key="login_pass")
    st.session_state.duty_shift = st.sidebar.selectbox("Select Duty Shift", ["Shift A (12 Hours)", "Shift B (12 Hours)", "Shift C (8 Hours)"], key="shift_sel")
    
    if st.sidebar.button("Login to Dashboard", type="primary"):
        if input_user in store["user_db"] and store["user_db"][input_user]["pass"] == input_pass:
            st.session_state.logged_in = True
            st.session_state.username = input_user
            st.session_state.user_role = store["user_db"][input_user]["role"]
            st.sidebar.success(f"Welcome {store['user_db'][input_user]['name']}!")
            st.rerun()
        else:
            st.sidebar.error("Invalid Username or Password!")
else:
    user_info = store["user_db"].get(st.session_state.username, {"name": st.session_state.username, "role": "operator"})
    st.sidebar.success(f"Logged in as: **{user_info['name']}** ({user_info['role'].upper()})")
    st.sidebar.info(f"Active Shift: **{st.session_state.duty_shift}**")
    
    if st.sidebar.button("Logout", type="secondary"):
        st.session_state.logged_in = False
        st.session_state.username = ""
        st.session_state.user_role = ""
        st.rerun()

    st.sidebar.markdown("---")
    
    if st.session_state.user_role == "admin":
        with st.sidebar.expander("⚙️ Admin Settings & Branding", expanded=True):
            st.markdown("#### App Title Settings")
            new_title = st.text_input("Main Title", value=store["app_title"])
            new_subtitle = st.text_area("Subtitle", value=store["app_subtitle"])
            if st.button("Save Title Settings"):
                store["app_title"] = new_title
                store["app_subtitle"] = new_subtitle
                st.success("Title updated successfully!")
                st.rerun()
                
            st.markdown("---")
            st.markdown("#### 🖼️ Company Logo & Wallpaper")
            uploaded_logo = st.file_uploader("Upload Logo Image", type=["png", "jpg", "jpeg", "svg"], key="up_logo")
            if uploaded_logo:
                encoded_logo = base64.b64encode(uploaded_logo.read()).decode()
                store["logo_image"] = f"data:image/png;base64,{encoded_logo}"
                st.success("Logo updated globally!")
                st.rerun()
                
            uploaded_bg = st.file_uploader("Upload Background Wallpaper", type=["png", "jpg", "jpeg"], key="up_bg")
            if uploaded_bg:
                bytes_data = uploaded_bg.read()
                mime = uploaded_bg.type
                encoded_bg = base64.b64encode(bytes_data).decode()
                store["bg_image"] = f"data:{mime};base64,{encoded_bg}"
                st.success("Background wallpaper updated globally!")
                st.rerun()
                
            if store["logo_image"] or store["bg_image"]:
                if st.button("Reset Branding to Default"):
                    store["logo_image"] = ""
                    store["bg_image"] = ""
                    st.rerun()

# ---------------------------------------------------------
# HEADER SECTION
# ---------------------------------------------------------
head_col1, head_col2 = st.columns([1, 5])
with head_col1:
    if store["logo_image"]:
        st.image(store["logo_image"], width=130)
    else:
        st.markdown("<h1 style='font-size: 70px; margin:0;'>🏭</h1>", unsafe_allow_html=True)

with head_col2:
    st.markdown(f"<h1 style='margin-bottom:0; font-weight:800;'>{store['app_title']}</h1>", unsafe_allow_html=True)
    st.markdown(f"<p style='color: #555; font-size: 16px; margin-top:4px;'><em>{store['app_subtitle']}</em></p>", unsafe_allow_html=True)

st.markdown("---")

cols = st.columns(3)
any_high_alert = False
alert_details = []

for idx, pt in enumerate(store["monitoring_points"]):
    col = cols[idx % 3]
    val = pt["val"]
    
    if val < pt["norm_min"]:
        status_label = "CRITICAL LOW ALERT"
        val_class = "card-val-red"
        badge_class = "badge-critical"
        sub_desc = "Oxygen level critically low!"
        any_high_alert = True
        alert_details.append(f"{pt['name']}: Low Level ({val} ppm)")
    elif val > pt["caution_max"]:
        status_label = "CRITICAL HIGH ALERT"
        val_class = "card-val-red"
        badge_class = "badge-critical"
        sub_desc = "Oxygen level out of safe limits!"
        any_high_alert = True
        alert_details.append(f"{pt['name']}: High Level ({val} ppm)")
    elif val > pt["norm_max"]:
        status_label = "CAUTION ZONE"
        val_class = "card-val-orange"
        badge_class = "badge-caution"
        sub_desc = "Elevated range, monitor closely."
    else:
        status_label = "SAFE ZONE"
        val_class = "card-val-green"
        badge_class = "badge-safe"
        sub_desc = "Normal safe range."

    with col:
        st.markdown(f"""
        <div class="main-card">
            <div class="card-title">{pt['name']}</div>
            <div class="{val_class}">{val:.1f} <span style="font-size:20px;">ppm</span></div>
            <div style="text-align: center; margin-top: 10px;">
                <span class="{badge_class}">● {status_label}</span>
                <div style="color: #aaa; font-size: 12px; margin-top: 6px;">{sub_desc}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

# ---------------------------------------------------------
# LOUD PRISON / INDUSTRIAL SIREN ALARM COMPONENT
# ---------------------------------------------------------
if st.session_state.logged_in and any_high_alert:
    alert_msg = " | ".join(alert_details)
    alarm_html = f"""
    <div style="font-family: sans-serif; background-color: #8b0000; color: white; padding: 18px; border-radius: 12px; text-align: center; border: 3px solid #ff4b4b; box-shadow: 0 6px 16px rgba(0,0,0,0.4); margin-top: 10px; margin-bottom: 20px;">
        <h2 style="margin: 0 0 8px 0; color: #ffffff; font-size: 26px; font-weight: 900; text-transform: uppercase;">🚨 CRITICAL EMERGENCY ALARM 🚨</h2>
        <p style="font-size: 16px; margin: 0 0 14px 0; color: #ffcccc; font-weight: bold;">{alert_msg}</p>
        <button id="alarmBtn" onclick="toggleSiren()" style="background-color: #ff1a1a; color: white; border: 3px solid #ffffff; padding: 14px 32px; font-size: 18px; border-radius: 8px; cursor: pointer; font-weight: 900; box-shadow: 0 4px 15px rgba(255,0,0,0.6); letter-spacing: 1px;">
            📢 START PRISON EMERGENCY SIREN ALARM 🔊
        </button>
    </div>

    <script>
    var audioCtx = null;
    var sirenInterval = null;
    var isPlaying = false;

    function toggleSiren() {{
        var btn = document.getElementById("alarmBtn");
        
        if (isPlaying) {{
            if (sirenInterval) clearInterval(sirenInterval);
            sirenInterval = null;
            isPlaying = false;
            if (btn) {{
                btn.innerText = "📢 START PRISON EMERGENCY SIREN ALARM 🔊";
                btn.style.backgroundColor = "#ff1a1a";
            }}
            return;
        }}
        
        try {{
            var AudioCtxClass = window.AudioContext || window.webkitAudioContext;
            if (!audioCtx) {{
                audioCtx = new AudioCtxClass();
            }}
            if (audioCtx.state === 'suspended') {{
                audioCtx.resume();
            }}
            
            isPlaying = true;
            if (btn) {{
                btn.innerText = "🚨 HIGH ALERT SIREN RINGING (CLICK TO MUTE) 🛑";
                btn.style.backgroundColor = "#990000";
            }}

            var direction = 1;
            
            function playSirenSweep() {{
                if (!isPlaying) return;
                try {{
                    var osc = audioCtx.createOscillator();
                    var gain = audioCtx.createGain();
                    
                    // Sawtooth wave generates loud industrial jailbreak alarm tone
                    osc.type = 'sawtooth';
                    
                    var now = audioCtx.currentTime;
                    var duration = 0.55;
                    
                    if (direction === 1) {{
                        osc.frequency.setValueAtTime(450, now);
                        osc.frequency.exponentialRampToValueAtTime(1600, now + duration);
                        direction = -1;
                    }} else {{
                        osc.frequency.setValueAtTime(1600, now);
                        osc.frequency.exponentialRampToValueAtTime(450, now + duration);
                        direction = 1;
                    }}
                    
                    gain.gain.setValueAtTime(0.95, now);
                    gain.gain.linearRampToValueAtTime(0.95, now + duration - 0.05);
                    gain.gain.linearRampToValueAtTime(0.01, now + duration);
                    
                    osc.connect(gain);
                    gain.connect(audioCtx.destination);
                    
                    osc.start(now);
                    osc.stop(now + duration);
                }} catch(e) {{
                    console.error("Audio error:", e);
                }}
            }}

            playSirenSweep();
            sirenInterval = setInterval(playSirenSweep, 550);

        }} catch(err) {{
            alert("Audio error: " + err.message);
        }}
    }}
    </script>
    """
    components.html(alarm_html, height=190)

# ---------------------------------------------------------
# DATA ENTRY & OPERATIONS TABS
# ---------------------------------------------------------
if st.session_state.logged_in:
    st.markdown("### 📝 Live Data Entry & Operations Panel")
    tabs = st.tabs(["⚡ Update Values", "➕ Manage Monitoring Points", "👥 User Management (Admin)", "📊 Google Sheets Log History"])
    
    with tabs[0]:
        st.subheader("Update Live Sensor Readings")
        up_col1, up_col2 = st.columns(2)
        with up_col1:
            selected_point_name = st.selectbox("Select Item to Update", [p["name"] for p in store["monitoring_points"]])
            selected_point = next(p for p in store["monitoring_points"] if p["name"] == selected_point_name)
            new_val = st.number_input("New Oxygen Level (ppm)", value=float(selected_point["val"]), step=1.0, format="%.2f")
        
        with up_col2:
            st.info(f"**Item Limits:** Normal: {selected_point['norm_min']} - {selected_point['norm_max']} ppm | Caution Max: {selected_point['caution_max']} ppm")
            if st.button("Submit & Save Reading", type="primary"):
                selected_point["val"] = new_val
                if new_val < selected_point["norm_min"]:
                    st_str = "CRITICAL LOW ALERT"
                elif new_val > selected_point["caution_max"]:
                    st_str = "CRITICAL HIGH ALERT"
                elif new_val > selected_point["norm_max"]:
                    st_str = "CAUTION ZONE"
                else:
                    st_str = "SAFE ZONE"
                    
                now_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                store["log_history"].append({
                    "Timestamp": now_str,
                    "Duty Shift": st.session_state.duty_shift,
                    "Item": selected_point_name,
                    "Oxygen Level (ppm)": new_val,
                    "Status": st_str,
                    "Updated By": st.session_state.username
                })
                st.success(f"Successfully updated {selected_point_name} to {new_val} ppm!")
                st.rerun()

    with tabs[1]:
        st.subheader("Add or Remove Monitoring Points")
        if st.session_state.user_role == "admin":
            st.markdown("#### ➕ Add New Point")
            with st.form("add_point_form"):
                p_name = st.text_input("Point Name (e.g. CR-3000 Top End)")
                p_val = st.number_input("Initial Value (ppm)", value=250.0)
                p_min = st.number_input("Minimum Safe (ppm)", value=150.0)
                p_norm_max = st.number_input("Normal Max (ppm)", value=400.0)
                p_caut_max = st.number_input("Caution Max (ppm)", value=600.0)
                if st.form_submit_button("Add Monitoring Point"):
                    if p_name:
                        store["monitoring_points"].append({
                            "name": p_name,
                            "val": p_val,
                            "norm_min": p_min,
                            "norm_max": p_norm_max,
                            "caution_max": p_caut_max
                        })
                        st.success(f"Added {p_name} successfully!")
                        st.rerun()
                    else:
                        st.error("Please provide a valid point name.")
                        
            st.markdown("---")
            st.markdown("#### 🗑️ Remove Point")
            del_point = st.selectbox("Select Point to Delete", [p["name"] for p in store["monitoring_points"]], key="del_sel")
            if st.button("Delete Selected Point", type="secondary"):
                store["monitoring_points"] = [p for p in store["monitoring_points"] if p["name"] != del_point]
                st.success(f"Deleted {del_point} successfully!")
                st.rerun()
        else:
            st.warning("Only Admin users can add or remove monitoring points.")

    with tabs[2]:
        if st.session_state.user_role == "admin":
            st.subheader("👥 System User Accounts")
            users_df = pd.DataFrame([
                {"Username": u, "Name": store["user_db"][u]["name"], "Role": store["user_db"][u]["role"], "Email": store["user_db"][u]["email"]}
                for u in store["user_db"]
            ])
            st.dataframe(users_df, use_container_width=True)
            
            st.markdown("#### Create New User Account")
            with st.form("new_user_form"):
                nu_user = st.text_input("New Username")
                nu_pass = st.text_input("New Password", type="password")
                nu_name = st.text_input("Full Name")
                nu_email = st.text_input("Email")
                nu_role = st.selectbox("Role", ["operator", "admin"])
                if st.form_submit_button("Create Account"):
                    if nu_user and nu_pass:
                        store["user_db"][nu_user] = {
                            "pass": nu_pass,
                            "name": nu_name,
                            "role": nu_role,
                            "email": nu_email
                        }
                        st.success(f"User {nu_user} created successfully!")
                        st.rerun()
                    else:
                        st.error("Username and Password are required.")
        else:
            st.warning("Access Restricted: Admin privileges required.")

    with tabs[3]:
        st.subheader("📊 24/7 Google Sheets Logged History")
        df_logs = pd.DataFrame(store["log_history"])
        st.dataframe(df_logs, use_container_width=True)
        csv_data = df_logs.to_csv(index=False).encode('utf-8')
        st.download_button("📥 Download Log History (CSV)", data=csv_data, file_name="pcl_oxygen_log.csv", mime="text/csv")
