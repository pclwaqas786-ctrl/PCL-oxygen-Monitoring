import base64
from datetime import datetime, timedelta, timezone
import json
import os
import pandas as pd
import requests
import streamlit as st

# Page Configuration
st.set_page_config(
    page_title="Pakistan Cable (CCR) - Oxygen & Coil Monitoring",
    page_icon="🏭",
    layout="wide",
    initial_sidebar_state="expanded",
)

DATA_FILE = "store_data.json"


def get_pkt_time():
    """Returns current accurate Pakistan Standard Time (UTC+5)"""
    pkt_zone = timezone(timedelta(hours=5))
    return datetime.now(pkt_zone).strftime("%Y-%m-%d %I:%M:%S %p")


default_store = {
    "app_title": "Pakistan Cable (CCR)- Oxygen & Coil Monitoring",
    "app_subtitle": "Real-time oxygen tracking system with individual item thresholds and 24/7 Google Sheets logging.",
    "logo_image": "",
    "google_sheet_url": "https://docs.google.com/spreadsheets/d/your-sheet-id-here/edit",
    "user_db": {
        "admin": {
            "pass": "admin123",
            "name": "Admin Manager",
            "role": "admin",
            "email": "admin@pcable.com",
        }
    },
    "monitoring_points": [
        {
            "name": "ROD",
            "coil_prefix": "CR",
            "coil_num": "9653",
            "val": 556.0,
            "min_limit": 100.0,
            "max_limit": 350.0,
            "last_updated": get_pkt_time(),
        },
        {
            "name": "Tundish",
            "coil_prefix": "",
            "coil_num": "",
            "val": 185.97,
            "min_limit": 100.0,
            "max_limit": 350.0,
            "last_updated": get_pkt_time(),
        },
        {
            "name": "Shaft Furnace (SF)",
            "coil_prefix": "",
            "coil_num": "",
            "val": 50.0,
            "min_limit": 100.0,
            "max_limit": 650.0,
            "last_updated": get_pkt_time(),
        },
        {
            "name": "Holding Furnace (HF)",
            "coil_prefix": "",
            "coil_num": "",
            "val": 450.0,
            "min_limit": 100.0,
            "max_limit": 500.0,
            "last_updated": get_pkt_time(),
        },
    ],
    "log_history": [],
}

if "store" not in st.session_state:
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r") as f:
                st.session_state.store = json.load(f)
        except Exception:
            st.session_state.store = default_store
    else:
        st.session_state.store = default_store

store = st.session_state.store


def save_store():
    try:
        with open(DATA_FILE, "w") as f:
            json.dump(st.session_state.store, f, indent=4)
    except Exception:
        pass


def save_to_google_sheet(log_data, sheet_url):
    if not sheet_url or "your-sheet-id-here" in sheet_url:
        return False
    try:
        requests.post(sheet_url, json={"data": log_data}, timeout=5)
        return True
    except Exception:
        return False


if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "username" not in st.session_state:
    st.session_state.username = ""
if "duty_shift" not in st.session_state:
    st.session_state.duty_shift = "Shift A"
if "muted_stations" not in st.session_state:
    st.session_state.muted_stations = {}

# Custom CSS for Big Display Door Se Dikhne Ke Liye
st.markdown(
    """
<style>
.stApp { background-color: #0b0f19; color: white; }
.big-card-container {
    background: #111827;
    border: 2px solid #374151;
    border-radius: 16px;
    padding: 24px;
    margin-bottom: 20px;
    box-shadow: 0 10px 25px rgba(0,0,0,0.6);
    text-align: center;
}
.big-card-critical {
    border: 3px solid #ef4444 !important;
    background: linear-gradient(180deg, #1f1215 0%, #111827 100%);
}
.big-card-safe {
    border: 3px solid #10b981 !important;
    background: linear-gradient(180deg, #062319 0%, #111827 100%);
}
.big-title {
    font-size: 32px !important;
    font-weight: 800 !important;
    color: #ffffff;
    letter-spacing: 1px;
}
.big-coil {
    font-size: 22px !important;
    color: #38bdf8;
    font-weight: 700;
    margin-top: 5px;
}
.big-value-red {
    font-size: 72px !important;
    font-weight: 900 !important;
    color: #ef4444;
    margin: 10px 0;
    text-shadow: 0 0 20px rgba(239, 68, 68, 0.4);
}
.big-value-green {
    font-size: 72px !important;
    font-weight: 900 !important;
    color: #10b981;
    margin: 10px 0;
    text-shadow: 0 0 20px rgba(16, 185, 129, 0.4);
}
.big-status-critical {
    background-color: #ef4444;
    color: white;
    font-size: 20px;
    font-weight: 800;
    padding: 8px 24px;
    border-radius: 30px;
    display: inline-block;
    letter-spacing: 1px;
}
.big-status-safe {
    background-color: #10b981;
    color: white;
    font-size: 20px;
    font-weight: 800;
    padding: 8px 24px;
    border-radius: 30px;
    display: inline-block;
    letter-spacing: 1px;
}
.big-subtext {
    font-size: 16px;
    color: #9ca3af;
    margin-top: 10px;
}
.big-time {
    font-size: 14px;
    color: #6b7280;
    margin-top: 15px;
    border-top: 1px solid #374151;
    padding-top: 10px;
}
</style>
""",
    unsafe_allow_html=True,
)

# Sidebar Controls
st.sidebar.markdown("### 🔐 User Login & Controls")
if not st.session_state.logged_in:
    st.sidebar.warning("Please log in to continue.")
    login_user = st.sidebar.text_input("Username", key="login_u")
    login_pass = st.sidebar.text_input("Password", type="password", key="login_p")
    if st.sidebar.button("Login", type="primary"):
        if (
            login_user in store["user_db"]
            and store["user_db"][login_user]["pass"] == login_pass
        ):
            st.session_state.logged_in = True
            st.session_state.username = login_user
            st.success("Logged in successfully!")
            st.rerun()
        else:
            st.sidebar.error("Invalid Username or Password")
    st.stop()

user_info = store["user_db"].get(
    st.session_state.username, {"name": "Admin Manager", "role": "admin"}
)
st.sidebar.success(
    f"Logged in as: **{user_info['name']}** ({user_info['role'].upper()})"
)

if st.sidebar.button("🚪 Logout", type="secondary"):
    st.session_state.logged_in = False
    st.session_state.username = ""
    st.rerun()

st.session_state.duty_shift = st.sidebar.selectbox(
    "Select Duty Shift", ["Shift A", "Shift B"], index=0
)

st.sidebar.markdown("---")
# Admin Settings
with st.sidebar.expander("⚙️ Admin Settings & Branding", expanded=False):
    st.markdown("#### App Title Settings")
    new_title = st.text_input("Main Title", value=store["app_title"])
    new_subtitle = st.text_area("Subtitle", value=store["app_subtitle"])
    if st.button("Save Title Settings"):
        store["app_title"] = new_title
        store["app_subtitle"] = new_subtitle
        save_store()
        st.success("Title updated successfully!")
        st.rerun()

    st.markdown("---")
    st.markdown("#### 📊 Google Sheets Integration")
    new_sheet_url = st.text_input(
        "Google Sheet Webhook URL", value=store.get("google_sheet_url", "")
    )
    if st.button("Save Sheet URL"):
        store["google_sheet_url"] = new_sheet_url
        save_store()
        st.success("Google Sheet URL saved!")
        st.rerun()

    st.markdown("---")
    st.markdown("#### 🖼️ Company Logo")
    uploaded_logo = st.file_uploader(
        "Upload Logo Image", type=["png", "jpg", "jpeg"]
    )
    if uploaded_logo:
        encoded_logo = base64.b64encode(uploaded_logo.read()).decode()
        store["logo_image"] = f"data:image/png;base64,{encoded_logo}"
        save_store()
        st.success("Logo uploaded successfully!")
        st.rerun()

# Header Section
head_col1, head_col2 = st.columns([1, 6])
with head_col1:
    if store.get("logo_image"):
        st.image(store["logo_image"], width=85)
    else:
        st.markdown(
            """<div style="background: #1f2937; width: 75px; height: 75px; border-radius: 12px; display: flex; align-items: center; justify-content: center; border: 2px solid #38bdf8;"><span style="color: #10b981; font-size: 20px; font-weight: bold;">PCL</span></div>""",
            unsafe_allow_html=True,
        )

with head_col2:
    st.markdown(
        f"<h1 style='margin:0; font-size: 30px;'>{store['app_title']}</h1>",
        unsafe_allow_html=True,
    )
    st.markdown(
        f"<p style='color: #9ca3af; font-size: 14px;'><em>{store['app_subtitle']}</em></p>",
        unsafe_allow_html=True,
    )

st.markdown("---")

# Checking Alarm Logic
play_audio = False
critical_stations = []

for pt in store["monitoring_points"]:
    s_name = pt["name"]
    val = pt["val"]
    min_l = pt.get("min_limit", 100.0)
    max_l = pt.get("max_limit", 350.0)

    if val < min_l or val > max_l:
        critical_stations.append(s_name)
        if not st.session_state.muted_stations.get(s_name, False):
            play_audio = True

if play_audio:
    st.error(
        f"🚨 CRITICAL ALARM ACTIVE: {', '.join(critical_stations)} limits exceeded!"
    )
    alarm_script = """
    <script>
    var ctx = new (window.AudioContext || window.webkitAudioContext)();
    function playBeep() {
        var osc = ctx.createOscillator();
        var gain = ctx.createGain();
        osc.type = 'sawtooth';
        osc.frequency.setValueAtTime(880, ctx.currentTime);
        gain.gain.setValueAtTime(0.3, ctx.currentTime);
        osc.connect(gain);
        gain.connect(ctx.destination);
        osc.start();
        osc.stop(ctx.currentTime + 0.4);
    }
    var intervalId = setInterval(playBeep, 800);
    </script>
    """
    st.components.v1.html(alarm_script, height=0, width=0)

# Main Display Stations (Door se dekhne ke liye Large View)
st.markdown("### 🖥️ Live Monitoring Display")

# Loop through all stations with big display format
for idx, pt in enumerate(store["monitoring_points"]):
    s_name = pt["name"]
    val = pt["val"]
    min_l = pt.get("min_limit", 100.0)
    max_l = pt.get("max_limit", 350.0)
    last_t = pt.get("last_updated", get_pkt_time())
    is_critical = val < min_l or val > max_l

    card_class = "big-card-critical" if is_critical else "big-card-safe"
    val_class = "big-value-red" if is_critical else "big-value-green"
    badge_class = (
        "big-status-critical" if is_critical else "big-status-safe"
    )
    status_text = "🚨 CRITICAL ALERT" if is_critical else "🟢 SAFE ZONE"

    coil_html = ""
    if "ROD" in s_name.upper() and (pt.get("coil_prefix") or pt.get("coil_num")):
        coil_html = f'<div class="big-coil">📦 Coil: {pt.get("coil_prefix", "")}-{pt.get("coil_num", "")}</div>'

    card_html = f"""
    <div class="big-card-container {card_class}">
        <div class="big-title">{s_name}</div>
        {coil_html}
        <div class="{val_class}">{val:.2f} <span style="font-size:28px;">PPM</span></div>
        <div style="margin: 15px 0;">
            <span class="{badge_class}">{status_text}</span>
        </div>
        <div class="big-subtext">Allowed Range: <b>{min_l} - {max_l} PPM</b></div>
        <div class="big-time">🕒 Last Update: {last_t} (PKT)</div>
    </div>
    """
    st.markdown(card_html, unsafe_allow_html=True)

    if is_critical:
        is_muted = st.session_state.muted_stations.get(s_name, False)
        btn_col1, btn_col2, btn_col3 = st.columns([1, 2, 1])
        with btn_col2:
            if not is_muted:
                if st.button(
                    f"🔕 Mute Alarm for {s_name}",
                    key=f"mute_btn_{idx}",
                    use_container_width=True,
                    type="primary",
                ):
                    st.session_state.muted_stations[s_name] = True
                    st.rerun()
            else:
                if st.button(
                    f"🔔 Unmute Alarm for {s_name}",
                    key=f"unmute_btn_{idx}",
                    use_container_width=True,
                ):
                    st.session_state.muted_stations[s_name] = False
                    st.rerun()

st.markdown("---")
st.markdown("### 📝 Operations & Data Input Panel")
tabs = st.tabs(
    [
        "⚡ Update Readings",
        "⚙️ Admin: Manage Limits",
        "👥 User Management",
        "📊 Log History & Google Sheets",
    ]
)

with tabs[0]:
    st.subheader("Update Live Sensor Reading & Coil Information")
    pt_names = [p["name"] for p in store["monitoring_points"]]
    selected_edit_idx = st.selectbox(
        "Select Monitoring Point",
        options=range(len(pt_names)),
        format_func=lambda x: pt_names[x],
    )
    current_pt = store["monitoring_points"][selected_edit_idx]

    col_a, col_b = st.columns(2)
    with col_a:
        new_val = st.number_input(
            "Oxygen Value (PPM)",
            value=float(current_pt["val"]),
            step=0.01,
            format="%.2f",
        )

    with col_b:
        if "ROD" in current_pt["name"].upper():
            new_prefix = st.text_input(
                "Coil/Item Prefix",
                value=current_pt.get("coil_prefix", "CR"),
                key="edit_prefix",
            )
            new_num = st.text_input(
                "Coil/Item Number",
                value=current_pt.get("coil_num", ""),
                key="edit_num",
            )
        else:
            new_prefix = ""
            new_num = ""

    if st.button("Submit & Save Reading", type="primary"):
        now_str = get_pkt_time()

        store["monitoring_points"][selected_edit_idx]["val"] = new_val
        store["monitoring_points"][selected_edit_idx][
            "coil_prefix"
        ] = new_prefix
        store["monitoring_points"][selected_edit_idx]["coil_num"] = new_num
        store["monitoring_points"][selected_edit_idx]["last_updated"] = now_str

        st.session_state.muted_stations[current_pt["name"]] = False

        new_log = {
            "Time": now_str,
            "Station": current_pt["name"],
            "Coil": (
                f"{new_prefix}-{new_num}"
                if new_num and "ROD" in current_pt["name"].upper()
                else "N/A"
            ),
            "Value": new_val,
            "User": st.session_state.username,
            "Shift": st.session_state.duty_shift,
        }

        store["log_history"].append(new_log)
        save_store()

        save_to_google_sheet(new_log, store.get("google_sheet_url", ""))

        st.success(f"Reading updated successfully at {now_str} (PKT)!")
        st.rerun()

with tabs[1]:
    st.subheader("⚙️ Admin Panel - Manage Limits")
    for idx, pt in enumerate(store["monitoring_points"]):
        col1, col2, col3 = st.columns(3)
        with col1:
            st.write(f"**{pt['name']}**")
        with col2:
            new_min = st.number_input(
                f"Min Limit ({pt['name']})",
                value=float(pt.get("min_limit", 100.0)),
                key=f"min_{idx}",
            )
        with col3:
            new_max = st.number_input(
                f"Max Limit ({pt['name']})",
                value=float(pt.get("max_limit", 350.0)),
                key=f"max_{idx}",
            )

        store["monitoring_points"][idx]["min_limit"] = new_min
        store["monitoring_points"][idx]["max_limit"] = new_max
    if st.button("Save All Limits"):
        save_store()
        st.success("Limits updated successfully!")
        st.rerun()

with tabs[2]:
    st.subheader("👥 User Management & Create New User")
    with st.form("create_user_form"):
        st.markdown("#### Add New System User")
        new_username = st.text_input("New Username")
        new_name = st.text_input("Full Name")
        new_password = st.text_input("Password", type="password")
        new_role = st.selectbox("Role", ["operator", "admin"])

        submit_user = st.form_submit_button("Create User")
        if submit_user:
            if new_username and new_password and new_name:
                if new_username in store["user_db"]:
                    st.error("Username already exists!")
                else:
                    store["user_db"][new_username] = {
                        "pass": new_password,
                        "name": new_name,
                        "role": new_role,
                        "email": f"{new_username}@pcable.com",
                    }
                    save_store()
                    st.success(
                        f"User '{new_username}' successfully created!"
                    )
                    st.rerun()

with tabs[3]:
    st.subheader("📊 Log History & Saved Records")

    if store["log_history"]:
        df_logs = pd.DataFrame(store["log_history"])
        st.dataframe(df_logs, use_container_width=True)

        csv_data = df_logs.to_csv(index=False).encode("utf-8")
        st.download_button(
            label="📥 Download Data Logs CSV",
            data=csv_data,
            file_name=f"oxygen_logs_{datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv",
        )
    else:
        st.info("No logs recorded yet.")
