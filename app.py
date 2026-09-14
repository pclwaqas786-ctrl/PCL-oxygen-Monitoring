from datetime import datetime
import base64
import gspread
import streamlit as st

st.set_page_config(
    page_title="CCR Oxygen & Coil Monitoring",
    page_icon="🏭",
    layout="wide",
)

# --- USER ACCOUNTS DATABASE ---
USER_CREDENTIALS = {
    "admin": {"pass": "admin123", "name": "Admin Manager", "role": "admin"},
    "user1": {
        "pass": "user123",
        "name": "User 1 (Shift Officer)",
        "role": "operator",
    },
    "user2": {"pass": "user223", "name": "User 2 (Operator)", "role": "operator"},
    "user3": {
        "pass": "user323",
        "name": "User 3 (QC Inspector)",
        "role": "operator",
    },
}

# --- GOOGLE SHEETS CONNECTION SETUP ---
def log_to_google_sheet(timestamp, user_name, shift, item_name, val, status):
  try:
    creds_dict = dict(st.secrets["gcp_service_account"])
    creds_dict["private_key"] = creds_dict["private_key"].replace("\\n", "\n")

    gc = gspread.service_account_from_dict(creds_dict)
    sheet = gc.open("CCR_Oxygen_Logs").sheet1
    sheet.append_row([timestamp, user_name, shift, item_name, val, status])
  except Exception as e:
    st.error(f"Google Sheet Logging Failed: {e}")


# --- SESSION STATE INITIALIZATION ---
if "logged_in" not in st.session_state:
  st.session_state.logged_in = False
  st.session_state.user_info = None

if "current_shift" not in st.session_state:
  st.session_state.current_shift = "Shift A"

if "app_title" not in st.session_state:
  st.session_state.app_title = "CCR Pakistan Cable - Oxygen & Coil Monitoring"

if "app_subtitle" not in st.session_state:
  st.session_state.app_subtitle = (
      "Real-time oxygen tracking system with individual item thresholds"
      " and 24/7 Google Sheets logging."
  )

if "bg_image" not in st.session_state:
  st.session_state.bg_image = ""

if "logo_image" not in st.session_state:
  st.session_state.logo_image = ""

if "monitoring_points" not in st.session_state:
  st.session_state.monitoring_points = [
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
          "val": 107.0,
          "min": 150.0,
          "norm_min": 150.0,
          "norm_max": 350.0,
          "caution_max": 500.0,
          "high": 500.0,
      },
      {
          "name": "CR-2486 (Top End)",
          "val": 577.0,
          "min": 200.0,
          "norm_min": 200.0,
          "norm_max": 400.0,
          "caution_max": 600.0,
          "high": 600.0,
      },
      {
          "name": "Shaft Furnace (SF-6)",
          "val": 292.0,
          "min": 180.0,
          "norm_min": 180.0,
          "norm_max": 380.0,
          "caution_max": 550.0,
          "high": 550.0,
      },
      {
          "name": "Tundish-Sample",
          "val": 512.0,
          "min": 200.0,
          "norm_min": 200.0,
          "norm_max": 450.0,
          "caution_max": 650.0,
          "high": 650.0,
      },
  ]

# --- PERSISTENT BACKGROUND WALLPAPER ---
if st.session_state.bg_image:
  bg_css = f"""
    <style>
    .stApp {{
        background-image: linear-gradient(rgba(14, 17, 23, 0.88), rgba(14, 17, 23, 0.88)), url("{st.session_state.bg_image}");
        background-size: cover;
        background-position: center;
        background-attachment: fixed;
    }}
    </style>
    """
  st.markdown(bg_css, unsafe_allow_html=True)

# --- HEADER DISPLAY ---
col_logo, col_title = st.columns([1, 6])

with col_logo:
  if st.session_state.logo_image:
    st.image(st.session_state.logo_image, width=100)
  else:
    st.title("🏭")

with col_title:
  st.title(st.session_state.app_title)
  st.markdown(f"*{st.session_state.app_subtitle}*")

st.markdown("---")

# --- SIDEBAR: LOGIN & CONTROLS ---
st.sidebar.header("🔐 User Login & Controls")

if not st.session_state.logged_in:
  st.sidebar.warning(
      "🔒 Read-Only Mode. Please log in to enable data updates."
  )

  input_user = st.sidebar.text_input("Username", key="login_user")
  input_pass = st.sidebar.text_input(
      "Password", type="password", key="login_pass"
  )
  input_shift = st.sidebar.selectbox(
      "Select Duty Shift", ["Shift A", "Shift B", "Shift C"], key="login_shift"
  )

  if st.sidebar.button("Login to Dashboard"):
    if (
        input_user in USER_CREDENTIALS
        and USER_CREDENTIALS[input_user]["pass"] == input_pass
    ):
      st.session_state.logged_in = True
      st.session_state.user_info = USER_CREDENTIALS[input_user]
      st.session_state.current_shift = input_shift
      st.rerun()
    else:
      st.sidebar.error("❌ Incorrect Username or Password!")
else:
  u_info = st.session_state.user_info
  st.sidebar.success(f"👤 **Logged in:** {u_info['name']}")
  st.sidebar.info(f"⏱️ **Active Shift:** {st.session_state.current_shift}")

  new_shift = st.sidebar.selectbox(
      "Change Shift",
      ["Shift A", "Shift B", "Shift C"],
      index=["Shift A", "Shift B", "Shift C"].index(
          st.session_state.current_shift
      ),
  )
  st.session_state.current_shift = new_shift

  if st.sidebar.button("Logout"):
    st.session_state.logged_in = False
    st.session_state.user_info = None
    st.rerun()

# --- STATUS FUNCTION ---
any_high_alert = False


def get_oxygen_status(val, item):
  global any_high_alert
  if val < item["min"] or val > item["high"]:
    any_high_alert = True
    return (
        "🔴 CRITICAL ALERT (Red)",
        "#ff4b4b",
        "Oxygen level out of safe limits!",
    )
  elif item["norm_min"] <= val <= item["norm_max"]:
    return "🟢 SAFE ZONE (Green)", "#09ab3b", "Normal safe range."
  elif item["norm_max"] < val <= item["caution_max"]:
    return "🟠 CAUTION ZONE (Orange)", "#ff8800", "Elevated range, monitor closely."
  else:
    any_high_alert = True
    return (
        "🔴 CRITICAL ALERT (Red)",
        "#ff4b4b",
        "Oxygen level out of safe limits!",
    )


# --- ADMIN & DATA ENTRY CONTROLS ---
if st.session_state.logged_in:
  role = st.session_state.user_info["role"]
  user_display_name = st.session_state.user_info["name"]

  if role == "admin":
    st.sidebar.markdown("---")
    st.sidebar.subheader("🎨 Admin: Header & Branding")

    with st.sidebar.expander("📝 Edit App Title & Subtitle"):
      st.session_state.app_title = st.text_input(
          "Main Title", st.session_state.app_title
      )
      st.session_state.app_subtitle = st.text_area(
          "Subtitle", st.session_state.app_subtitle
      )

    with st.sidebar.expander("🖼️ Company Logo & Wallpaper"):
      logo_file = st.file_uploader(
          "Upload Logo Image", type=["jpg", "png", "jpeg"], key="logo_upload"
      )
      if logo_file is not None:
        bytes_data = logo_file.getvalue()
        base64_img = base64.b64encode(bytes_data).decode()
        st.session_state.logo_image = (
            f"data:{logo_file.type};base64,{base64_img}"
        )

      bg_file = st.file_uploader(
          "Upload Background Wallpaper",
          type=["jpg", "png", "jpeg"],
          key="bg_upload",
      )
      if bg_file is not None:
        bytes_data = bg_file.getvalue()
        base64_img = base64.b64encode(bytes_data).decode()
        st.session_state.bg_image = f"data:{bg_file.type};base64,{base64_img}"

    st.sidebar.markdown("---")
    st.sidebar.subheader("⚙️ Admin: Thresholds & Items")

    new_point = st.sidebar.text_input(
        "Add New Point Name", key="new_point_input"
    )
    if st.sidebar.button("Add Point"):
      if new_point:
        st.session_state.monitoring_points.append({
            "name": new_point,
            "val": 300.0,
            "min": 200.0,
            "norm_min": 200.0,
            "norm_max": 400.0,
            "caution_max": 600.0,
            "high": 600.0,
        })
        st.rerun()

  st.sidebar.markdown("---")
  st.sidebar.subheader("⚡ Quick Data Entry")

  for i, item in enumerate(st.session_state.monitoring_points):
    with st.sidebar.expander(f"Update: {item['name']}"):
      item["name"] = st.text_input(
          "Coil / Item Name", item["name"], key=f"user_name_{i}"
      )
      new_val = st.number_input(
          "Oxygen Value (ppm)", value=float(item["val"]), key=f"user_val_{i}"
      )

      if role == "admin":
        item["min"] = st.number_input(
            "Min Limit (Red)", value=float(item["min"]), key=f"min_{i}"
        )
        item["norm_min"] = st.number_input(
            "Normal Min", value=float(item["norm_min"]), key=f"nmin_{i}"
        )
        item["norm_max"] = st.number_input(
            "Normal Max (Green)",
            value=float(item["norm_max"]),
            key=f"nmax_{i}",
        )
        item["caution_max"] = st.number_input(
            "Caution Max (Orange)",
            value=float(item["caution_max"]),
            key=f"cmax_{i}",
        )
        item["high"] = st.number_input(
            "High Limit (Red)", value=float(item["high"]), key=f"high_{i}"
        )

        if st.button(f"Delete {item['name']}", key=f"del_{i}"):
          st.session_state.monitoring_points.pop(i)
          st.rerun()

      if new_val != item["val"]:
        item["val"] = new_val
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        status_text, _, _ = get_oxygen_status(new_val, item)

        log_to_google_sheet(
            current_time,
            user_display_name,
            st.session_state.current_shift,
            item["name"],
            new_val,
            status_text,
        )

else:
  st.info(
      "💡 **Note:** Display values are currently in live monitoring mode. Please"
      " log in via the sidebar to update values."
  )

# --- CARDS DISPLAY ---
cols = st.columns(3)

for idx, item in enumerate(st.session_state.monitoring_points):
  title = item["name"]
  val = item["val"]
  status_text, bg_color, message = get_oxygen_status(val, item)

  with cols[idx % 3]:
    st.markdown(
        f"""
        <div style="padding: 22px; border-radius: 12px; background-color: rgba(30, 30, 30, 0.92); border: 3px solid {bg_color}; text-align: center; box-shadow: 0 4px 10px rgba(0,0,0,0.5); margin-bottom: 20px;">
            <h3 style="color: #ffffff; margin-bottom: 5px; font-size: 18px;">{title}</h3>
            <h1 style="color: {bg_color}; font-size: 42px; margin: 10px 0;">{val} <span style="font-size: 20px;">ppm</span></h1>
            <p style="color: {bg_color}; font-weight: bold; font-size: 15px; margin-bottom: 5px;">{status_text}</p>
            <p style="color: #b0b0b0; font-size: 12px;">{message}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

# --- CONTINUOUS ALARM SOUND & VISUAL ALERT ---
if any_high_alert:
  st.toast(
      "🚨 CRITICAL ALERT: Oxygen level is out of safe limits!", icon="⚠️"
  )

  alert_html = """
    <div style="background-color: #8b0000; color: white; padding: 18px; border-radius: 10px; text-align: center; margin-bottom: 20px; border: 2px solid #ff4b4b;">
        <h2 style="margin:0 0 8px 0; color: #ffffff;">🚨 CRITICAL HIGH ALERT!</h2>
        <p style="font-size: 16px; margin:0 0 12px 0;">Oxygen level has exceeded safe operating limits!</p>
        <button id="alarm-btn" onclick="triggerAlarmSound()" style="background-color: #ff4b4b; color: white; border: none; padding: 10px 20px; font-size: 15px; border-radius: 6px; cursor: pointer; font-weight: bold; box-shadow: 0 4px 6px rgba(0,0,0,0.3);">
            🔔 CLICK HERE TO START ALARM SOUND 🔊
        </button>
    </div>

    <script>
    (function() {
        var AudioContext = window.AudioContext || window.webkitAudioContext;
        if (!AudioContext) return;
        var ctx = new AudioContext();

        function playLoudBeep() {
            if (ctx.state === 'suspended') {
                ctx.resume();
            }
            var osc = ctx.createOscillator();
            var gain = ctx.createGain();
            osc.type = 'sawtooth';
            osc.frequency.setValueAtTime(950, ctx.currentTime);
            gain.gain.setValueAtTime(0.5, ctx.currentTime);
            osc.connect(gain);
            gain.connect(ctx.destination);
            osc.start();
            osc.stop(ctx.currentTime + 0.35);
        }

        playLoudBeep();
        var alarmInterval = setInterval(playLoudBeep, 650);

        setTimeout(function() {
            clearInterval(alarmInterval);
        }, 60000);

        window.triggerAlarmSound = function() {
            ctx.resume().then(function() {
                playLoudBeep();
                var btn = document.getElementById("alarm-btn");
                if (btn) btn.innerText = "🚨 ALARM RINGING (1 MINUTE)...";
            });
        };
    })();
    </script>
    """
  st.markdown(alert_html, unsafe_allow_html=True)
