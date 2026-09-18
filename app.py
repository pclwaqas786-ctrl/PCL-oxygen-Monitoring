import base64
from datetime import datetime, timedelta, timezone
import json
import os
import pandas as pd
import requests
import streamlit as st

# Set Page Config
st.set_page_config(
    page_title="Pakistan Cable (CCR) - Oxygen & Coil Monitoring",
    page_icon="🏭",
    layout="wide",
    initial_sidebar_state="expanded",
)

DATA_FILE = "store_data.json"


def get_pkt_time():
    """Returns current accurate Pakistan Standard Time (UTC+5) without extra libraries"""
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
            "coil_num": "1234",
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
            "name": "Shaft Furnace(SF)",
            "coil_prefix": "",
            "coil_num": "",
            "val": 0.0,
            "min_limit": 100.0,
            "max_limit": 650.0,
            "last_updated": get_pkt_time(),
        },
        {
            "name": "Holding furnace(HF)",
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

# Custom CSS
st.markdown(
    """
<style>
.stApp { background-color: #0F172A; color: white; }
.main-card {
    background-color: #1e293b;
    border: 1px solid rgba(255, 255, 255, 0.15);
    border-radius: 12px;
    padding: 18px;
    margin-bottom: 15px;
    color: white;
    box-shadow: 0 4px 15px rgba(0,0,0,0.4);
}
.card-title { font-weight: 700; font-size: 22px; margin-bottom: 6px; color: #ffffff; text-align: center; }
.card-coil { font-weight: 600; font-size: 15px; margin-bottom: 10px; color: #38bdf8; text-align: center; }
.card-val-green { font-size: 42px; font-weight: 900; color: #2ecc71; text-align: center; margin: 10px 0; }
.card-val-red { font-size: 42px; font-weight: 900; color: #e74c3c; text-align: center; margin: 10px 0; }
.badge-safe { background-color: rgba(46, 204, 113, 0.2); color: #2ecc71; padding: 6px 12px; border-radius: 20px; font-weight: bold; font-size: 13px; display: inline-block; }
.badge-critical { background-color: rgba(231, 76, 60, 0.2); color: #e74c3c; padding: 6px 12px; border-radius: 20px; font-weight: bold; font-size: 13px; display: inline-block; }
.card-timestamp { color: #94a3b8; font-size: 12px; text-align: center; margin-top: 12px; border-top: 1px solid rgba(255, 255, 255, 0.1); padding-top: 8px; }
</style>
""",
    unsafe_allow_html=True,
)

# Sidebar Login & Controls
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
head_col1, head_col2 = st.columns([1.2, 5.8])
with head_col1:
    if store.get("logo_image"):
        st.image(store["logo_image"], width=100)
    else:
        st.markdown(
            """<div style="background: #1e293b; width: 80px; height: 80px; border-radius: 12px; display: flex; align-items: center; justify-content: center; border: 2px solid #38bdf8;"><span style="color: #2ecc71; font-size: 20px; font-weight: bold;">PCL</span></div>""",
            unsafe_allow_html=True,
        )

with head_col2:
    st.markdown(
        f"<h2 style='margin:0;'>{store['app_title']}</h2>", unsafe_allow_html=True
    )
    st.markdown(
        f"<p style='color: #cbd5e1; font-size: 14px;'><em>{store['app_subtitle']}</em></p>",
        unsafe_allow_html=True,
    )

st.markdown("---")

# Strict Range Checking
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

# Loud Industrial Synth Beep JavaScript Alarm
if play_audio:
    st.error(
        f"🚨 CRITICAL ALERT ({', '.join(critical_stations)}): Values violate Min/Max limits!"
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
        osc.stop(ctx.currentTime + 0.5);
    }
    var intervalId = setInterval(playBeep, 800);
    </script>
    """
    st.components.v1.html(alarm_script, height=0, width=0)

# Station Cards Layout
cols = st.columns(len(store["monitoring_points"]))
for idx, pt in enumerate(store["monitoring_points"]):
    with cols[idx]:
        s_name = pt["name"]
        val = pt["val"]
        min_l = pt.get("min_limit", 100.0)
        max_l = pt.get("max_limit", 350.0)
        last_t = pt.get("last_updated", get_pkt_time())

        coil_html = ""
        if s_name.upper() == "ROD" and (
            pt.get("coil_prefix") or pt.get("coil_num")
        ):
            coil_html = f'<div class="card-coil">📦 Coil: {pt.get("coil_prefix", "")}-{pt.get("coil_num", "")}</div>'

        is_critical = val < min_l or val > max_l

        if is_critical:
            status_label, val_class, badge_class, sub_desc = (
                "CRITICAL ALERT",
                "card-val-red",
                "badge-critical",
                f"Limit: {min_l} - {max_l}",
            )
        else:
            status_label, val_class, badge_class, sub_desc = (
                "SAFE ZONE",
                "card-val-green",
                "badge-safe",
                f"Range: {min_l} - {max_l}",
            )
            st.session_state.muted_stations[s_name] = False

        card_html = f'<div class="main-card"><div class="card-title">{s_name}</div>{coil_html}<div class="{val_class}">{val:.2f} <span style="font-size:16px;">ppm</span></div><div style="text-align: center;"><span class="{badge_class}">● {status_label}</span><div style="color: #94a3b8; font-size: 11px; margin-top: 6px;">{sub_desc}</div></div><div class="card-timestamp">🕒 {last_t}</div></div>'
        st.markdown(card_html, unsafe_allow_html=True)

        if is_critical:
            is_muted = st.session_state.muted_stations.get(s_name, False)
            if not is_muted:
                if st.button(
                    f"🔕 Mute ({s_name})",
                    key=f"mute_{idx}",
                    use_container_width=True,
                ):
                    st.session_state.muted_stations[s_name] = True
                    st.rerun()
            else:
                if st.button(
                    f"🔔 Unmute ({s_name})",
                    key=f"unmute_{idx}",
                    use_container_width=True,
                ):
                    st.session_state.muted_stations[s_name] = False
                    st.rerun()

st.markdown("---")
st.markdown("### 📝 Live Data Entry & Operations Panel")
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
        if current_pt["name"].upper() == "ROD":
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
                if new_num and current_pt["name"].upper() == "ROD"
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
