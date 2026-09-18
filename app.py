import base64
from datetime import datetime
import json
import os
import pandas as pd
import streamlit as st

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
            "coil_num": "2002",
            "val": 876.0,
            "min_limit": 100.0,
            "max_limit": 350.0,
            "last_updated": datetime.now().strftime("%Y-%m-%d %I:%M:%S %p"),
        },
        {
            "name": "Tundish",
            "coil_prefix": "",
            "coil_num": "",
            "val": 476.0,
            "min_limit": 100.0,
            "max_limit": 350.0,
            "last_updated": datetime.now().strftime("%Y-%m-%d %I:%M:%S %p"),
        },
        {
            "name": "Shaft Furnace(SF)",
            "coil_prefix": "",
            "coil_num": "",
            "val": 200.0,
            "min_limit": 100.0,
            "max_limit": 650.0,
            "last_updated": datetime.now().strftime("%Y-%m-%d %I:%M:%S %p"),
        },
        {
            "name": "Holding furnace(HF)",
            "coil_prefix": "",
            "coil_num": "",
            "val": 0.0,
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

# CSS Styling with Extra Large Fonts
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

# Check which stations have critical alerts and manage sound per station
has_active_critical = False
play_audio = False

for pt in store["monitoring_points"]:
    s_name = pt["name"]
    val = pt["val"]
    min_l = pt.get("min_limit", 100.0)
    max_l = pt.get("max_limit", 350.0)

    if val > 0 and (val < min_l or val > max_l):
        has_active_critical = True
        # If this specific station is NOT muted, trigger sound
        if not st.session_state.muted_stations.get(s_name, False):
            play_audio = True

# Play the loud custom alarm audio if any unmuted station is critical
if play_audio:
    st.error(
        "🚨 CRITICAL ALERT: Oxygen value out of range! Continuous custom alarm ringing..."
    )
    # Embedding the exact requested loud audio sample (QuickSounds.com)
    st.markdown(
        """
        <audio autoplay loop>
          <source src="https://www.quicksounds.com/uploads/tracks/1865913508_1928092284_ext.mp3" type="audio/mpeg">
        </audio>
    """,
        unsafe_allow_html=True,
    )

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


# Helper function to render card with individual Mute/Unmute button
def render_station_card(pt):
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

    is_critical = val > 0 and (val < min_l or val > max_l)

    if val == 0.0:
        status_label, val_class, badge_class, sub_desc = (
            "NO DATA YET",
            "card-val-green",
            "badge-safe",
            "Awaiting reading.",
        )
    elif is_critical:
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
        # Reset mute for this station if it becomes safe
        st.session_state.muted_stations[s_name] = False

    card_div = f'<div class="main-card" style="padding: 35px;"><div class="card-title" style="font-size: 30px;">{s_name}</div>{coil_html}<div class="{val_class}">{val:.2f} <span style="font-size:26px;">ppm</span></div><div style="text-align: center;"><span class="{badge_class}" style="font-size: 18px; padding: 10px 22px;">● {status_label}</span><div style="color: #94a3b8; font-size: 16px; margin-top: 12px;">{sub_desc}</div></div><div class="card-timestamp" style="font-size: 15px;">🕒 Last Updated: {last_t}</div></div>'
    return card_div, is_critical


# Cards Display Layout
if selected_view == "Show All Cards":
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

            is_critical = val > 0 and (val < min_l or val > max_l)

            if val == 0.0:
                status_label, val_class, badge_class, sub_desc = (
                    "NO DATA YET",
                    "card-val-green",
                    "badge-safe",
                    "Awaiting reading.",
                )
            elif is_critical:
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

            # Individual Mute/Unmute Button under each card if critical
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
else:
    focused_pt = next(
        (p for p in store["monitoring_points"] if p["name"] == selected_view),
        None,
    )
    if focused_pt:
        s_name = focused_pt["name"]
        card_rendered, is_crit = render_station_card(focused_pt)
        st.markdown(card_rendered, unsafe_allow_html=True)
        if is_crit:
            is_muted = st.session_state.muted_stations.get(s_name, False)
            col_m1, col_m2 = st.columns([2, 4])
            with col_m1:
                if not is_muted:
                    if st.button(
                        f"🔕 Mute Alarm ({s_name})",
                        key="mute_focused",
                        use_container_width=True,
                    ):
                        st.session_state.muted_stations[s_name] = True
                        st.rerun()
                else:
                    if st.button(
                        f"🔔 Unmute Alarm ({s_name})",
                        key="unmute_focused",
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
        # Accurate real-time PKT timestamp (AM/PM 12-hour format)
        now_str = datetime.now().strftime("%Y-%m-%d %I:%M:%S %p")
        store["monitoring_points"][selected_edit_idx]["val"] = new_val
        store["monitoring_points"][selected_edit_idx][
            "coil_prefix"
        ] = new_prefix
        store["monitoring_points"][selected_edit_idx]["coil_num"] = new_num
        store["monitoring_points"][selected_edit_idx]["last_updated"] = now_str

        # Reset mute for this station on new reading update
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

        # Real-time Google Sheet API sync integration using gspread
        sheet_link = store.get("google_sheet_url", "")
        if "docs.google.com" in sheet_link:
            try:
                import gspread

                # To connect your Google Sheet automatically:
                # 1. Place your Google Cloud service account credentials file as 'credentials.json' in your app folder.
                # 2. Share your Google Sheet with the service account email.
                if os.path.exists("credentials.json"):
                    gc = gspread.service_account(filename="credentials.json")
                    sh = gc.open_by_url(sheet_link)
                    worksheet = sh.get_worksheet(0)
                    worksheet.append_row(
                        [now_str, current_pt["name"], new_val, new_log["Coil"]]
                    )
            except Exception as e:
                pass

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
        new_username = st.text_input("New Username (e.g. operator1)")
        new_name = st.text_input("Full Name (e.g. Ali Khan)")
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
            else:
                st.warning("Please fill in all fields.")

    st.markdown("---")
    st.write("### Registered Users List:")
    for username, details in store["user_db"].items():
        st.markdown(
            f"- **{username}**: {details['name']} (Role: **{details['role'].upper()}**)"
        )

with tabs[3]:
    st.subheader("📊 Log History & Google Sheets Access")

    col_btn1, col_btn2 = st.columns([2, 4])
    with col_btn1:
        sheet_link = store.get("google_sheet_url", "")
        if sheet_link and "your-sheet-id-here" not in sheet_link:
            st.markdown(
                f'<a href="{sheet_link}" target="_blank"><button style="background-color: #2ecc71; color: white; border: none; padding: 12px 24px; border-radius: 8px; font-weight: bold; cursor: pointer; font-size: 15px;">📂 Open Live Google Sheet</button></a>',
                unsafe_allow_html=True,
            )
        else:
            st.info(
                "Configure your Google Sheet URL in Sidebar -> Admin Settings."
            )

    if store["log_history"]:
        st.markdown("### Recent Log Entries")
        df_logs = pd.DataFrame(store["log_history"])
        st.dataframe(df_logs, use_container_width=True)

        csv_data = df_logs.to_csv(index=False).encode("utf-8")
        st.download_button(
            label="📥 Download Logs as CSV (for Google Sheets import)",
            data=csv_data,
            file_name="ccr_oxygen_logs.csv",
            mime="text/csv",
        )
    else:
        st.info("No logs recorded yet.")
