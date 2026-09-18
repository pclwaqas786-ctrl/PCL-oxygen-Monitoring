import datetime
import json
import os
import textwrap
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
    "app_subtitle": (
        "Real-time oxygen tracking system with individual item thresholds and"
        " 24/7 Google Sheets logging."
    ),
    "bg_image": "",
    "logo_image": "",
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
            "last_updated": "2026-09-18 20:00:00",
        },
        {
            "name": "Tundish",
            "coil_prefix": "",
            "coil_num": "",
            "val": 476.0,
            "min_limit": 100.0,
            "max_limit": 350.0,
            "last_updated": "2026-09-18 20:00:00",
        },
        {
            "name": "Shaft Furnace(SF)",
            "coil_prefix": "",
            "coil_num": "",
            "val": 200.0,
            "min_limit": 100.0,
            "max_limit": 350.0,
            "last_updated": "2026-09-18 20:00:00",
        },
        {
            "name": "Holding furnace(HF)",
            "coil_prefix": "",
            "coil_num": "",
            "val": 0.0,
            "min_limit": 100.0,
            "max_limit": 350.0,
            "last_updated": "2026-09-18 20:00:00",
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

bg_css = """
<style>
.stApp {
    background-color: #0F172A;
}
</style>
"""
if store.get("bg_image"):
  bg_css = f"""
<style>
.stApp {{
    background: linear-gradient(rgba(15, 23, 42, 0.85), rgba(15, 23, 42, 0.85)), url("{store['bg_image']}") no-repeat center center fixed;
    background-size: cover;
}}
</style>
"""

st.markdown(bg_css, unsafe_allow_html=True)
st.markdown(
    """
<style>
.main-card {
    background-color: rgba(38, 38, 38, 0.9);
    border: 1px solid rgba(255, 255, 255, 0.15);
    border-radius: 12px;
    padding: 20px;
    margin-bottom: 20px;
    color: white;
    box-shadow: 0 4px 15px rgba(0,0,0,0.3);
}
.main-card-large {
    background-color: rgba(38, 38, 38, 0.95);
    border: 2px solid #38bdf8;
    border-radius: 16px;
    padding: 35px;
    margin-bottom: 20px;
    color: white;
    box-shadow: 0 8px 25px rgba(56, 189, 248, 0.3);
}
.card-title {
    font-weight: 700;
    font-size: 18px;
    margin-bottom: 4px;
    color: #ffffff;
    text-align: center;
}
.card-title-large {
    font-weight: 800;
    font-size: 26px;
    margin-bottom: 8px;
    color: #ffffff;
    text-align: center;
}
.card-coil {
    font-weight: 600;
    font-size: 14px;
    margin-bottom: 10px;
    color: #38bdf8;
    text-align: center;
}
.card-coil-large {
    font-weight: 600;
    font-size: 18px;
    margin-bottom: 15px;
    color: #38bdf8;
    text-align: center;
}
.card-val-green {
    font-size: 40px;
    font-weight: 800;
    color: #2ecc71;
    text-align: center;
    margin: 10px 0;
}
.card-val-green-large {
    font-size: 75px;
    font-weight: 900;
    color: #2ecc71;
    text-align: center;
    margin: 15px 0;
}
.card-val-red {
    font-size: 40px;
    font-weight: 800;
    color: #e74c3c;
    text-align: center;
    margin: 10px 0;
}
.card-val-red-large {
    font-size: 75px;
    font-weight: 900;
    color: #e74c3c;
    text-align: center;
    margin: 15px 0;
}
.badge-safe {
    background-color: rgba(46, 204, 113, 0.2);
    color: #2ecc71;
    padding: 6px 12px;
    border-radius: 20px;
    font-weight: bold;
    font-size: 13px;
    display: inline-block;
}
.badge-safe-large {
    background-color: rgba(46, 204, 113, 0.2);
    color: #2ecc71;
    padding: 10px 20px;
    border-radius: 25px;
    font-weight: bold;
    font-size: 16px;
    display: inline-block;
}
.badge-critical {
    background-color: rgba(231, 76, 60, 0.2);
    color: #e74c3c;
    padding: 6px 12px;
    border-radius: 20px;
    font-weight: bold;
    font-size: 13px;
    display: inline-block;
}
.badge-critical-large {
    background-color: rgba(231, 76, 60, 0.2);
    color: #e74c3c;
    padding: 10px 20px;
    border-radius: 25px;
    font-weight: bold;
    font-size: 16px;
    display: inline-block;
}
.card-sub-desc {
    color: #94a3b8;
    font-size: 12px;
    margin-top: 6px;
    text-align: center;
}
.card-sub-desc-large {
    color: #cbd5e1;
    font-size: 16px;
    margin-top: 10px;
    text-align: center;
}
.card-timestamp {
    color: #94a3b8;
    font-size: 11px;
    text-align: center;
    margin-top: 12px;
    border-top: 1px solid rgba(255, 255, 255, 0.1);
    padding-top: 6px;
}
</style>
""",
    unsafe_allow_html=True,
)

st.sidebar.markdown("### 🔐 User Login & Controls")
if not st.session_state.logged_in:
  st.sidebar.warning("Please log in to continue.")
  login_user = st.sidebar.text_input("Username", key="login_u")
  login_pass = st.sidebar.text_input(
      "Password", type="password", key="login_p"
  )
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

with st.sidebar.expander("⚙️ Admin Settings & Branding", expanded=False):
  st.markdown("#### App Title Settings")
  new_title = st.text_input("Main Title", value=store["app_title"])
  new_subtitle = st.text_area("Subtitle", value=store["app_subtitle"])
  if st.button("Save Title Settings"):
    st.session_state.store["app_title"] = new_title
    st.session_state.store["app_subtitle"] = new_subtitle
    save_store()
    st.success("Title updated successfully!")
    st.rerun()

  st.markdown("---")
  st.markdown("#### 🖼️ Company Logo & Wallpaper")
  uploaded_logo = st.file_uploader(
      "Upload Logo Image", type=["png", "jpg", "jpeg", "svg"], key="logo_up"
  )
  if uploaded_logo:
    encoded_logo = base64.b64encode(uploaded_logo.read()).decode()
    file_type = uploaded_logo.type or "image/png"
    st.session_state.store["logo_image"] = (
        f"data:{file_type};base64,{encoded_logo}"
    )
    save_store()
    st.success("Logo uploaded successfully!")
    st.rerun()

  uploaded_bg = st.file_uploader(
      "Upload Background Wallpaper", type=["png", "jpg", "jpeg"], key="bg_up"
  )
  if uploaded_bg:
    encoded_bg = base64.b64encode(uploaded_bg.read()).decode()
    bg_type = uploaded_bg.type or "image/jpeg"
    st.session_state.store["bg_image"] = f"data:{bg_type};base64,{encoded_bg}"
    save_store()
    st.success("Background wallpaper updated successfully!")
    st.rerun()

head_col1, head_col2 = st.columns([1.2, 5.8])
with head_col1:
  if store.get("logo_image"):
    logo_code = textwrap.dedent(f"""
        <div style="background-color: #0b1329; padding: 10px; border-radius: 12px; display: inline-block; border: 2px solid #38bdf8; text-align: center;">
            <img src="{store['logo_image']}" width="120" style="border-radius: 6px; display: block; margin: 0 auto; object-fit: contain;">
        </div>
        """)
    st.markdown(logo_code, unsafe_allow_html=True)
  else:
    logo_code = textwrap.dedent("""
        <div style="background: linear-gradient(135deg, #0b1329 0%, #1e293b 100%); width: 130px; height: 130px; border-radius: 16px; border: 2px solid #38bdf8; display: flex; flex-direction: column; align-items: center; justify-content: center; box-shadow: 0 4px 12px rgba(0,0,0,0.4); text-align: center; padding: 8px;">
            <div style="width: 50px; height: 50px; border: 4px solid #38bdf8; border-radius: 50%; display: flex; align-items: center; justify-content: center; margin-bottom: 6px;">
                <span style="color: #2ecc71; font-size: 26px; font-weight: bold;">✓</span>
            </div>
            <span style="color: white; font-size: 11px; font-weight: 800; letter-spacing: 0.5px; line-height: 1.1;">PAKISTAN CABLES</span>
        </div>
        """)
    st.markdown(logo_code, unsafe_allow_html=True)

with head_col2:
  st.markdown(
      f"<h1 style='margin-bottom:0; font-weight:800; color:"
      f" white;'>{store['app_title']}</h1>",
      unsafe_allow_html=True,
  )
  st.markdown(
      "<p style='color: #cbd5e1; font-size: 16px;"
      f" margin-top:4px;'><em>{store['app_subtitle']}</em></p>",
      unsafe_allow_html=True,
  )

st.markdown("---")

st.markdown(
    "<h4 style='color: #38bdf8; margin-bottom: 5px;'>🔍 Select View"
    " Mode</h4>",
    unsafe_allow_html=True,
)
view_options = ["Show All Cards"] + [p["name"] for p in store["monitoring_points"]]
selected_view = st.selectbox(
    "Choose station view mode:",
    options=view_options,
    label_visibility="collapsed",
)

st.markdown("<br>", unsafe_allow_html=True)

any_high_alert = False
alert_details = []

if selected_view == "Show All Cards":
  if len(store["monitoring_points"]) > 0:
    cols = st.columns(min(len(store["monitoring_points"]), 4))
  else:
    cols = [st.empty()]

  for idx, pt in enumerate(store["monitoring_points"]):
    col = cols[idx % len(cols)]
    val = pt["val"]
    min_l = pt.get("min_limit", 100.0)
    max_l = pt.get("max_limit", 350.0)
    last_t = pt.get(
        "last_updated", datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    )

    coil_html = ""
    if pt["name"].upper() == "ROD":
      prefix = pt.get("coil_prefix", "CR")
      c_num = pt.get("coil_num", "2002")
      full_coil_display = f"{prefix}-{c_num}".strip()
      coil_html = (
          f'<div class="card-coil">📦 Item/Coil: {full_coil_display}</div>'
      )

    if val == 0.0:
      status_label = "NO DATA YET"
      val_class = "card-val-green"
      badge_class = "badge-safe"
      sub_desc = "Awaiting first reading input."
    elif val < min_l:
      status_label = "CRITICAL ALERT (Red)"
      val_class = "card-val-red"
      badge_class = "badge-critical"
      sub_desc = f"Below minimum safe limit ({min_l} ppm)!"
      any_high_alert = True
      alert_details.append(f"{pt['name']}: Low Level ({val} ppm)")
    elif val > max_l:
      status_label = "CRITICAL ALERT (Red)"
      val_class = "card-val-red"
      badge_class = "badge-critical"
      sub_desc = f"Above maximum safe limit ({max_l} ppm)!"
      any_high_alert = True
      alert_details.append(f"{pt['name']}: High Level ({val} ppm)")
    else:
      status_label = "SAFE ZONE (Green)"
      val_class = "card-val-green"
      badge_class = "badge-safe"
      sub_desc = "Normal safe range."

    card_code = textwrap.dedent(f"""
        <div class="main-card">
            <div class="card-title">{pt['name']}</div>
            {coil_html}
            <div class="{val_class}">{val:.2f} <span style="font-size:20px;">ppm</span></div>
            <div style="text-align: center; margin-top: 10px;">
                <span class="{badge_class}">● {status_label}</span>
                <div class="card-sub-desc">{sub_desc}</div>
            </div>
            <div class="card-timestamp">🕒 Recorded At: {last_t}</div>
        </div>
        """)
    with col:
      st.markdown(card_code, unsafe_allow_html=True)
else:
  focused_pt = next(
      (p for p in store["monitoring_points"] if p["name"] == selected_view), None
  )
  if focused_pt:
    val = focused_pt["val"]
    min_l = focused_pt.get("min_limit", 100.0)
    max_l = focused_pt.get("max_limit", 350.0)
    last_t = focused_pt.get(
        "last_updated", datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    )

    coil_html_large = ""
    if focused_pt["name"].upper() == "ROD":
      prefix = focused_pt.get("coil_prefix", "CR")
      c_num = focused_pt.get("coil_num", "2002")
      full_coil_display = f"{prefix}-{c_num}".strip()
      coil_html_large = (
          f'<div class="card-coil-large">📦 Item/Coil: {full_coil_display}</div>'
      )

    if val == 0.0:
      status_label = "NO DATA YET"
      val_class = "card-val-green-large"
      badge_class = "badge-safe-large"
      sub_desc = "Awaiting first reading input."
    elif val < min_l:
      status_label = "CRITICAL ALERT (Red)"
      val_class = "card-val-red-large"
      badge_class = "badge-critical-large"
      sub_desc = f"Below minimum safe limit ({min_l} ppm)!"
      any_high_alert = True
      alert_details.append(f"{focused_pt['name']}: Low Level ({val} ppm)")
    elif val > max_l:
      status_label = "CRITICAL ALERT (Red)"
      val_class = "card-val-red-large"
      badge_class = "badge-critical-large"
      sub_desc = f"Above maximum safe limit ({max_l} ppm)!"
      any_high_alert = True
      alert_details.append(f"{focused_pt['name']}: High Level ({val} ppm)")
    else:
      status_label = "SAFE ZONE (Green)"
      val_class = "card-val-green-large"
      badge_class = "badge-safe-large"
      sub_desc = "Normal safe range."

    focused_card_code = textwrap.dedent(f"""
        <div class="main-card-large">
            <div class="card-title-large">🔍 Focused View: {focused_pt['name']}</div>
            {coil_html_large}
            <div class="{val_class}">{val:.2f} <span style="font-size:30px;">ppm</span></div>
            <div style="text-align: center; margin-top: 20px;">
                <span class="{badge_class}">● {status_label}</span>
                <div class="card-sub-desc-large">{sub_desc}</div>
            </div>
            <div class="card-timestamp" style="font-size: 14px; margin-top: 20px;">🕒 Recorded At: {last_t}</div>
        </div>
        """)
    st.markdown(focused_card_code, unsafe_allow_html=True)

for pt in store["monitoring_points"]:
  val = pt["val"]
  min_l = pt.get("min_limit", 100.0)
  max_l = pt.get("max_limit", 350.0)
  if val > 0 and (val < min_l or val > max_l):
    any_high_alert = True

if any_high_alert:
  alert_msg = (
      " | ".join(alert_details) if alert_details else "Critical limit exceeded!"
  )
  alarm_html = f"""
    <div style="font-family: sans-serif; background-color: #8b0000; color: white; padding: 18px; border-radius: 12px; text-align: center; border: 3px solid #ff4b4b; box-shadow: 0 6px 16px rgba(0,0,0,0.4); margin-top: 10px; margin-bottom: 20px;">
        <h2 style="margin: 0 0 8px 0; color: #ffffff; font-size: 24px;">🚨 EXTREME CRITICAL HIGH ALERT!</h2>
        <p style="font-size: 15px; margin: 0 0 14px 0; color: #ffcccc;">{alert_msg}</p>
        <button id="alarmBtn" onclick="toggleSiren()" style="background-color: #ff4b4b; color: white; border: 2px solid #ffffff; padding: 14px 30px; font-size: 18px; border-radius: 8px; cursor: pointer; font-weight: bold; box-shadow: 0 4px 10px rgba(0,0,0,0.5);">
            🔔 START LOUD ALARM SOUND 🔊
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
                btn.innerText = "🔔 START LOUD ALARM SOUND 🔊";
                btn.style.backgroundColor = "#ff4b4b";
            }}
            return;
        }}

        isPlaying = true;
        if (btn) {{
            btn.innerText = "🚨 LOUD ALARM RINGING (CLICK TO MUTE) 🔊";
            btn.style.backgroundColor = "#cc0000";
        }}

        try {{
            var AudioCtxClass = window.AudioContext || window.webkitAudioContext;
            if (!audioCtx) {{ audioCtx = new AudioCtxClass(); }}
            if (audioCtx.state === 'suspended') {{ audioCtx.resume(); }}
            var flip = false;
            function playSirenTone() {{
                if (!isPlaying) return;
                try {{
                    var osc = audioCtx.createOscillator();
                    var gain = audioCtx.createGain();
                    osc.type = 'sawtooth';
                    var freq = flip ? 1200 : 700;
                    flip = !flip;
                    osc.frequency.setValueAtTime(freq, audioCtx.currentTime);
                    gain.gain.setValueAtTime(1.0, audioCtx.currentTime);
                    gain.gain.exponentialRampToValueAtTime(0.1, audioCtx.currentTime + 0.4);
                    osc.connect(gain);
                    gain.connect(audioCtx.destination);
                    osc.start();
                    osc.stop(audioCtx.currentTime + 0.4);
                }} catch(e) {{}}
            }}
            playSirenTone();
            sirenInterval = setInterval(playSirenTone, 400);
        }} catch(err) {{}}
    }}
    </script>
    """
  components.html(alarm_html, height=190)

st.markdown(
    "<h3 style='color: white;'>📝 Live Data Entry & Operations Panel</h3>",
    unsafe_allow_html=True,
)
tabs = st.tabs([
    "⚡ Update Readings",
    "⚙️ Admin: Manage Limits",
    "👥 User Management",
    "📊 Log History",
])

with tabs[0]:
  st.subheader("Update Live Sensor Reading")
  if len(store["monitoring_points"]) > 0:
    selected_edit_idx = st.selectbox(
        "Select Monitoring Point",
        options=range(len(store["monitoring_points"])),
        format_func=lambda x: store["monitoring_points"][x]["name"],
        key="update_item_idx",
    )
    current_pt = store["monitoring_points"][selected_edit_idx]

    up_col1, up_col2 = st.columns(2)
    with up_col1:
      if current_pt["name"].upper() == "ROD":
        new_coil_prefix = st.text_input(
            "Prefix (e.g. CR)",
            value=current_pt.get("coil_prefix", "CR"),
            key="up_prefix",
        )
        new_coil_num = st.text_input(
            "Item / Coil Number",
            value=current_pt.get("coil_num", "2002"),
            key="up_num",
        )
      else:
        new_coil_prefix = ""
        new_coil_num = ""
        st.info("Coil number is only applicable for ROD station.")

    with up_col2:
      new_val = st.number_input(
          f"Oxygen Value for {current_pt['name']} (PPM)",
          value=float(current_pt["val"]),
          step=0.01,
          format="%.2f",
          key=f"up_ppm_val_{selected_edit_idx}",
      )

    if st.button("Submit & Save Reading", type="primary"):
      now_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

      if current_pt["name"].upper() == "ROD":
        st.session_state.store["monitoring_points"][selected_edit_idx][
            "coil_prefix"
        ] = new_coil_prefix
        st.session_state.store["monitoring_points"][selected_edit_idx][
            "coil_num"
        ] = new_coil_num

      st.session_state.store["monitoring_points"][selected_edit_idx][
          "val"
      ] = new_val
      st.session_state.store["monitoring_points"][selected_edit_idx][
          "last_updated"
      ] = now_str

      min_l = current_pt.get("min_limit", 100.0)
      max_l = current_pt.get("max_limit", 350.0)

      if new_val == 0.0:
        st_str = "NO DATA YET"
      elif new_val < min_l or new_val > max_l:
        st_str = "CRITICAL ALERT (Red)"
      else:
        st_str = "SAFE ZONE (Green)"

      user_display_name = store["user_db"].get(st.session_state.username, {}).get(
          "name", st.session_state.username
      )
      full_item_str = (
          f"{new_coil_prefix}-{new_coil_num}".strip()
          if (new_coil_prefix or new_coil_num and current_pt["name"].upper() == "ROD")
          else current_pt["name"]
      )

      log_entry = {
          "Timestamp": now_str,
          "User": user_display_name,
          "Shift": st.session_state.duty_shift,
          "Item Name": full_item_str,
          "Value (ppm)": new_val,
          "Status": st_str,
      }

      st.session_state.store["log_history"].append(log_entry)
      save_store()
      st.success(
          f"Successfully updated {current_pt['name']} to {new_val:.2f} ppm!"
      )
      st.rerun()

with tabs[1]:
  st.subheader("⚙️ Admin Panel: Manage Limits")
  if len(store["monitoring_points"]) > 0:
    adm_idx = st.selectbox(
        "Select Point to Configure",
        options=range(len(store["monitoring_points"])),
        format_func=lambda x: store["monitoring_points"][x]["name"],
        key="adm_edit_sel",
    )
    p_item = store["monitoring_points"][adm_idx]
    new_min = st.number_input(
        "Minimum Safe Limit",
        value=float(p_item.get("min_limit", 100.0)),
        key="adm_min",
    )
    new_max = st.number_input(
        "Maximum Safe Limit",
        value=float(p_item.get("max_limit", 350.0)),
        key="adm_max",
    )
    if st.button("Save Limits"):
      st.session_state.store["monitoring_points"][adm_idx]["min_limit"] = new_min
      st.session_state.store["monitoring_points"][adm_idx]["max_limit"] = new_max
      save_store()
      st.success("Limits updated successfully!")
      st.rerun()

with tabs[2]:
  st.subheader("👥 User Management")
  users_df = pd.DataFrame([
      {
          "Username": u,
          "Name": store["user_db"][u]["name"],
          "Role": store["user_db"][u]["role"],
          "Email": store["user_db"][u]["email"],
      }
      for u in store["user_db"]
  ])
  st.dataframe(users_df, use_container_width=True)

with tabs[3]:
  st.subheader("📊 Log History")
  if store["log_history"]:
    st.dataframe(pd.DataFrame(store["log_history"]), use_container_width=True)
  else:
    st.info("No logs recorded yet.")
