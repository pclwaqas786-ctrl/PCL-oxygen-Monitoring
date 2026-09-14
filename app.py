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
# INITIALIZE SESSION STATE STORE (PERMANENT PERSISTENCE)
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
          "operator2": {
              "pass": "user223",
              "name": "Shift Operator 2",
              "role": "operator",
              "email": "op2@pcable.com",
          },
      },
      "monitoring_points": [
          {
              "name": "CR-2002 (Top/Tail)",
              "val": 249.01,
              "min": 200.0,
              "norm_min": 200.0,
              "norm_max": 400.0,
              "caution_max": 600.0,
              "high": 600.0,
          },
          {
              "name": "CR-1605 (Top End)",
              "val": 107.00,
              "min": 150.0,
              "norm_min": 150.0,
              "norm_max": 350.0,
              "caution_max": 500.0,
              "high": 500.0,
          },
          {
              "name": "CR-2486 (Top End)",
              "val": 577.00,
              "min": 200.0,
              "norm_min": 200.0,
              "norm_max": 400.0,
              "caution_max": 600.0,
              "high": 600.0,
          },
          {
              "name": "Shaft Furnace (SF-6)",
              "val": 292.00,
              "min": 180.0,
              "norm_min": 180.0,
              "norm_max": 380.0,
              "caution_max": 550.0,
              "high": 550.0,
          },
          {
              "name": "Tundish-Sample",
              "val": 512.00,
              "min": 200.0,
              "norm_min": 200.0,
              "norm_max": 450.0,
              "caution_max": 650.0,
              "high": 650.0,
          },
      ],
      "log_history": [
          {
              "Timestamp": "2026-09-14 10:00:00",
              "Duty Shift": "Shift A (12 Hours)",
              "Item": "CR-2002 (Top/Tail)",
              "Oxygen Level (ppm)": 249.01,
              "Status": "SAFE ZONE",
              "Updated By": "System",
          },
          {
              "Timestamp": "2026-09-14 10:15:00",
              "Duty Shift": "Shift A (12 Hours)",
              "Item": "CR-1605 (Top End)",
              "Oxygen Level (ppm)": 107.00,
              "Status": "CRITICAL LOW ALERT",
              "Updated By": "operator1",
          },
          {
              "Timestamp": "2026-09-14 10:30:00",
              "Duty Shift": "Shift A (12 Hours)",
              "Item": "CR-2486 (Top End)",
              "Oxygen Level (ppm)": 577.00,
              "Status": "CAUTION ZONE",
              "Updated By": "admin",
          },
      ],
  }

store = st.session_state.store

# Initialize session state for user authentication
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
    margin-bottom: 12px;
    color: #ffffff;
    text-align: center;
}
.card-val-green {
    font-size: 42px;
    font-weight: 800;
    color: #2ecc71;
    text-align: center;
    margin: 10px 0;
}
.card-val-orange {
    font-size: 42px;
    font-weight: 800;
    color: #f39c12;
    text-align: center;
    margin: 10px 0;
}
.card-val-red {
    font-size: 42px;
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
  st.sidebar.warning("🔒 Read-Only Mode. Please log in to enable data updates.")
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

  with st.sidebar.expander("🔑 Forgot Password?"):
    st.write(
        "Contact Admin Manager at `admin@pcable.com` to reset your credentials."
    )
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

  # ADMIN ONLY SETTINGS PANEL IN SIDEBAR
  if st.session_state.user_role == "admin":
    with st.sidebar.expander("⚙️ Admin Settings & Branding"):
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
      uploaded_logo = st.file_uploader(
          "Upload Logo Image", type=["png", "jpg", "jpeg", "svg"], key="logo_up"
      )
      if uploaded_logo:
        encoded_logo = base64.b64encode(uploaded_logo.read()).decode()
        store["logo_image"] = f"data:image/png;base64,{encoded_logo}"
        st.success("Logo updated globally!")
        st.rerun()

      uploaded_bg = st.file_uploader(
          "Upload Background Wallpaper", type=["png", "jpg", "jpeg"], key="bg_up"
      )
      if uploaded_bg:
        encoded_bg = base64.b64encode(uploaded_bg.read()).decode()
        store["bg_image"] = f"data:image/jpeg;base64,{encoded_bg}"
        st.success("Background wallpaper updated globally!")
        st.rerun()

      if store["logo_image"] or store["bg_image"]:
        if st.button("Reset Branding to Default"):
          store["logo_image"] = ""
          store["bg_image"] = ""
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

if not st.session_state.logged_in:
  st.info(
      "💡 **Note:** Display values are currently in live monitoring mode."
      " Please log in via the sidebar to update values."
  )

# ---------------------------------------------------------
# CARDS DISPLAY SECTION & ALARM LOGIC
# ---------------------------------------------------------
cols = st.columns(3)
any_high_alert = False
alert_details = []

for idx, pt in enumerate(store["monitoring_points"]):
  col = cols[idx % 3]
  val = pt["val"]

  if val < pt["norm_min"]:
    status_label = "CRITICAL ALERT (Red)"
    val_class = "card-val-red"
    badge_class = "badge-critical"
    sub_desc = "Oxygen level critically low!"
    any_high_alert = True
    alert_details.append(f"{pt['name']}: Low Level ({val} ppm)")
  elif val > pt["caution_max"]:
    status_label = "CRITICAL ALERT (Red)"
    val_class = "card-val-red"
    badge_class = "badge-critical"
    sub_desc = "Oxygen level out of safe limits!"
    any_high_alert = True
    alert_details.append(f"{pt['name']}: High Level ({val} ppm)")
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
# CRITICAL ALARM BANNER (ONLY SHOW WHEN LOGGED IN & ALERT ACTIVE)
# ---------------------------------------------------------
if st.session_state.logged_in and any_high_alert:
  alert_msg = " | ".join(alert_details)
  alarm_html = f"""
    <div style="font-family: sans-serif; background-color: #8b0000; color: white; padding: 18px; border-radius: 12px; text-align: center; border: 3px solid #ff4b4b; box-shadow: 0 6px 16px rgba(0,0,0,0.4); margin-top: 10px; margin-bottom: 20px;">
        <h2 style="margin: 0 0 8px 0; color: #ffffff; font-size: 24px;">🚨 CRITICAL HIGH ALERT!</h2>
        <p style="font-size: 15px; margin: 0 0 14px 0; color: #ffcccc;">{alert_msg}</p>
        <button id="alarmBtn" onclick="toggleSiren()" style="background-color: #ff4b4b; color: white; border: 2px solid #ffffff; padding: 12px 26px; font-size: 16px; border-radius: 8px; cursor: pointer; font-weight: bold; box-shadow: 0 4px 10px rgba(0,0,0,0.5);">
            🔔 CLICK HERE TO START ALARM SOUND 🔊
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
                btn.innerText = "🔔 CLICK HERE TO START ALARM SOUND 🔊";
                btn.style.backgroundColor = "#ff4b4b";
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
                btn.innerText = "🚨 ALARM RINGING (CLICK TO MUTE) 🔊";
                btn.style.backgroundColor = "#cc0000";
            }}

            var flip = false;
            function playSirenTone() {{
                if (!isPlaying) return;
                try {{
                    var osc = audioCtx.createOscillator();
                    var gain = audioCtx.createGain();
                    osc.type = 'sawtooth';
                    
                    var freq = flip ? 980 : 620;
                    flip = !flip;
                    
                    osc.frequency.setValueAtTime(freq, audioCtx.currentTime);
                    gain.gain.setValueAtTime(0.8, audioCtx.currentTime);
                    gain.gain.exponentialRampToValueAtTime(0.05, audioCtx.currentTime + 0.45);
                    
                    osc.connect(gain);
                    gain.connect(audioCtx.destination);
                    
                    osc.start();
                    osc.stop(audioCtx.currentTime + 0.45);
                }} catch(e) {{
                    console.error("Audio error:", e);
                }}
            }}

            playSirenTone();
            sirenInterval = setInterval(playSirenTone, 500);

        }} catch(err) {{
            alert("Audio playback error: " + err.message);
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

  tabs = st.tabs([
      "⚡ Update Values",
      "➕ Manage Monitoring Points",
      "👥 User Management (Admin)",
      "📊 Google Sheets Log History",
  ])

  # TAB 1: UPDATE VALUES
  with tabs[0]:
    st.subheader("Update Live Sensor Readings")
    up_col1, up_col2 = st.columns(2)
    with up_col1:
      selected_point_name = st.selectbox(
          "Select Item to Update",
          [p["name"] for p in store["monitoring_points"]],
          key="update_sel_item",
      )
      selected_point = next(
          p
          for p in store["monitoring_points"]
          if p["name"] == selected_point_name
      )
      new_val = st.number_input(
          "New Oxygen Level (ppm)",
          value=float(selected_point["val"]),
          step=1.0,
          format="%.2f",
          key="update_new_val",
      )

    with up_col2:
      st.info(
          f"**Item Limits:** Normal: {selected_point['norm_min']} -"
          f" {selected_point['norm_max']} ppm | Caution Max:"
          f" {selected_point['caution_max']} ppm"
      )
      if st.button("Submit & Save Reading", type="primary"):
        selected_point["val"] = new_val

        # Determine status
        if new_val < selected_point["norm_min"]:
          st_str = "CRITICAL LOW ALERT"
        elif new_val > selected_point["caution_max"]:
          st_str = "CRITICAL HIGH ALERT"
        elif new_val > selected_point["norm_max"]:
          st_str = "CAUTION ZONE"
        else:
          st_str = "SAFE ZONE"

        # Add to log history
        now_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        store["log_history"].append({
            "Timestamp": now_str,
            "Duty Shift": st.session_state.duty_shift,
            "Item": selected_point_name,
            "Oxygen Level (ppm)": new_val,
            "Status": st_str,
            "Updated By": st.session_state.username,
        })
        st.success(
            f"Successfully updated {selected_point_name} to {new_val} ppm!"
        )
        st.rerun()

  # TAB 2: MANAGE POINTS (ADD, EDIT CR/NAME, DELETE)
  with tabs[1]:
    st.subheader("Add, Edit or Remove Monitoring Points")

    st.markdown("#### ✏️ Edit Existing Point / CR Name & Limits")
    edit_pt_name = st.selectbox(
        "Select Point/CR to Edit",
        [p["name"] for p in store["monitoring_points"]],
        key="edit_pt_select",
    )
    edit_pt = next(
        p for p in store["monitoring_points"] if p["name"] == edit_pt_name
    )

    # Use regular inputs instead of st.form to fix saving issues instantly
    new_edit_name = st.text_input(
        "Edit Point / CR Name", value=edit_pt["name"], key="edit_name_input"
    )
    new_edit_min = st.number_input(
        "Minimum Safe (ppm)",
        value=float(edit_pt["norm_min"]),
        key="edit_min_input",
    )
    new_edit_norm_max = st.number_input(
        "Normal Max (ppm)",
        value=float(edit_pt["norm_max"]),
        key="edit_norm_max_input",
    )
    new_edit_caut_max = st.number_input(
        "Caution Max (ppm)",
        value=float(edit_pt["caution_max"]),
        key="edit_caut_max_input",
    )

    if st.button("Update Point Settings", type="primary"):
      edit_pt["name"] = new_edit_name
      edit_pt["norm_min"] = new_edit_min
      edit_pt["min"] = new_edit_min
      edit_pt["norm_max"] = new_edit_norm_max
      edit_pt["caution_max"] = new_edit_caut_max
      edit_pt["high"] = new_edit_caut_max
      st.success(f"Successfully updated {new_edit_name}!")
      st.rerun()

    st.markdown("---")

    if st.session_state.user_role == "admin":
      st.markdown("#### ➕ Add New Point")
      p_name = st.text_input(
          "Point Name (e.g. CR-3000 Top End)", key="add_p_name"
      )
      p_val = st.number_input("Initial Value (ppm)", value=250.0, key="add_p_val")
      p_min = st.number_input(
          "Minimum Safe (ppm)", value=150.0, key="add_p_min"
      )
      p_norm_max = st.number_input(
          "Normal Max (ppm)", value=400.0, key="add_p_norm_max"
      )
      p_caut_max = st.number_input(
          "Caution Max (ppm)", value=600.0, key="add_p_caut_max"
      )

      if st.button("Add Monitoring Point"):
        if p_name:
          store["monitoring_points"].append({
              "name": p_name,
              "val": p_val,
              "min": p_min,
              "norm_min": p_min,
              "norm_max": p_norm_max,
              "caution_max": p_caut_max,
              "high": p_caut_max,
          })
          st.success(f"Added {p_name} successfully!")
          st.rerun()
        else:
          st.error("Please provide a valid point name.")

      st.markdown("---")
      st.markdown("#### 🗑️ Remove Point")
      del_point = st.selectbox(
          "Select Point to Delete",
          [p["name"] for p in store["monitoring_points"]],
          key="del_sel",
      )
      if st.button("Delete Selected Point", type="secondary"):
        store["monitoring_points"] = [
            p for p in store["monitoring_points"] if p["name"] != del_point
        ]
        st.success(f"Deleted {del_point} successfully!")
        st.rerun()
    else:
      st.info(
          "Note: Adding new points or deleting points requires Admin privileges,"
          " but you can edit existing point names/limits above."
      )

  # TAB 3: USER MANAGEMENT (ADMIN ONLY)
  with tabs[2]:
    if st.session_state.user_role == "admin":
      st.subheader("👥 System User Accounts")
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

      st.markdown("#### Create New User Account")
      nu_user = st.text_input("New Username", key="nu_user_input")
      nu_pass = st.text_input(
          "New Password", type="password", key="nu_pass_input"
      )
      nu_name = st.text_input("Full Name", key="nu_name_input")
      nu_email = st.text_input("Email", key="nu_email_input")
      nu_role = st.selectbox("Role", ["operator", "admin"], key="nu_role_input")

      if st.button("Create Account"):
        if nu_user and nu_pass:
          store["user_db"][nu_user] = {
              "pass": nu_pass,
              "name": nu_name,
              "role": nu_role,
              "email": nu_email,
          }
          st.success(f"User {nu_user} created successfully!")
          st.rerun()
        else:
          st.error("Username and Password are required.")
    else:
      st.warning("Access Restricted: Admin privileges required.")

  # TAB 4: LOG HISTORY
  with tabs[3]:
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
