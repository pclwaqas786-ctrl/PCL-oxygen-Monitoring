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
    initial_sidebar_state="collapsed",
)

DATA_FILE = "store_data.json"


def _load_logo_b64():
    try:
        _p = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets", "pcl-logo.png")
        with open(_p, "rb") as _f:
            return base64.b64encode(_f.read()).decode("ascii")
    except Exception:
        return ""


PCL_LOGO_B64 = _load_logo_b64()


def get_pkt_time():
    """Returns current accurate Pakistan Standard Time (UTC+5)"""
    pkt_zone = timezone(timedelta(hours=5))
    return datetime.now(pkt_zone).strftime("%Y-%m-%d %I:%M:%S %p")


default_store = {
    "app_title": "Pakistan Cable (CCR)- Oxygen & Coil Monitoring",
    "app_subtitle": "Real-time oxygen tracking system with individual item thresholds and 24/7 Google Sheets logging.",
    "logo_image": "",
    "google_sheet_url": "https://docs.google.com/spreadsheets/d/your-sheet-id-here/edit",
    "selected_alarm_sound": "Jail Siren (Wail)",
    "schema_version": 2,
    "user_db": {
        "admin": {
            "pass": "admin123@",
            "name": "Admin Manager",
            "role": "admin",
            "email": "admin@pcable.com",
        },
        "shoaib.sheikh": {
            "pass": "123456",
            "name": "Shoaib Sheikh",
            "role": "operator",
            "email": "shoaib@pcable.com",
        },
    },
    "monitoring_points": [
        {
            "name": "ROD",
            "coil_prefix": "CR",
            "coil_num": "9653",
            "val": 220.0,
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
            "val": 320.0,
            "min_limit": 100.0,
            "max_limit": 650.0,
            "last_updated": get_pkt_time(),
        },
        {
            "name": "Holding furnace(HF)",
            "coil_prefix": "",
            "coil_num": "",
            "val": 150.0,
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
    """Sends one log row to the Google Apps Script Web App webhook.

    sheet_url must be the Web App /exec URL from Apps Script
    (see apps-script/Code.gs). Returns True on success, False otherwise.
    Never raises - a failed save must not break the reading submit flow.
    """
    if not sheet_url:
        return False
    if "your-sheet-id-here" in sheet_url:
        return False
    if "script.google.com/macros" not in sheet_url:
        # Not an Apps Script webhook URL - a plain Google Sheets share
        # link cannot receive POSTs, so skip instead of failing silently.
        return False
    try:
        r = requests.post(sheet_url, json={"data": log_data}, timeout=8)
        return r.ok
    except Exception:
        return False


def sheets_autosave_on(sheet_url):
    """True when a valid Apps Script webhook URL is configured."""
    return bool(
        sheet_url
        and "your-sheet-id-here" not in sheet_url
        and "script.google.com/macros" in sheet_url
    )


# One-time migration (v2): green default readings + Jail Siren default sound.
# The server's store_data.json survives redeploys, so without this the old
# values (ROD 556, SF 0.0) and old sound would persist after the update.
if store.get("schema_version", 1) < 2:
    _v2_defaults = [220.0, 185.97, 320.0, 150.0]
    for _pt, _v in zip(store.get("monitoring_points", []), _v2_defaults):
        _pt["val"] = _v
        _pt["last_updated"] = get_pkt_time()
    store["selected_alarm_sound"] = "Jail Siren (Wail)"
    store["schema_version"] = 2
    save_store()

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "username" not in st.session_state:
    st.session_state.username = ""
if "duty_shift" not in st.session_state:
    st.session_state.duty_shift = "Shift A"
if "muted_stations" not in st.session_state:
    st.session_state.muted_stations = {}

# Custom Styling
st.markdown(
    """
<style>
.stApp {
    background: radial-gradient(1200px 600px at 20% -5%, #16233d 0%, #0d1526 55%, #090e1a 100%);
    color: #f2f6fc;
}
div[data-baseweb="tab-list"] { gap: 8px; }
button[data-baseweb="tab"], [data-testid="stTab"] {
    background-color: #22314d !important;
    color: #dbe6f7 !important;
    border-radius: 10px;
    padding: 10px 18px;
    font-weight: 700;
    font-size: 17px !important;
    border: 1px solid #3b5178;
}
button[data-baseweb="tab"]:hover, [data-testid="stTab"]:hover {
    background-color: #2c3f63 !important;
    color: #ffffff !important;
}
button[data-baseweb="tab"][aria-selected="true"], [data-testid="stTab"][aria-selected="true"] {
    background-color: #1d6ff2 !important;
    color: #ffffff !important;
    border-color: #7fb2ff;
    box-shadow: 0 0 12px rgba(59,130,246,.55);
}
/* secondary buttons (Full Screen / Refresh): dark pill, white text */
[data-testid="stBaseButton-secondary"] {
    background-color: #22314d !important;
    color: #ffffff !important;
    border: 1px solid #3b5178 !important;
    font-weight: 700;
}
[data-testid="stBaseButton-secondary"]:hover {
    background-color: #2c3f63 !important;
    color: #ffffff !important;
    border-color: #7fb2ff !important;
}
.stSelectbox label, .stNumberInput label, .stTextInput label, .stRadio label {
    color: #e8eefb !important;
    font-weight: 600;
}
section[data-testid="stSidebar"] { background-color: #0d1626; }
</style>
""",
    unsafe_allow_html=True,
)

# Sidebar Login Controls
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
    st.session_state.username, {"name": "Operator User", "role": "operator"}
)
is_admin = user_info.get("role") == "admin"

st.sidebar.success(
    f"Logged in as: **{user_info['name']}** ({user_info['role'].upper()})"
)

if st.sidebar.button("🚪 Logout", type="secondary"):
    st.session_state.logged_in = False
    st.session_state.username = ""
    st.session_state.pop("fs_station", None)
    st.rerun()

st.session_state.duty_shift = st.sidebar.selectbox(
    "Select Duty Shift", ["Shift A", "Shift B"], index=0
)

# Admin Only Branding Controls in Sidebar
if is_admin:
    with st.sidebar.expander("⚙️ Admin Branding Settings", expanded=False):
        new_title = st.text_input("Main Title", value=store["app_title"])
        new_subtitle = st.text_area("Subtitle", value=store["app_subtitle"])
        new_sheet_url = st.text_input(
            "Google Sheet Webhook URL",
            value=store.get("google_sheet_url", ""),
            help="Apps Script Web App /exec URL (script.google.com/macros/...) - NOT the normal Sheets share link. Setup steps: README.md",
        )
        if st.button("Save System Settings"):
            store["app_title"] = new_title
            store["app_subtitle"] = new_subtitle
            store["google_sheet_url"] = new_sheet_url
            save_store()
            st.success("Settings updated!")
            st.rerun()

sound_type = store.get("selected_alarm_sound", "Jail Siren (Wail)")
sound_scripts = {
    "Loud Industrial Siren": """
        var osc = ctx.createOscillator();
        var gain = ctx.createGain();
        osc.type = 'sawtooth';
        osc.frequency.setValueAtTime(440, ctx.currentTime);
        osc.frequency.exponentialRampToValueAtTime(1200, ctx.currentTime + 0.5);
        gain.gain.setValueAtTime(0.8, ctx.currentTime);
        osc.connect(gain);
        gain.connect(ctx.destination);
        osc.start();
        osc.stop(ctx.currentTime + 0.5);
    """,
    "High Pitch Beep Alert": """
        var osc = ctx.createOscillator();
        var gain = ctx.createGain();
        osc.type = 'square';
        osc.frequency.setValueAtTime(2400, ctx.currentTime);
        gain.gain.setValueAtTime(0.6, ctx.currentTime);
        osc.connect(gain);
        gain.connect(ctx.destination);
        osc.start();
        osc.stop(ctx.currentTime + 0.2);
    """,
    "Pulsing Emergency Siren": """
        var osc = ctx.createOscillator();
        var gain = ctx.createGain();
        osc.type = 'triangle';
        osc.frequency.setValueAtTime(600, ctx.currentTime);
        osc.frequency.linearRampToValueAtTime(1500, ctx.currentTime + 0.3);
        osc.frequency.linearRampToValueAtTime(600, ctx.currentTime + 0.6);
        gain.gain.setValueAtTime(0.9, ctx.currentTime);
        osc.connect(gain);
        gain.connect(ctx.destination);
        osc.start();
        osc.stop(ctx.currentTime + 0.6);
    """,
    "Submarine Continuous Horn": """
        var osc = ctx.createOscillator();
        var gain = ctx.createGain();
        osc.type = 'sawtooth';
        osc.frequency.setValueAtTime(220, ctx.currentTime);
        gain.gain.setValueAtTime(1.0, ctx.currentTime);
        osc.connect(gain);
        gain.connect(ctx.destination);
        osc.start();
        osc.stop(ctx.currentTime + 0.7);
    """,
    "Jail Siren (Wail)": """
        var osc = ctx.createOscillator();
        var gain = ctx.createGain();
        var lfo = ctx.createOscillator();
        var lfoGain = ctx.createGain();
        osc.type = 'sawtooth';
        osc.frequency.setValueAtTime(800, ctx.currentTime);
        lfo.type = 'sine';
        lfo.frequency.setValueAtTime(0.45, ctx.currentTime);
        lfoGain.gain.setValueAtTime(350, ctx.currentTime);
        lfo.connect(lfoGain);
        lfoGain.connect(osc.frequency);
        gain.gain.setValueAtTime(0.7, ctx.currentTime);
        osc.connect(gain);
        gain.connect(ctx.destination);
        osc.start();
        lfo.start();
        var stopTime = ctx.currentTime + 2.2;
        osc.stop(stopTime);
        lfo.stop(stopTime);
    """,
}
current_js = sound_scripts.get(
    sound_type, sound_scripts["Jail Siren (Wail)"]
)


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


# Fullscreen station display - giant readout for control-room screens
if st.session_state.get("fs_station"):
    if play_audio:
        st.components.v1.html(
            f"<script>var ctx = new (window.AudioContext || window.webkitAudioContext)(); function playAlarm(){{{current_js}}} var intervalId = setInterval(playAlarm, 700);</script>",
            height=0,
            width=0,
        )
    fs_name = st.session_state.fs_station
    fs_pt = next(
        (p for p in store["monitoring_points"] if p["name"] == fs_name), None
    )
    if fs_pt is None:
        st.session_state.pop("fs_station", None)
        st.rerun()
    else:
        fs_val = fs_pt["val"]
        fs_min = fs_pt.get("min_limit", 100.0)
        fs_max = fs_pt.get("max_limit", 350.0)
        fs_crit = fs_val < fs_min or fs_val > fs_max
        fs_color = "#ef4444" if fs_crit else "#22c55e"
        fs_bg = "#26090d" if fs_crit else "#03130d"
        fs_status = (
            f"CRITICAL - out of bounds ({fs_min} - {fs_max} PPM)"
            if fs_crit
            else f"SAFE ZONE - Normal limits ({fs_min} - {fs_max} PPM)"
        )
        fs_coil = ""
        if "ROD" in fs_name.upper() and (
            fs_pt.get("coil_prefix") or fs_pt.get("coil_num")
        ):
            fs_coil = f"<div style='font-size:32px;color:#7dd3fc;font-weight:700;margin-bottom:8px;'>Coil: {fs_pt.get('coil_prefix','')}-{fs_pt.get('coil_num','')}</div>"
        st.markdown(
            """<style>
            section[data-testid="stSidebar"]{display:none !important;}
            header[data-testid="stHeader"]{display:none !important;}
            header{display:none !important;}
            [data-testid="stHeader"]{display:none !important;}
            [data-testid="stToolbar"]{display:none !important;}
            div[data-testid="stToolbar"]{display:none !important;}
            </style>""",
            unsafe_allow_html=True,
        )
        # NOTE: single-line HTML (no blank lines / indentation) so the markdown
        # renderer never treats the value divs as a code block when fs_coil is empty.
        fs_html = (
            '<div style="min-height:82vh;display:flex;flex-direction:column;align-items:center;justify-content:center;'
            f'background:{fs_bg};border:6px solid {fs_color};border-radius:24px;margin:6px;padding:20px 12px;text-align:center;">'
            f'<div style="font-size:44px;font-weight:800;color:#ffffff;margin-bottom:4px;">{fs_name}</div>'
            f"{fs_coil}"
            f'<div style="font-size:21vw;line-height:1.05;color:{fs_color};font-weight:900;">{fs_val:.2f}</div>'
            f'<div style="font-size:52px;color:{fs_color};font-weight:800;">PPM</div>'
            f'<div style="font-size:24px;color:#e5e7eb;margin-top:10px;">{fs_status}</div>'
            f'<div style="font-size:18px;color:#9ca3af;margin-top:6px;">Last Updated: {fs_pt.get("last_updated", get_pkt_time())} (PKT)</div>'
            "</div>"
        )
        st.markdown(fs_html, unsafe_allow_html=True)
        fs_b1, fs_b2 = st.columns(2)
        with fs_b1:
            if st.button("Refresh", key="fs_refresh", use_container_width=True):
                st.rerun()
        with fs_b2:
            if st.button(
                "X Exit Full Screen",
                key="fs_exit",
                use_container_width=True,
                type="primary",
            ):
                st.session_state.pop("fs_station", None)
                st.rerun()
        st.stop()


# Header Section
head_col1, head_col2 = st.columns([1, 6])
with head_col1:
    if store.get("logo_image"):
        st.image(store["logo_image"], width=80)
    elif PCL_LOGO_B64:
        st.markdown(
            f"""<img src="data:image/png;base64,{PCL_LOGO_B64}" style="width:78px;height:78px;object-fit:contain;filter:drop-shadow(0 2px 8px rgba(0,0,0,.6));">""",
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            """<div style="background: #1f2937; width: 70px; height: 70px; border-radius: 12px; display: flex; align-items: center; justify-content: center; border: 2px solid #38bdf8;"><span style="color: #10b981; font-size: 18px; font-weight: bold;">PCL</span></div>""",
            unsafe_allow_html=True,
        )

with head_col2:
    st.markdown(
        f"<h2 style='margin:0;'>{store['app_title']}</h2>", unsafe_allow_html=True
    )
    st.markdown(
        f"<p style='color: #c7d2e4; font-size: 13px;'><em>{store['app_subtitle']}</em></p>",
        unsafe_allow_html=True,
    )

st.markdown("---")

# JavaScript Audio Generators
if play_audio:
    if not st.session_state.get("fs_station"):
        st.error(
            f"🚨 CRITICAL ALARM ACTIVE ({sound_type}): {', '.join(critical_stations)} limits exceeded!"
        )
    alarm_script = f"""
    <script>
    var ctx = new (window.AudioContext || window.webkitAudioContext)();
    function playAlarm() {{
        {current_js}
    }}
    var intervalId = setInterval(playAlarm, 700);
    </script>
    """
    st.components.v1.html(alarm_script, height=0, width=0)

st.markdown("### Select Monitoring Station (Full Display View)")

# Tabs Selection for Station Display
station_names = [pt["name"] for pt in store["monitoring_points"]]
station_tabs = st.tabs(station_names)

for idx, tab in enumerate(station_tabs):
    with tab:
        pt = store["monitoring_points"][idx]
        s_name = pt["name"]
        val = pt["val"]
        min_l = pt.get("min_limit", 100.0)
        max_l = pt.get("max_limit", 350.0)
        last_t = pt.get("last_updated", get_pkt_time())
        is_critical = val < min_l or val > max_l

        border_color = "#ef4444" if is_critical else "#10b981"
        bg_color = "#1f1215" if is_critical else "#062319"

        st.markdown(
            f"""
        <div style="background-color: {bg_color}; border: 3px solid {border_color}; border-radius: 16px; padding: 25px; text-align: center; margin-bottom: 15px;">
            <h1 style="color: white; margin: 0; font-size: 36px;">{s_name}</h1>
        </div>
        """,
            unsafe_allow_html=True,
        )

        if "ROD" in s_name.upper() and (
            pt.get("coil_prefix") or pt.get("coil_num")
        ):
            st.markdown(
                f"<div style='text-align: center; color: #38bdf8; font-size: 30px; font-weight: 700; margin: 2px 0;'>📦 Coil: {pt.get('coil_prefix', '')}-{pt.get('coil_num', '')}</div>",
                unsafe_allow_html=True,
            )

        val_color = "#ef4444" if is_critical else "#10b981"
        st.markdown(
            f"<h2 style='text-align: center; color: #ffffff; font-size: 46px; margin: 2px 0 0 0; font-weight: 800;'>{s_name}</h2>",
            unsafe_allow_html=True,
        )
        st.markdown(
            f"<h1 style='text-align: center; color: {val_color}; font-size: 112px; margin: 10px 0; font-weight: 900;'>{val:.2f} <span style='font-size: 42px;'>PPM</span></h1>",
            unsafe_allow_html=True,
        )

        if is_critical:
            st.error(
                f"🚨 CRITICAL ALERT — Value out of safe bounds ({min_l} - {max_l} PPM)"
            )
        else:
            st.success(f"🟢 SAFE ZONE — Normal limits ({min_l} - {max_l} PPM)")

        st.caption(f"🕒 Last Updated: {last_t} (PKT)")

        if st.button(
            f"⛶ Full Screen ({s_name})",
            key=f"fs_open_{idx}",
            use_container_width=True,
        ):
            st.session_state.fs_station = s_name
            st.rerun()

        if is_critical:
            is_muted = st.session_state.muted_stations.get(s_name, False)
            if not is_muted:
                if st.button(
                    f"🔕 Mute Alarm ({s_name})",
                    key=f"tab_mute_{idx}",
                    use_container_width=True,
                    type="primary",
                ):
                    st.session_state.muted_stations[s_name] = True
                    st.rerun()
            else:
                if st.button(
                    f"🔔 Unmute Alarm ({s_name})",
                    key=f"tab_unmute_{idx}",
                    use_container_width=True,
                ):
                    st.session_state.muted_stations[s_name] = False
                    st.rerun()

st.markdown("---")
st.markdown("### 📝 Operations Panel")

# Role Based Tab Generation
op_tabs_list = ["⚡ Update Readings", "📊 Log History"]
if is_admin:
    op_tabs_list.extend(
        [
            "🔊 Alarm Sound Settings",
            "⚙️ Admin: Manage Limits",
            "👥 User Management",
        ]
    )

tabs_op = st.tabs(op_tabs_list)

# Tab 1: Update Readings (Both Admin and Operator)
with tabs_op[0]:
    st.subheader("Update Live Sensor Reading & Coil Information")
    selected_edit_idx = st.selectbox(
        "Select Monitoring Point",
        options=range(len(station_names)),
        format_func=lambda x: station_names[x],
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

# Tab 2: Log History (Both Admin and Operator)
with tabs_op[1]:
    st.subheader("📊 Log History & Saved Records")

    if sheets_autosave_on(store.get("google_sheet_url", "")):
        st.caption("🟢 Google Sheets auto-save: ON")
    else:
        st.caption("⚪ Google Sheets auto-save: OFF (webhook URL not configured - see README.md)")

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

# Admin Only Tabs
if is_admin:
    # Sound Settings
    with tabs_op[2]:
        st.subheader("🔊 Select Loud Alarm Sound")
        sound_options = list(sound_scripts.keys())
        current_selected = store.get(
            "selected_alarm_sound", "Jail Siren (Wail)"
        )

        chosen_sound = st.radio(
            "Choose Alarm Tone Type:",
            options=sound_options,
            index=(
                sound_options.index(current_selected)
                if current_selected in sound_options
                else 0
            ),
        )

        col_s1, col_s2 = st.columns(2)
        with col_s1:
            if st.button("🔊 Test Selected Sound"):
                test_js = sound_scripts[chosen_sound]
                st.components.v1.html(
                    f"<script>var ctx = new (window.AudioContext || window.webkitAudioContext)(); {test_js}</script>",
                    height=0,
                    width=0,
                )
                st.toast(f"Testing sound: {chosen_sound}")

        with col_s2:
            if st.button("💾 Save Sound Setting", type="primary"):
                store["selected_alarm_sound"] = chosen_sound
                save_store()
                st.success(f"Alarm sound set to: {chosen_sound}")
                st.rerun()

    # Manage Limits
    with tabs_op[3]:
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

    # User Management
    with tabs_op[4]:
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
