import base64
from datetime import datetime
import json
import os
import pandas as pd
import streamlit as st
import streamlit.components.v1 as components

# Set Page Config
st.set_page_config(
    page_title="Pakistan Cable (CCR) - Oxygen & Coil Monitoring",
    page_icon="🏭",
    layout="wide",
    initial_sidebar_state="expanded",
)

DATA_FILE = "store_data.json"

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
            "last_updated": datetime.now().strftime("%Y-%m-%d %I:%M:%S %p"),
        },
        {
            "name": "Tundish",
            "coil_prefix": "",
            "coil_num": "",
            "val": 185.97,
            "min_limit": 100.0,
            "max_limit": 350.0,
            "last_updated": datetime.now().strftime("%Y-%m-%d %I:%M:%S %p"),
        },
        {
            "name": "Shaft Furnace(SF)",
            "coil_prefix": "",
            "coil_num": "",
            "val": 0.0,
            "min_limit": 100.0,
            "max_limit": 650.0,
            "last_updated": datetime.now().strftime("%Y-%m-%d %I:%M:%S %p"),
        },
        {
            "name": "Holding furnace(HF)",
            "coil_prefix": "",
            "coil_num": "",
            "val": 450.0,
            "min_limit": 100.0,
            "max_limit": 500.0,
            "last_updated": datetime.now().strftime("%Y-%m-%d %I:%M:%S %p"),
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


if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "username" not in st.session_state:
    st.session_state.username = ""
if "duty_shift" not in st.session_state:
    st.session_state.duty_shift = "Shift A"
if "muted_stations" not in st.session_state:
    st.session_state.muted_stations = {}

# CSS Styling
st.markdown(
    """
<style>
.stApp { background-color: #0F172A; color: white; }
.main-card {
    background-color: #1e293b;
    border: 1px solid rgba(255, 255, 255, 0.15);
    border-radius: 12px;
    padding: 25px;
    margin-bottom: 20px;
    color: white;
    box-shadow: 0 4px 15px rgba(0,0,0,0.4);
}
.card-title { font-weight: 700; font-size: 26px; margin-bottom: 8px; color: #ffffff; text-align: center; }
.card-coil { font-weight: 600; font-size: 18px; margin-bottom: 12px; color: #38bdf8; text-align: center; }
.card-val-green { font-size: 68px; font-weight: 900; color: #2ecc71; text-align: center; margin: 15px 0; }
.card-val-red { font-size: 68px; font-weight: 900; color: #e74c3c; text-align: center; margin: 15px 0; }
.badge-safe { background-color: rgba(46, 204, 113, 0.2); color: #2ecc71; padding: 8px 16px; border-radius: 20px; font-weight: bold; font-size: 15px; display: inline-block; }
.badge-critical { background-color: rgba(231, 76, 60, 0.2); color: #e74c3c; padding: 8px 16px; border-radius: 20px; font-weight: bold; font-size: 15px; display: inline-block; }
.card-timestamp { color: #94a3b8; font-size: 14px; text-align: center; margin-top: 15px; border-top: 1px solid rgba(255, 255, 255, 0.1); padding-top: 10px; }
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

# Admin Settings in Sidebar
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
        "Google Sheet URL", value=store.get("google_sheet_url", "")
    )
    if st.button("Save Sheet URL"):
        store["google_sheet_url"] = new_sheet_url
        save_store()
        st.success("Google Sheet URL updated!")
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
        st.image(store["logo_image"], width=120)
    else:
        st.markdown(
            """<div style="background: #1e293b; width: 100px; height: 100px; border-radius: 12px; display: flex; align-items: center; justify-content: center; border: 2px solid #38bdf8;"><span style="color: #2ecc71; font-size: 24px; font-weight: bold;">PCL</span></div>""",
            unsafe_allow_html=True,
        )

with head_col2:
    st.markdown(f"<h1>{store['app_title']}</h1>", unsafe_allow_html=True)
    st.markdown(
        f"<p style='color: #cbd5e1; font-size: 16px;'><em>{store['app_subtitle']}</em></p>",
        unsafe_allow_html=True,
    )

st.markdown("---")

# Alarm Condition Check (Including 0 value if out of min/max range)
play_audio = False
critical_stations = []

for pt in store["monitoring_points"]:
    s_name = pt["name"]
    val = pt["val"]
    min_l = pt.get("min_limit", 100.0)
    max_l = pt.get("max_limit", 350.0)

    # FIXED: 0 is checked against min_limit/max_limit as well
    if val < min_l or val > max_l:
        critical_stations.append(s_name)
        if not st.session_state.muted_stations.get(s_name, False):
            play_audio = True

# Sound Player with Auto-retry JavaScript
if play_audio:
    st.error(
        f"🚨 CRITICAL ALERT ({', '.join(critical_stations)}): Oxygen value out of range! Alarm active."
    )
    audio_url = (
        "https://www.quicksounds.com/uploads/tracks/1865913508_1928092284_ext.mp3"
    )

    # JS Code to bypass browser autoplay restrictions
    sound_js = f"""
    <script>
    var audio = new Audio('{audio_url}');
    audio.loop = true;
    audio.play().catch(function(error) {{
        console.log("Autoplay prevented. Waiting for click.");
        document.addEventListener('click', function() {{
            audio.play();
        }}, {{ once: true }});
    }});
    </script>
    <div style="padding: 10px; background-color: #7f1d1d; color: white; border-radius: 8px; text-align: center; margin-bottom: 10px;">
        🔊 <b>Alarm Triggered!</b> If sound is blocked by browser, click anywhere on the page to start sound.
    </div>
    """
    components.html(sound_js, height=60)

# View Mode Selection
st.markdown(
    "<h4 style='color: #38bdf8;'>🔍 Select View Mode</h4>",
    unsafe_allow_html=True,
)
view_options = ["Show All Cards"] + [
    p["name"] for p in store["monitoring_points"]
]
selected_view = st.selectbox(
    "Choose station view mode:",
    options=view_options,
    label_visibility="collapsed",
)

# Display Cards
cols = st.columns(len(store["monitoring_points"]))
for idx, pt in enumerate(store["monitoring_points"]):
    with cols[idx]:
        s_name = pt["name"]
        val = pt["val"]
        min_l = pt.get("min_limit", 100.0)
        max_l = pt.get("max_limit", 350.0)
        last_t = pt.get(
            "last_updated", datetime.now().strftime("%Y-%m-%d %I:%M:%S %p")
        )

        coil_html = ""
        if s_name.upper() == "ROD" and (
            pt.get("coil_prefix") or pt.get("coil_num")
        ):
            coil_html = f'<div class="card-coil">📦 Item/Coil: {pt.get("coil_prefix", "")}-{pt.get("coil_num", "")}</div>'

        # FIXED logic: Check value strictly against min and max
        is_critical = val < min_l or val > max_l

        if is_critical:
            status_label, val_class, badge_class, sub_desc = (
                "CRITICAL ALERT",
                "card-val-red",
                "badge-critical",
                "Out of safe range!",
            )
        else:
            status_label, val_class, badge_class, sub_desc = (
                "SAFE ZONE",
                "card-val-green",
                "badge-safe",
                "Normal safe range.",
            )
            st.session_state.muted_stations[s_name] = False

        card_html = f'<div class="main-card"><div class="card-title">{s_name}</div>{coil_html}<div class="{val_class}" style="font-size: 52px;">{val:.2f} <span style="font-size:20px;">ppm</span></div><div style="text-align: center;"><span class="{badge_class}">● {status_label}</span><div style="color: #94a3b8; font-size: 12px; margin-top: 8px;">{sub_desc}</div></div><div class="card-timestamp">🕒 {last_t}</div></div>'
        st.markdown(card_html, unsafe_allow_html=True)

        if is_critical:
            is_muted = st.session_state.muted_stations.get(s_name, False)
            if not is_muted:
                if st.button(
                    f"🔕 Mute Alarm ({s_name})",
                    key=f"mute_{idx}",
                    use_container_width=True,
                ):
                    st.session_state.muted_stations[s_name] = True
                    st.rerun()
            else:
                if st.button(
                    f"🔔 Unmute Alarm ({s_name})",
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
        now_str = datetime.now().strftime("%Y-%m-%d %I:%M:%S %p")
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
        }
        store["log_history"].append(new_log)
        save_store()

        st.success(
            f"Successfully updated {current_pt['name']} to {new_val:.2f} ppm at {now_str}!"
        )
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
    st.subheader("📊 Log History & Google Sheets Access")

    if store["log_history"]:
        df_logs = pd.DataFrame(store["log_history"])
        st.dataframe(df_logs, use_container_width=True)
    else:
        st.info("No logs recorded yet.")
