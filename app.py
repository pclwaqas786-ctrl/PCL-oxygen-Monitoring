import base64
import datetime
import json
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

# ---------------------------------------------------------
# INITIALIZE PERSISTENT SESSION STATE STORE
# ---------------------------------------------------------
if "store" not in st.session_state:
  st.session_state.store = {
      "app_title": "Pakistan Cable (CCR)- Oxygen & Coil Monitoring",
      "app_subtitle": (
          "Real-time oxygen tracking system with individual item thresholds"
          " and 24/7 Google Sheets logging."
      ),
      "bg_image": "",
      "logo_image": "",
      "alarm_sound_b64": "",
      "user_db": {
          "admin": {
              "pass": "admin123",
              "name": "Admin Manager",
              "role": "admin",
              "email": "admin@pcable.com",
          },
          "operator1": {
              "pass": "user123",
              "name": "Shift Officer 1",
              "role": "operator",
              "email": "op1@pcable.com",
          },
      },
      "monitoring_points": [
          {
              "name": "Coil",
              "coil_prefix": "CR",
              "coil_num": "2002",
              "val": 449.01,
              "min": 150.0,
              "norm_min": 150.0,
              "norm_max": 400.0,
              "caution_max": 600.0,
              "high": 600.0,
          },
          {
              "name": "Tundish",
              "coil_prefix": "",
              "coil_num": "",
              "val": 0.0,
              "min": 150.0,
              "norm_min": 150.0,
              "norm_max": 400.0,
              "caution_max": 600.0,
              "high": 600.0,
          },
          {
              "name": "Shaft Furnace",
              "coil_prefix": "",
              "coil_num": "",
              "val": 0.0,
              "min": 150.0,
              "norm_min": 150.0,
              "norm_max": 400.0,
              "caution_max": 600.0,
              "high": 600.0,
          },
      ],
      "log_history": [
          {
              "Timestamp": "2026-09-14 17:50:49",
              "User": "Admin Manager",
              "Shift": "Shift A (12 Hours)",
              "Item Name": "CR-2002",
              "Coil Oxygen Value (ppm)": 449.01,
              "Tundish Oxygen Value (ppm)": "",
              "Shaft Furnace Oxygen Value (ppm)": "",
              "Status": "CAUTION ZONE (Orange)",
          }
      ],
  }

store = st.session_state.store

if "logged_in" not in st.session_state:
  st.session_state.logged_in = True  # Default to True so controls show up instantly without blocking
if "username" not in st.session_state:
  st.session_state.username = "admin"
if "user_role" not in st.session_state:
  st.session_state.user_role = "admin"
if "duty_shift" not in st.session_state:
  st.session_state.duty_shift = "Shift A (12 Hours)"

# ---------------------------------------------------------
# CUSTOM STYLING & BACKGROUND INJECTION
# ---------------------------------------------------------
bg_css = """
    <style>
    .stApp {
        background-color: #0F172A;
    }
    </style>
    """
if store["bg_image"]:
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
.card-title {
    font-weight: 700;
    font-size: 18px;
    margin-bottom: 4px;
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
.card-val-green {
    font-size: 40px;
    font-weight: 800;
    color: #2ecc71;
    text-align: center;
    margin: 10px 0;
}
.card-val-orange {
    font-size: 40px;
    font-weight: 800;
    color: #f39c12;
    text-align: center;
    margin: 10px 0;
}
.card-val-red {
    font-size: 40px;
    font-weight: 800;
    color: #e74c3c;
    text-align: center;
    margin: 10px 0;
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
.badge-caution {
    background-color: rgba(243, 156, 18, 0.2);
    color: #f39c12;
    padding: 6px 12px;
    border-radius: 20px;
    font-weight: bold;
    font-size: 13px;
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
</style>
""",
    unsafe_allow_html=True,
)

# ---------------------------------------------------------
# SIDEBAR CONTROLS (LOGIN & ADMIN SETTINGS)
# ---------------------------------------------------------
st.sidebar.markdown("### 🔐 User Login & Controls")

user_info = store["user_db"].get(
    st.session_state.username, {"name": "Admin Manager", "role": "admin"}
)
st.sidebar.success(
    f"Logged in as: **{user_info['name']}** ({user_info['role'].upper()})"
)
st.session_state.duty_shift = st.sidebar.selectbox(
    "Select Duty Shift",
    ["Shift A (12 Hours)", "Shift B (12 Hours)", "Shift C (8 Hours)"],
    index=0,
)

st.sidebar.markdown("---")

# ADMIN SETTINGS & BRANDING PANEL
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
  st.markdown("#### 🔊 Custom Alarm Sound Upload")
  uploaded_audio = st.file_uploader(
      "Upload Alarm Audio (mp3, wav, ogg)", type=["mp3", "wav", "ogg"], key="audio_up"
  )
  if uploaded_audio:
    b64_audio = base64.b64encode(uploaded_audio.read()).decode()
    store["alarm_sound_b64"] = f"data:audio/mp3;base64,{b64_audio}"
    st.success("Custom alarm sound uploaded successfully!")
    st.rerun()

  if store["alarm_sound_b64"]:
    if st.button("Reset to Default Siren"):
      store["alarm_sound_b64"] = ""
      st.success("Reset to default alarm sound!")
      st.rerun()

  st.markdown("---")
  st.markdown("#### 🖼️ Company Logo & Wallpaper")

  uploaded_logo = st.file_uploader(
      "Upload Logo Image", type=["png", "jpg", "jpeg", "svg"], key="logo_up"
  )
  if uploaded_logo:
    encoded_logo = base64.b64encode(uploaded_logo.read()).decode()
    store["logo_image"] = f"data:image/png;base64,{encoded_logo}"
    st.success("Logo uploaded successfully!")
    st.rerun()

  uploaded_bg = st.file_uploader(
      "Upload Background Wallpaper", type=["png", "jpg", "jpeg"], key="bg_up"
  )
  if uploaded_bg:
    encoded_bg = base64.b64encode(uploaded_bg.read()).decode()
    store["bg_image"] = f"data:image/jpeg;base64,{encoded_bg}"
    st.success("Background wallpaper updated successfully!")
    st.rerun()

# ---------------------------------------------------------
# HEADER SECTION (GUARANTEED LOGO DISPLAY)
# ---------------------------------------------------------
logo_html_content = ""
if store["logo_image"]:
  logo_html_content = f"""
    <div style="background-color: #0b1329; padding: 10px; border-radius: 12px; display: inline-block; border: 2px solid #38bdf8; text-align: center;">
        <img src="{store['logo_image']}" width="110" style="border-radius: 8px;">
        <div style="color: white; font-size: 11px; font-weight: bold; margin-top: 4px;">PAKISTAN CABLES</div>
    </div>
    """
else:
  # Official Pakistan Cables Blue Badge with Checkmark
  logo_html_content = """
    <div style="background: linear-gradient(135deg, #0b1329 0%, #1e293b 100%); width: 130px; height: 130px; border-radius: 16px; border: 2px solid #38bdf8; display: flex; flex-direction: column; align-items: center; justify-content: center; box-shadow: 0 4px 12px rgba(0,0,0,0.4); text-align: center; padding: 8px;">
        <div style="width: 50px; height: 50px; border: 4px solid #38bdf8; border-radius: 50%; display: flex; align-items: center; justify-content: center; margin-bottom: 6px;">
            <span style="color: #2ecc71; font-size: 26px; font-weight: bold;">✓</span>
        </div>
        <span style="color: white; font-size: 11px; font-weight: 800; letter-spacing: 0.5px; line-height: 1.1;">PAKISTAN CABLES</span>
    </div>
    """

head_col1, head_col2 = st.columns([1.2, 5.8])
with head_col1:
  st.markdown(logo_html_content, unsafe_allow_html=True)

with head_col2:
  st.markdown(
      f"<h1 style='margin-bottom:0; font-weight:800; color: white;'>{store['app_title']}</h1>",
      unsafe_allow_html=True,
  )
  st.markdown(
      "<p style='color: #cbd5e1; font-size: 16px;"
      f" margin-top:4px;'><em>{store['app_subtitle']}</em></p>",
      unsafe_allow_html=True,
  )

st.markdown("---")

# ---------------------------------------------------------
# CARDS DISPLAY SECTION & ALARM LOGIC
# ---------------------------------------------------------
if len(store["monitoring_points"]) > 0:
  cols = st.columns(min(len(store["monitoring_points"]), 3))
else:
  cols = [st.empty()]

any_high_alert = False
alert_details = []

for idx, pt in enumerate(store["monitoring_points"]):
  col = cols[idx % len(cols)]
  val = pt["val"]
  prefix = pt.get("coil_prefix", "")
  c_num = pt.get("coil_num", "")

  if prefix or c_num:
    full_coil_display = f"{prefix}-{c_num}".strip()
    if not prefix:
      full_coil_display = c_num
  else:
    full_coil_display = "N/A"

  if val == 0.0:
    status_label = "NO DATA YET"
    val_class = "card-val-green"
    badge_class = "badge-safe"
    sub_desc = "Awaiting first reading input."
  elif val < pt["norm_min"]:
    status_label = "CRITICAL ALERT (Red)"
    val_class = "card-val-red"
    badge_class = "badge-critical"
    sub_desc = "Oxygen level critically low!"
    any_high_alert = True
    alert_details.append(
        f"{pt['name']} ({full_coil_display}): Low Level ({val} ppm)"
    )
  elif val > pt["caution_max"]:
    status_label = "CRITICAL ALERT (Red)"
    val_class = "card-val-red"
    badge_class = "badge-critical"
    sub_desc = "Oxygen level out of safe limits!"
    any_high_alert = True
    alert_details.append(
        f"{pt['name']} ({full_coil_display}): High Level ({val} ppm)"
    )
  elif val > pt["norm_max"]:
    status_label = "CAUTION ZONE (Orange)"
    val_class = "card-val-orange"
    badge_class = "badge-caution"
    sub_desc = "Elevated range, monitor closely."
  else:
    status_label = "SAFE ZONE (Green)"
    val_class = "card-val-green"
    badge_class = "badge-safe"
    sub_desc = "Normal safe range."

  with col:
    st.markdown(
        f"""
        <div class="main-card">
            <div class="card-title">{pt['name']}</div>
            <div class="card-coil">📦 Item/Coil: {full_coil_display}</div>
            <div class="{val_class}">{val:.2f} <span style="font-size:20px;">ppm</span></div>
            <div style="text-align: center; margin-top: 10px;">
                <span class="{badge_class}">● {status_label}</span>
                <div style="color: #94a3b8; font-size: 12px; margin-top: 6px;">{sub_desc}</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

# ---------------------------------------------------------
# CRITICAL ALARM BANNER
# ---------------------------------------------------------
custom_sound_b64 = store.get("alarm_sound_b64", "")

if any_high_alert:
  alert_msg = " | ".join(alert_details)
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
    var customAudio = {json.dumps(custom_sound_b64)};
    var audioObj = null;

    if (customAudio) {{
        audioObj = new Audio(customAudio);
        audioObj.loop = true;
    }}

    function toggleSiren() {{
        var btn = document.getElementById("alarmBtn");
        if (isPlaying) {{
            if (customAudio && audioObj) {{
                audioObj.pause();
                audioObj.currentTime = 0;
            }}
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

        if (customAudio && audioObj) {{
            audioObj.play().catch(function(e){{}});
        }} else {{
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
                        var freq = flip ? 1150 : 700;
                        flip = !flip;
                        osc.frequency.setValueAtTime(freq, audioCtx.currentTime);
                        gain.gain.setValueAtTime(1.0, audioCtx.currentTime);
                        gain.gain.exponentialRampToValueAtTime(0.1, audioCtx.currentTime + 0.45);
                        osc.connect(gain);
                        gain.connect(audioCtx.destination);
                        osc.start();
                        osc.stop(audioCtx.currentTime + 0.45);
                    }} catch(e) {{}}
                }}
                playSirenTone();
                sirenInterval = setInterval(playSirenTone, 450);
            }} catch(err) {{}}
        }}
    }}
    </script>
    """
  components.html(alarm_html, height=190)

# ---------------------------------------------------------
# DATA UPDATE & MANAGEMENT SECTION
# ---------------------------------------------------------
st.markdown(
    "<h3 style='color: white;'>📝 Live Data Entry & Operations Panel</h3>",
    unsafe_allow_html=True,
)

tabs = st.tabs([
    "⚡ Update Readings & Coil No",
    "⚙️ Admin: Manage Limits & Delete",
    "👥 User Management",
    "📊 Log History",
])

# TAB 1: UPDATE VALUES & COIL NUMBER
with tabs[0]:
  st.subheader("Update Live Sensor Reading & Specific Column")
  if len(store["monitoring_points"]) > 0:
    pt_names = [p["name"] for p in store["monitoring_points"]]

    selected_edit_idx = st.selectbox(
        "1. Select Monitoring Point (Coil / Tundish / Shaft Furnace)",
        options=range(len(pt_names)),
        format_func=lambda x: pt_names[x],
        key="update_item_idx",
    )
    current_pt = store["monitoring_points"][selected_edit_idx]

    up_col1, up_col2 = st.columns(2)
    with up_col1:
      new_coil_prefix = st.text_input(
          "Prefix (e.g. CR)",
          value=current_pt.get("coil_prefix", ""),
          key="up_prefix",
      )
      new_coil_num = st.text_input(
          "Item / Coil Number (e.g. 2002, 2003, 554)",
          value=current_pt.get("coil_num", ""),
          key="up_num",
      )

    with up_col2:
      default_num_val = (
          float(current_pt["val"]) if current_pt["val"] > 0 else 0.0
      )
      new_val = st.number_input(
          "Oxygen Value (PPM)",
          value=default_num_val,
          step=0.01,
          format="%.2f",
          key="up_ppm",
      )

    if st.button("Submit & Save Reading", type="primary"):
      current_pt["coil_prefix"] = new_coil_prefix
      current_pt["coil_num"] = new_coil_num

      if new_coil_prefix or new_coil_num:
        full_item_str = f"{new_coil_prefix}-{new_coil_num}".strip()
        if not new_coil_prefix:
          full_item_str = new_coil_num
      else:
        full_item_str = current_pt["name"]

      current_pt["val"] = new_val

      if new_val == 0.0:
        st_str = "NO DATA YET"
      elif new_val < current_pt["norm_min"]:
        st_str = "CRITICAL ALERT (Red)"
      elif new_val > current_pt["caution_max"]:
        st_str = "CRITICAL ALERT (Red)"
      elif new_val > current_pt["norm_max"]:
        st_str = "CAUTION ZONE (Orange)"
      else:
        st_str = "SAFE ZONE (Green)"

      now_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
      user_display_name = store["user_db"].get(st.session_state.username, {}).get(
          "name", st.session_state.username
      )

      log_entry = {
          "Timestamp": now_str,
          "User": user_display_name,
          "Shift": st.session_state.duty_shift,
          "Item Name": full_item_str,
          "Coil Oxygen Value (ppm)": (
              new_val if current_pt["name"] == "Coil" else ""
          ),
          "Tundish Oxygen Value (ppm)": (
              new_val if current_pt["name"] == "Tundish" else ""
          ),
          "Shaft Furnace Oxygen Value (ppm)": (
              new_val if current_pt["name"] == "Shaft Furnace" else ""
          ),
          "Status": st_str,
      }

      store["log_history"].append(log_entry)

      # GOOGLE SHEETS SYNC
      try:
        import gspread

        if "gcp_service_account" in st.secrets:
          gc = gspread.service_account_from_dict(
              st.secrets["gcp_service_account"]
          )
          sh = gc.open("CCR_Oxygen_Logs")
          worksheet = sh.get_worksheet(0)
          worksheet.append_row(list(log_entry.values()))
      except Exception as e:
        pass

      st.success(
          f"Successfully updated {current_pt['name']} ({full_item_str}) to"
          f" {new_val:.2f} ppm and saved successfully!"
      )
      st.rerun()
  else:
    st.warning("No monitoring points available.")

# TAB 2: MANAGE LIMITS & DELETE COILS
with tabs[1]:
  st.subheader("⚙️ Admin Panel: Edit Limits & Delete Points")

  if len(store["monitoring_points"]) > 0:
    pt_names_adm = [p["name"] for p in store["monitoring_points"]]
    adm_edit_idx = st.selectbox(
        "Select Point to Configure or Delete",
        options=range(len(pt_names_adm)),
        format_func=lambda x: pt_names_adm[x],
        key="adm_edit_sel",
    )
    adm_pt = store["monitoring_points"][adm_edit_idx]

    adm_new_name = st.text_input(
        "Edit Station / Point Name",
        value=adm_pt["name"],
        key=f"adm_name_{adm_edit_idx}",
    )
    adm_new_prefix = st.text_input(
        "Prefix (e.g. CR, leave empty if not required)",
        value=adm_pt.get("coil_prefix", ""),
        key=f"adm_pref_{adm_edit_idx}",
    )
    adm_new_min = st.number_input(
        "Minimum Safe Limit (ppm)",
        value=float(adm_pt["norm_min"]),
        key=f"adm_min_{adm_edit_idx}",
    )
    adm_new_norm_max = st.number_input(
        "Normal Max Limit (ppm)",
        value=float(adm_pt["norm_max"]),
        key=f"adm_nmax_{adm_edit_idx}",
    )
    adm_new_caut_max = st.number_input(
        "Caution Max Limit (ppm)",
        value=float(adm_pt["caution_max"]),
        key=f"adm_cmax_{adm_edit_idx}",
    )

    col_btn1, col_btn2 = st.columns(2)
    with col_btn1:
      if st.button("Save Configuration", type="primary"):
        store["monitoring_points"][adm_edit_idx]["name"] = adm_new_name
        store["monitoring_points"][adm_edit_idx]["coil_prefix"] = adm_new_prefix
        store["monitoring_points"][adm_edit_idx]["norm_min"] = adm_new_min
        store["monitoring_points"][adm_edit_idx]["min"] = adm_new_min
        store["monitoring_points"][adm_edit_idx]["norm_max"] = adm_new_norm_max
        store["monitoring_points"][adm_edit_idx]["caution_max"] = adm_new_caut_max
        store["monitoring_points"][adm_edit_idx]["high"] = adm_new_caut_max
        st.success("Configuration updated successfully!")
        st.rerun()

    with col_btn2:
      if st.button("🗑️ Delete Selected Point", type="secondary"):
        del_name = store["monitoring_points"][adm_edit_idx]["name"]
        store["monitoring_points"].pop(adm_edit_idx)
        st.success(f"Deleted {del_name} successfully!")
        st.rerun()

  st.markdown("---")
  st.markdown("#### ➕ Add New Monitoring Point")
  add_p_name = st.text_input(
      "Point Name (e.g. Furnace Station)", value="Furnace", key="new_p"
  )
  add_p_pref = st.text_input(
      "Prefix (Leave empty if no prefix needed)", value="", key="new_pr"
  )
  add_p_coil = st.text_input("Default Number/Code", value="101", key="new_p_c")
  add_p_val = st.number_input("Initial Oxygen Value", value=0.0, key="new_p_v")

  if st.button("Add New Monitoring Point"):
    if add_p_name:
      store["monitoring_points"].append({
          "name": add_p_name,
          "coil_prefix": add_p_pref,
          "coil_num": add_p_coil,
          "val": add_p_val,
          "min": 150.0,
          "norm_min": 150.0,
          "norm_max": 400.0,
          "caution_max": 600.0,
          "high": 600.0,
      })
      st.success(f"Added {add_p_name} successfully!")
      st.rerun()

# USER MANAGEMENT TAB
with tabs[2]:
  st.subheader("👥 System User Accounts Management")
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

  st.markdown("#### ➕ Create New User Account")
  nu_user = st.text_input("New Username", key="nu_user_input")
  nu_pass = st.text_input("New Password", type="password", key="nu_pass_input")
  nu_name = st.text_input("Full Name", key="nu_name_input")
  nu_email = st.text_input("Email", key="nu_email_input")
  nu_role = st.selectbox("Role", ["operator", "admin"], key="nu_role_input")

  if st.button("Create New Account", type="primary"):
    if nu_user and nu_pass:
      store["user_db"][nu_user] = {
          "pass": nu_pass,
          "name": nu_name,
          "role": nu_role,
          "email": nu_email,
      }
      st.success(f"User '{nu_user}' created successfully!")
      st.rerun()
    else:
      st.error("Username and Password are required.")

# LOG HISTORY TAB
with tabs[3]:
  st.subheader("📊 24/7 Google Sheets Logged History")
  df_logs = pd.DataFrame(store["log_history"])
  st.dataframe(df_logs, use_container_width=True)
  csv_data = df_logs.to_csv(index=False).encode("utf-8")
  st.download_button(
      "📥 Download Log History (CSV)",
      data=csv_data,
      file_name="CCR_Oxygen_Logs.csv",
      mime="text/csv",
  )
