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
# INITIALIZE SESSION STATE STORE
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
              "coil_num": "2003",
              "val": 249.0,
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
              "val": 250.0,
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
              "val": 250.0,
              "min": 150.0,
              "norm_min": 150.0,
              "norm_max": 400.0,
              "caution_max": 600.0,
              "high": 600.0,
          },
      ],
      "log_history": [
          {
              "Timestamp": "2026-09-14 10:00:00",
              "Duty Shift": "Shift A (12 Hours)",
              "Item": "Coil",
              "Coil No": "CR2003",
              "Oxygen Level (ppm)": 249.0,
              "Status": "SAFE ZONE",
              "Updated By": "System",
          }
      ],
  }

store = st.session_state.store

if "logged_in" not in st.session_state:
  st.session_state.logged_in = False
if "username" not in st.session_state:
  st.session_state.username = ""
if "user_role" not in st.session_state:
  st.session_state.user_role = ""
if "duty_shift" not in st.session_state:
  st.session_state.duty_shift = "Shift A (12 Hours)"

# ---------------------------------------------------------
# CUSTOM STYLING & BACKGROUND INJECTION
# ---------------------------------------------------------
bg_css = ""
if store["bg_image"]:
  bg_css = f"""
    <style>
    .stApp {{
        background: linear-gradient(rgba(15, 23, 42, 0.85), rgba(15, 23, 42, 0.85)), url("{store['bg_image']}") no-repeat center center fixed;
        background-size: cover;
    }}
    </style>
    """
else:
  bg_css = """
    <style>
    .stApp {
        background-color: #0F172A;
    }
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
# SIDEBAR CONTROLS (LOGIN & NAVIGATION)
# ---------------------------------------------------------
st.sidebar.markdown("### 🔐 User Login & Controls")

if not st.session_state.logged_in:
  st.sidebar.warning("🔒 Read-Only Mode. Please log in to enable updates.")
  input_user = st.sidebar.text_input("Username", key="login_user")
  input_pass = st.sidebar.text_input("Password", type="password", key="login_pass")
  st.session_state.duty_shift = st.sidebar.selectbox(
      "Select Duty Shift",
      ["Shift A (12 Hours)", "Shift B (12 Hours)", "Shift C (8 Hours)"],
      key="shift_sel",
  )

  if st.sidebar.button("Login to Dashboard", type="primary"):
    if (
        input_user in store["user_db"]
        and store["user_db"][input_user]["pass"] == input_pass
    ):
      st.session_state.logged_in = True
      st.session_state.username = input_user
      st.session_state.user_role = store["user_db"][input_user]["role"]
      st.sidebar.success(f"Welcome {store['user_db'][input_user]['name']}!")
      st.rerun()
    else:
      st.sidebar.error("Invalid Username or Password!")
else:
  user_info = store["user_db"].get(
      st.session_state.username,
      {"name": st.session_state.username, "role": "operator"},
  )
  st.sidebar.success(
      f"Logged in as: **{user_info['name']}** ({user_info['role'].upper()})"
  )
  st.sidebar.info(f"Active Shift: **{st.session_state.duty_shift}**")

  if st.sidebar.button("Logout", type="secondary"):
    st.session_state.logged_in = False
    st.session_state.username = ""
    st.session_state.user_role = ""
    st.rerun()

  st.sidebar.markdown("---")

  # ADMIN ONLY SETTINGS PANEL IN SIDEBAR (Expanded by default for convenience)
  if st.session_state.user_role == "admin":
    with st.sidebar.expander(
        "⚙️ Admin Settings & Branding", expanded=True
    ):
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
# HEADER SECTION (LOGO + TITLE)
# ---------------------------------------------------------
head_col1, head_col2 = st.columns([1, 5])
with head_col1:
  if store["logo_image"]:
    st.image(store["logo_image"], width=130)
  else:
    st.markdown(
        "<h1 style='font-size: 70px; margin:0;'>🏭</h1>", unsafe_allow_html=True
    )

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
    full_coil_display = f"{prefix}{c_num}".strip()
  else:
    full_coil_display = "N/A"

  if val < pt["norm_min"]:
    status_label = "CRITICAL ALERT (Red)"
    val_class = "card-val-red"
    badge_class = "badge-critical"
    sub_desc = "Oxygen level critically low!"
    any_high_alert = True
    alert_details.append(
        f"{pt['name']} (Coil: {full_coil_display}): Low Level ({val} ppm)"
    )
  elif val > pt["caution_max"]:
    status_label = "CRITICAL ALERT (Red)"
    val_class = "card-val-red"
    badge_class = "badge-critical"
    sub_desc = "Oxygen level out of safe limits!"
    any_high_alert = True
    alert_details.append(
        f"{pt['name']} (Coil: {full_coil_display}): High Level ({val} ppm)"
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
            <div class="card-coil">📦 Coil No: {full_coil_display}</div>
            <div class="{val_class}">{val:.1f} <span style="font-size:20px;">ppm</span></div>
            <div style="text-align: center; margin-top: 10px;">
                <span class="{badge_class}">● {status_label}</span>
                <div style="color: #94a3b8; font-size: 12px; margin-top: 6px;">{sub_desc}</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

# ---------------------------------------------------------
# CRITICAL ALARM BANNER (CUSTOM SOUND OR DEFAULT LOUD SIREN)
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
# DATA UPDATE & MANAGEMENT SECTION (LOGGED IN USERS ONLY)
# ---------------------------------------------------------
if st.session_state.logged_in:
  st.markdown(
      "<h3 style='color: white;'>📝 Live Data Entry & Operations Panel</h3>",
      unsafe_allow_html=True,
  )

  if st.session_state.user_role == "admin":
    tabs = st.tabs([
        "⚡ Update Readings & Coil No",
        "⚙️ Admin: Manage Limits & Delete",
        "👥 User Management",
        "📊 Log History",
    ])
  else:
    tabs = st.tabs(
        ["⚡ Update Readings & Coil No", "📊 Log History (Read Only)"]
    )

  # TAB 1: UPDATE VALUES & COIL NUMBER
  with tabs[0]:
    st.subheader("Update Live Sensor Reading & Coil Number")
    if len(store["monitoring_points"]) > 0:
      up_col1, up_col2, up_col3 = st.columns(3)
      pt_names = [p["name"] for p in store["monitoring_points"]]

      with up_col1:
        selected_edit_idx = st.selectbox(
            "1. Select Coil / Point",
            options=range(len(pt_names)),
            format_func=lambda x: pt_names[x],
            key="update_item_idx",
        )
        current_pt = store["monitoring_points"][selected_edit_idx]

      with up_col2:
        st.markdown(
            "<label style='font-size:14px; font-weight:600; color:#ffffff;'>2."
            " Enter Prefix & Number</label>",
            unsafe_allow_html=True,
        )
        col_p1, col_p2 = st.columns([1, 2])
        curr_prefix = current_pt.get("coil_prefix", "")
        with col_p1:
          new_coil_prefix = st.text_input(
              "Prefix",
              value=curr_prefix,
              label_visibility="collapsed",
              key="update_coil_prefix_input",
          )
        with col_p2:
          new_coil_num = st.text_input(
              "Number",
              value=current_pt.get("coil_num", ""),
              label_visibility="collapsed",
              key="update_coil_num_input",
          )

      with up_col3:
        new_val = st.number_input(
            "3. Enter PPM",
            value=float(current_pt["val"]),
            step=1.0,
            format="%.2f",
            key="update_oxygen_val",
        )

      if st.button("Submit & Save Reading", type="primary"):
        current_pt["coil_prefix"] = new_coil_prefix
        current_pt["coil_num"] = new_coil_num
        
        if new_coil_prefix or new_coil_num:
          full_coil_str = f"{new_coil_prefix}{new_coil_num}".strip()
        else:
          full_coil_str = "N/A"
          
        current_pt["val"] = new_val

        if new_val < current_pt["norm_min"]:
          st_str = "CRITICAL LOW ALERT"
        elif new_val > current_pt["caution_max"]:
          st_str = "CRITICAL HIGH ALERT"
        elif new_val > current_pt["norm_max"]:
          st_str = "CAUTION ZONE"
        else:
          st_str = "SAFE ZONE"

        now_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        store["log_history"].append({
            "Timestamp": now_str,
            "Duty Shift": st.session_state.duty_shift,
            "Item": current_pt["name"],
            "Coil No": full_coil_str,
            "Oxygen Level (ppm)": new_val,
            "Status": st_str,
            "Updated By": st.session_state.username,
        })
        st.success(
            f"Successfully updated {current_pt['name']} (Coil No:"
            f" {full_coil_str}) to {new_val} ppm!"
        )
        st.rerun()
    else:
      st.warning(
          "No monitoring points available. Please add one from Admin panel."
      )

  # TAB 2 (ADMIN ONLY): MANAGE LIMITS & DELETE COILS
  if st.session_state.user_role == "admin":
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
            store["monitoring_points"][adm_edit_idx]["coil_prefix"] = (
                adm_new_prefix
            )
            store["monitoring_points"][adm_edit_idx]["norm_min"] = adm_new_min
            store["monitoring_points"][adm_edit_idx]["min"] = adm_new_min
            store["monitoring_points"][adm_edit_idx]["norm_max"] = (
                adm_new_norm_max
            )
            store["monitoring_points"][adm_edit_idx]["caution_max"] = (
                adm_new_caut_max
            )
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
          "Point Name (e.g. Furnace Station)",
          value="Furnace",
          key="new_p",
      )
      add_p_pref = st.text_input(
          "Prefix (Leave empty if no prefix needed)", value="", key="new_pr"
      )
      add_p_coil = st.text_input(
          "Default Number/Code", value="101", key="new_p_c"
      )
      add_p_val = st.number_input(
          "Initial Oxygen Value", value=250.0, key="new_p_v"
      )

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

  # USER MANAGEMENT TAB (ADMIN ONLY)
  if st.session_state.user_role == "admin":
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
      nu_pass = st.text_input(
          "New Password", type="password", key="nu_pass_input"
      )
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
  log_tab_index = 3 if st.session_state.user_role == "admin" else 1
  with tabs[log_tab_index]:
    st.subheader("📊 24/7 Google Sheets Logged History")
    df_logs = pd.DataFrame(store["log_history"])
    st.dataframe(df_logs, use_container_width=True)
    csv_data = df_logs.to_csv(index=False).encode("utf-8")
    st.download_button(
        "📥 Download Log History (CSV)",
        data=csv_data,
        file_name="pcl_oxygen_log.csv",
        mime="text/csv",
    )
