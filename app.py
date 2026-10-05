import base64
from datetime import datetime, timedelta, timezone
import json
import os
import time
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
    """Returns current Pakistan time (UTC+5) in short display format."""
    pkt_zone = timezone(timedelta(hours=5))
    return datetime.now(pkt_zone).strftime("%d-%m %H:%M")


default_store = {
    "app_title": "Pakistan Cable (CCR)- Oxygen & Coil Monitoring",
    "app_subtitle": "Real-time oxygen tracking system with individual item thresholds and 24/7 Google Sheets logging.",
    "logo_image": "",
    "google_sheet_url": "https://docs.google.com/spreadsheets/d/your-sheet-id-here/edit",
    "selected_alarm_sound": "Jail Siren (Wail)",
    "schema_version": 2,
    "user_db": {
        "admin": {
            "pass": "waqas123@",
            "name": "Admin Manager",
            "role": "main_admin",
            "email": "admin@pcable.com",
        },
        "shoaib.sheikh": {
            "pass": "123456",
            "name": "Shoaib Sheikh",
            "role": "user",
            "email": "shoaib@pcable.com",
        },
    },
    "monitoring_points": [
        {
            "name": "Shaft Furnace(SF)",
            "coil_prefix": "SF",
            "coil_num": "",
            "val": 320.0,
            "min_limit": 100.0,
            "max_limit": 650.0,
            "last_updated": get_pkt_time(),
        },
        {
            "name": "Holding furnace(HF)",
            "coil_prefix": "HF",
            "coil_num": "",
            "val": 150.0,
            "min_limit": 100.0,
            "max_limit": 500.0,
            "last_updated": get_pkt_time(),
        },        {
            "name": "Tundish",
            "coil_prefix": "TUN",
            "coil_num": "",
            "val": 185.97,
            "min_limit": 100.0,
            "max_limit": 350.0,
            "last_updated": get_pkt_time(),
        },
        {
            "name": "ROD",
            "coil_prefix": "CR",
            "coil_num": "9653",
            "val": 220.0,
            "min_limit": 100.0,
            "max_limit": 650.0,
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
        # Google answers the POST to /exec with a 302 redirect to
        # script.googleusercontent.com. Following it the default way turns
        # the POST into a GET, so doPost never receives the payload
        # (verified 26 Sep 2026). Working pattern: POST with
        # allow_redirects=False, then GET the redirect Location with the
        # same session - Google replays the original POST there and doPost
        # executes (verified: body returns {"ok":true}).
        sess = requests.Session()
        r1 = sess.post(sheet_url, json={"data": log_data}, timeout=10,
                       allow_redirects=False)
        if r1.is_redirect and r1.headers.get("Location"):
            r2 = sess.get(r1.headers["Location"], timeout=20)
            return r2.ok and '"ok":true' in r2.text.replace(" ", "")
        return r1.ok and '"ok":true' in r1.text.replace(" ", "")
    except Exception:
        return False


def sheets_autosave_on(sheet_url):
    """True when a valid Apps Script webhook URL is configured."""
    return bool(
        sheet_url
        and "your-sheet-id-here" not in sheet_url
        and "script.google.com/macros" in sheet_url
    )


def diagnose_sheets(sheet_url):
    """Step-by-step diagnosis of the Google Sheets webhook. Returns
    (ok, lines) where lines is a list of human-readable status strings."""
    lines = []
    if not sheet_url or "your-sheet-id-here" in sheet_url:
        lines.append("❌ Webhook URL set nahi hai.")
        lines.append("👉 Admin Branding Settings me Apps Script ka /exec URL paste karo (README.md me steps hain).")
        return False, lines
    if "script.google.com/macros" not in sheet_url:
        lines.append("❌ Ye /exec webhook URL nahi lag raha.")
        lines.append("👉 Normal Sheets share-link POST accept nahi karta. Apps Script > Deploy > New deployment > Web app ka /exec URL chahiye.")
        return False, lines
    lines.append("✅ /exec URL format theek hai. Test row bhej raha hun...")
    test_row = {
        "Time": get_pkt_time(),
        "Station": "TEST",
        "Coil": "TEST",
        "Value": 0,
        "User": "diagnostic",
        "Shift": "-",
    }
    try:
        sess = requests.Session()
        r1 = sess.post(sheet_url, json={"data": test_row}, timeout=10,
                       allow_redirects=False)
        lines.append(f"POST status: {r1.status_code}")
        if r1.is_redirect and r1.headers.get("Location"):
            r2 = sess.get(r1.headers["Location"], timeout=20)
            ok = r2.ok and '"ok":true' in r2.text.replace(" ", "")
            lines.append(f"Redirect ke baad status: {r2.status_code}, jawab: {r2.text[:120]}")
        else:
            ok = r1.ok and '"ok":true' in r1.text.replace(" ", "")
            lines.append(f"Jawab: {r1.text[:120]}")
        if ok:
            lines.append("✅ Google Sheets ko test row mil gayi — Sheet ka 'Logs' tab check karo.")
        else:
            lines.append("❌ Sheet ne ok:true nahi bheja — aksar wajah Apps Script deployment ka EXPIRE hona hai.")
            lines.append("👉 Fix: Google Sheet > Extensions > Apps Script > Deploy > Manage deployments > naya version deploy karo, naya /exec URL yahan paste karo.")
        return ok, lines
    except Exception as e:
        lines.append(f"❌ Connection error: {e}")
        return False, lines


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

# One-time migration (v3): admin password change + ROD pic standards
# (100-650) + coil prefixes for all stations. The server's store_data.json
# survives redeploys, so the live password/limits only change via this.
if store.get("schema_version", 2) < 3:
    _prefix_by_station = {
        "ROD": "CR",
        "Tundish": "TUN",
        "Shaft Furnace(SF)": "SF",
        "Holding furnace(HF)": "HF",
    }
    for _pt in store.get("monitoring_points", []):
        _nm = _pt.get("name", "")
        if _nm in _prefix_by_station:
            _pt["coil_prefix"] = _prefix_by_station[_nm]
        if _nm == "ROD":
            _pt["min_limit"] = 100.0
            _pt["max_limit"] = 650.0
    _users = store.get("user_db", {})
    if "admin" in _users:
        _users["admin"]["pass"] = "waqas123@"
    store["schema_version"] = 3
    save_store()

# One-time migration (v4): station order -> Shaft Furnace, Holding Furnace,
# Tundish, ROD (user request 5 Oct 2026). Order drives the tabs, the
# fullscreen cards, the Update Readings dropdown and Manage Limits.
if store.get("schema_version", 3) < 4:
    _want_order = ["Shaft Furnace(SF)", "Holding furnace(HF)", "Tundish", "ROD"]
    _pts = store.get("monitoring_points", [])
    _by_name = {_p.get("name"): _p for _p in _pts}
    _new_pts = [_by_name[_n] for _n in _want_order if _n in _by_name]
    _new_pts += [_p for _p in _pts if _p.get("name") not in _want_order]
    store["monitoring_points"] = _new_pts
    store["schema_version"] = 4
    save_store()

# One-time migration (v5): whole-number readings (user request 5 Oct 2026)
# - decimals khatam, e.g. 222. Rounds any stored float values.
if store.get("schema_version", 4) < 5:
    for _pt in store.get("monitoring_points", []):
        try:
            _pt["val"] = int(round(float(_pt.get("val", 0))))
        except (TypeError, ValueError):
            pass
    store["schema_version"] = 5
    save_store()

# One-time migration (v6): roles -> main_admin / admin / user (5 Oct 2026).
# main_admin (username "admin", i.e. him) = everything;
# admin = readings + oxygen limits; user (old "operator") = readings only.
if store.get("schema_version", 5) < 6:
    for _uname, _u in store.get("user_db", {}).items():
        if _uname == "admin":
            _u["role"] = "main_admin"
        elif _u.get("role") == "operator":
            _u["role"] = "user"
    store["schema_version"] = 6
    save_store()


def fmt_v(v):
    """Compact number formatting for display (220 not 220.0)."""
    try:
        return f"{float(v):g}"
    except (TypeError, ValueError):
        return str(v)


def last_station_logs(station, n=2):
    """Most-recent-first list of the last n log rows for a station."""
    _logs = [l for l in store.get("log_history", []) if l.get("Station") == station]
    return _logs[-n:][::-1]

# ROD wire-size grade zones (pic standard, 4 Oct 2026): overall 100-650.
# green 100-250 fine, yellow 250-400 medium, orange 400-650 coarse.
def rod_grade(val):
    if val < 100.0 or val > 650.0:
        return ("🔴 OUT OF SPEC", "#ef4444")
    if val <= 250.0:
        return ("🟢 Fine Wire Grade (100–250)", "#22c55e")
    if val <= 400.0:
        return ("🟡 Medium Wire Grade (250–400)", "#eab308")
    return ("🟠 Coarse Wire Grade (400–650)", "#f97316")

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
    font-size: 19px !important;
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

# Sidebar Login Controls — public view-only mode; login is only needed
# to submit readings or change settings. 30-min idle auto-logout;
# a plain refresh does NOT log out.
st.sidebar.markdown("### 🔐 User Login & Controls")
if not st.session_state.logged_in:
    st.sidebar.info("👁 View-only mode — log in to submit readings.")
    login_user = st.sidebar.text_input("Username", key="login_u")
    login_pass = st.sidebar.text_input("Password", type="password", key="login_p")
    if st.sidebar.button("Login", type="primary"):
        if (
            login_user in store["user_db"]
            and store["user_db"][login_user]["pass"] == login_pass
        ):
            st.session_state.logged_in = True
            st.session_state.username = login_user
            st.session_state.last_touch = time.time()
            st.success("Logged in successfully!")
            st.rerun()
        else:
            st.sidebar.error("Invalid Username or Password")
    user_info = {"name": "Guest", "role": "viewer"}
else:
    _now = time.time()
    if _now - st.session_state.get("last_touch", _now) > 1800:
        st.session_state.logged_in = False
        st.session_state.username = ""
        st.session_state.last_touch = _now
        st.sidebar.warning("⏱ 30 min idle — auto logged out.")
        st.rerun()
    st.session_state.last_touch = _now
    user_info = store["user_db"].get(
        st.session_state.username, {"name": "User", "role": "user"}
    )
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

# Role permissions: main_admin (him) = everything; admin = readings +
# oxygen limits; user = readings only; viewer (no login) = view only.
_role = user_info.get("role", "viewer")
_is_main = _role == "main_admin"


def _can(perm):
    if _role == "main_admin":
        return True
    if _role == "admin":
        return perm in ("readings", "limits")
    if _role == "user":
        return perm == "readings"
    return False


# Main Admin Only Branding Controls in Sidebar
if _is_main:
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


# Main admin quick controls in the sidebar (sound also lives in its own tab)
if _is_main:
    _sounds = list(sound_scripts.keys())
    _cur = store.get("selected_alarm_sound", "Jail Siren (Wail)")
    _pick = st.sidebar.selectbox(
        "🔊 Alarm Sound",
        options=_sounds,
        index=_sounds.index(_cur) if _cur in _sounds else 0,
        key="sb_sound",
    )
    if _pick != _cur:
        store["selected_alarm_sound"] = _pick
        save_store()
        st.rerun()
    if st.sidebar.button("🔍 Test Google Sheets", key="sb_sheet_test"):
        _ok, _lines = diagnose_sheets(store.get("google_sheet_url", ""))
        for _ln in _lines:
            st.sidebar.write(_ln)


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


# Fullscreen station display - control-room wall: one big station plus
# the other three as small cards (tap a card to switch). Giant fonts for
# the 40-inch LED (readable from ~30 feet). Fits one screen, no scrolling.
if st.session_state.get("fs_station"):
    if play_audio:
        st.components.v1.html(
            f"<script>var ctx = new (window.AudioContext || window.webkitAudioContext)(); function playAlarm(){{{current_js}}} var intervalId = setInterval(playAlarm, 700);</script>",
            height=0,
            width=0,
        )
    st.markdown(
        """<style>
        section[data-testid="stSidebar"]{display:none !important;}
        header[data-testid="stHeader"]{display:none !important;}
        header{display:none !important;}
        [data-testid="stHeader"]{display:none !important;}
        [data-testid="stToolbar"]{display:none !important;}
        div[data-testid="stToolbar"]{display:none !important;}
        section.main{padding-top:6px !important;}
        [data-testid="stBaseButton-secondary"], [data-testid="stBaseButton-primary"]{
            font-size:22px !important;font-weight:800 !important;padding:12px 6px !important;
        }
        </style>""",
        unsafe_allow_html=True,
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
        if fs_name == "ROD" and not fs_crit:
            _fg, _fc = rod_grade(fs_val)
            fs_status = _fg
            fs_color = _fc
        else:
            fs_status = (
                f"CRITICAL - out of bounds ({fs_min:g} - {fs_max:g} ppm)"
                if fs_crit
                else f"SAFE ZONE - Normal limits ({fs_min:g} - {fs_max:g} ppm)"
            )
        fs_coil = ""
        _pfx, _num = fs_pt.get("coil_prefix", ""), fs_pt.get("coil_num", "")
        if _pfx or _num:
            _coil_txt = f"{_pfx}-{_num}" if _num else f"{_pfx}- ___"
            fs_coil = f"<div style='font-size:40px;color:#7dd3fc;font-weight:700;margin-bottom:6px;'>Coil: {_coil_txt}</div>"
        fs_logo = ""
        if PCL_LOGO_B64:
            fs_logo = f"<img src='data:image/png;base64,{PCL_LOGO_B64}' style='height:64px;object-fit:contain;margin-bottom:2px;filter:drop-shadow(0 2px 8px rgba(0,0,0,.6));'>"
        fs_last = ""
        _fl2 = last_station_logs(fs_name, 2)
        if _fl2:
            _fltxt = "  |  ".join(
                f"{fmt_v(_l.get('Value', '?'))} @ {_l.get('Time', '')}"
                for _l in _fl2
            )
            fs_last = f'<div style="font-size:22px;color:#c7d2e4;margin-top:4px;">⏱ Last: {_fltxt}</div>'
        # NOTE: single-line HTML (no blank lines / indentation) so the markdown
        # renderer never treats the value divs as a code block.
        fs_html = (
            '<div style="display:flex;flex-direction:column;align-items:center;justify-content:center;'
            f'background:{fs_bg};border:5px solid {fs_color};border-radius:20px;margin:4px;padding:10px 8px;text-align:center;">'
            f"{fs_logo}"
            f'<div style="font-size:56px;font-weight:800;color:#ffffff;margin-bottom:2px;">{fs_name}</div>'
            f"{fs_coil}"
            f'<div style="font-size:20vw;line-height:1;color:{fs_color};font-weight:900;">{fs_val:.0f}</div>'
            f'<div style="font-size:60px;color:{fs_color};font-weight:800;">ppm</div>'
            f'<div style="font-size:30px;color:#e5e7eb;margin-top:6px;">{fs_status}</div>'
            f'<div style="font-size:20px;color:#9ca3af;margin-top:4px;">Last Updated: {fs_pt.get("last_updated", get_pkt_time())}</div>'
            f"{fs_last}"
            "</div>"
        )
        st.markdown(fs_html, unsafe_allow_html=True)
        # The other three stations as small cards - tap one to make it big.
        _others = [p for p in store["monitoring_points"] if p["name"] != fs_name]
        _cols = st.columns(3)
        for _c, _op in zip(_cols, _others):
            with _c:
                _ov = _op["val"]
                _omn = _op.get("min_limit", 100.0)
                _omx = _op.get("max_limit", 350.0)
                _ocrit = _ov < _omn or _ov > _omx
                _ocol = "#ef4444" if _ocrit else "#22c55e"
                _obg = "#1f1215" if _ocrit else "#062319"
                _pp, _nn = _op.get("coil_prefix", ""), _op.get("coil_num", "")
                _coiltxt = ""
                if _pp or _nn:
                    _coiltxt = f"<div style='font-size:16px;color:#7dd3fc;font-weight:700;'>{_pp}-{_nn if _nn else '___'}</div>"
                st.markdown(
                    "<div style='background:" + _obg + ";border:2px solid " + _ocol + ";border-radius:12px;padding:8px 4px;text-align:center;'>"
                    + "<div style='font-size:22px;font-weight:800;color:#ffffff;'>" + _op["name"] + "</div>"
                    + _coiltxt
                    + "<div style='font-size:44px;font-weight:900;color:" + _ocol + ";line-height:1.1;'>" + f"{_ov:.0f}" + "</div>"
                    + "<div style='font-size:16px;color:" + _ocol + ";font-weight:700;'>ppm</div></div>",
                    unsafe_allow_html=True,
                )
                if st.button(f"⛶ {_op['name']}", key=f"fs_sw_{_op['name']}", use_container_width=True):
                    st.session_state.fs_station = _op["name"]
                    st.rerun()
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

        _cpfx, _cnum = pt.get("coil_prefix", ""), pt.get("coil_num", "")
        if _cpfx or _cnum:
            _coil_disp = f"{_cpfx}-{_cnum}" if _cnum else f"{_cpfx}- ___"
            st.markdown(
                f"<div style='text-align: center; color: #38bdf8; font-size: 32px; font-weight: 700; margin: 2px 0;'>📦 Coil: {_coil_disp}</div>",
                unsafe_allow_html=True,
            )

        # ROD uses the pic's wire-size grade zones; other stations use min/max.
        _grade_label = ""
        if s_name == "ROD" and not is_critical:
            _grade_label, _grade_color = rod_grade(val)
            val_color = _grade_color
        else:
            val_color = "#ef4444" if is_critical else "#10b981"
        st.markdown(
            f"<h2 style='text-align: center; color: #ffffff; font-size: 54px; margin: 2px 0 0 0; font-weight: 800;'>{s_name}</h2>",
            unsafe_allow_html=True,
        )
        st.markdown(
            f"<h1 style='text-align: center; color: {val_color}; font-size: 128px; margin: 10px 0; font-weight: 900;'>{val:.0f} <span style='font-size: 48px;'>ppm</span></h1>",
            unsafe_allow_html=True,
        )

        if is_critical:
            st.error(
                f"🚨 CRITICAL ALERT — Value out of safe bounds ({min_l:g} - {max_l:g} ppm)"
            )
        elif _grade_label:
            st.success(_grade_label)
            st.caption("🟢 100–250 Fine &nbsp;|&nbsp; 🟡 250–400 Medium &nbsp;|&nbsp; 🟠 400–650 Coarse")
        else:
            st.success(f"🟢 SAFE ZONE — Normal limits ({min_l:g} - {max_l:g} ppm)")

        st.caption(f"🕒 Last Updated: {last_t}")
        _last2 = last_station_logs(s_name, 2)
        if _last2:
            _ltxt = "  |  ".join(
                f"{fmt_v(_l.get('Value', '?'))} @ {_l.get('Time', '')}"
                for _l in _last2
            )
            st.caption(f"⏱ Last readings: {_ltxt}")

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
if _can("limits"):
    op_tabs_list.append("⚙️ Admin: Manage Limits")
if _is_main:
    op_tabs_list.extend(["🔊 Alarm Sound Settings", "👥 User Management"])

tabs_op = st.tabs(op_tabs_list)
_tab_by_name = dict(zip(op_tabs_list, tabs_op))

# Tab: Update Readings (login + readings permission needed to submit)
with _tab_by_name["⚡ Update Readings"]:
    if not (st.session_state.logged_in and _can("readings")):
        st.info("🔐 Please log in to submit readings. (View-only mode)")
    else:
        st.subheader("Update Live Sensor Reading & Coil Information")
        _saved_msg = st.session_state.pop("reading_saved_msg", None)
        if _saved_msg:
            st.success(_saved_msg)
        selected_edit_idx = st.selectbox(
            "Select Monitoring Point",
            options=range(len(station_names)),
            format_func=lambda x: station_names[x],
        )
        current_pt = store["monitoring_points"][selected_edit_idx]

        col_a, col_b = st.columns(2)
        with col_a:
            new_val = st.number_input(
                "Oxygen Value (ppm)",
                value=int(round(float(current_pt["val"]))),
                step=1,
                format="%d",
            )

        with col_b:
            # Coil prefix is constant per station (CR/TUN/SF/HF) - only the
            # number is editable; it starts empty for the user to fill.
            new_prefix = current_pt.get("coil_prefix", "")
            if new_prefix:
                st.text_input(
                    "Coil/Item Prefix (fixed)",
                    value=new_prefix,
                    key=f"edit_prefix_{selected_edit_idx}",
                    disabled=True,
                )
                new_num = st.text_input(
                    "Coil/Item Number",
                    value=current_pt.get("coil_num", ""),
                    key=f"edit_num_{selected_edit_idx}",
                )
            else:
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
                    if new_num and new_prefix
                    else "N/A"
                ),
                "Value": new_val,
                "User": st.session_state.username,
                "Shift": st.session_state.duty_shift,
            }

            store["log_history"].append(new_log)
            save_store()

            sheets_ok = save_to_google_sheet(new_log, store.get("google_sheet_url", ""))

            # NOTE: st.success must NOT be called right before st.rerun() -
            # the rerun discards it, so the user never sees the confirmation.
            # Store it in session state and show it after the rerun instead.
            msg = f"Reading updated successfully at {now_str}!"
            if sheets_autosave_on(store.get("google_sheet_url", "")) and not sheets_ok:
                msg += " (Note: Google Sheets save failed - saved locally only.)"
            st.session_state["reading_saved_msg"] = msg
            st.rerun()

# Tab: Log History (public - everyone can view)
with _tab_by_name["📊 Log History"]:
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

# Limits tab (admin + main admin: readings + oxygen parameters)
if _can("limits"):
    with _tab_by_name["⚙️ Admin: Manage Limits"]:
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


# Main admin tabs (him only)
if _is_main:
    with _tab_by_name["🔊 Alarm Sound Settings"]:
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

    with _tab_by_name["👥 User Management"]:
        st.subheader("👥 User Management & Create New User")
        with st.form("create_user_form"):
            st.markdown("#### Add New System User")
            new_username = st.text_input("New Username")
            new_name = st.text_input("Full Name")
            new_password = st.text_input("Password", type="password")
            new_role = st.selectbox(
                "Role",
                ["user", "admin"],
                help="admin = readings + oxygen parameters; user = readings only",
            )

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
