from datetime import datetime
import base64
import gspread
import streamlit as st

st.set_page_config(
    page_title="Oxygen & Coil Monitoring",
    page_icon="🏭",
    layout="wide",
)

# --- GOOGLE SHEETS CONNECTION SETUP ---


def log_to_google_sheet(timestamp, item_name, val, status):
  try:
    creds_dict = dict(st.secrets["gcp_service_account"])
    creds_dict["private_key"] = creds_dict["private_key"].replace("\\n", "\n")

    gc = gspread.service_account_from_dict(creds_dict)
    sheet = gc.open("CCR_Oxygen_Logs").sheet1
    sheet.append_row([timestamp, item_name, val, status])
  except Exception as e:
    st.error(f"Google Sheet Logging Failed: {e}")


# --- SESSION STATE INITIALIZATION ---
if "logged_in" not in st.session_state:
  st.session_state.logged_in = False

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

# --- DYNAMIC BACKGROUND CSS ---
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

# --- HEADER TITLE & LOGO DISPLAY ---
col_logo, col_title = st.columns([1, 6])

with col_logo:
  if st.session_state.logo_image:
    st.image(st.session_state.logo_image, width=110)
  else:
    st.title("🏭")

with col_title:
  st.title(st.session_state.app_title)
  st.markdown(f"*{st.session_state.app_subtitle}*")

st.markdown("---")

# --- SIDEBAR: AUTHENTICATION & CONTROLS ---
st.sidebar.header("🔐 User / Admin Panel")

if not st.session_state.logged_in:
  st.sidebar.info(
      "Viewing as Normal User (Quick value updates & Coil name editing enabled)"
  )
  admin_pass = st.sidebar.text_input(
      "Enter Admin Password", type="password", key="admin_pass_input"
  )
  if st.sidebar.button("Login as Admin"):
    if admin_pass == "admin123":
      st.session_state.logged_in = True
      st.rerun()
    else:
      st.sidebar.error("Incorrect Password!")
else:
  st.sidebar.success("Logged in as ADMIN ✅")
  if st.sidebar.button("Logout"):
    st.session_state.logged_in = False
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


# --- ADMIN PANEL ---
if st.session_state.logged_in:
  st.sidebar.markdown("---")
  st.sidebar.subheader("🎨 Customize App Branding & Title")

  with st.sidebar.expander("📝 Edit App Header & Title"):
    st.session_state.app_title = st.text_input(
        "Main Title", st.session_state.app_title
    )
    st.session_state.app_subtitle = st.text_area(
        "Subtitle", st.session_state.app_subtitle
    )

  with st.sidebar.expander("🖼️ Change Logo & Background"):
    logo_url = st.text_input("Logo Image URL", st.session_state.logo_image)
    if logo_url != st.session_state.logo_image:
      st.session_state.logo_image = logo_url

    bg_url = st.text_input("Background Wallpaper URL", st.session_state.bg_image)
    if bg_url != st.session_state.bg_image:
      st.session_state.bg_image = bg_url

    bg_file = st.file_uploader("Upload Background Image", type=["jpg", "png"])
    if bg_file is not None:
      bytes_data = bg_file.getvalue()
      base64_img = base64.b64encode(bytes_data).decode()
      st.session_state.bg_image = f"data:image/jpeg;base64,{base64_img}"

  st.sidebar.markdown("---")
  st.sidebar.subheader("⚙️ Admin: Manage Items & Thresholds")

  new_point = st.sidebar.text_input("Add New Point Name", key="new_point_input")
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

  for i, item in enumerate(st.session_state.monitoring_points):
    with st.sidebar.expander(f"Edit: {item['name']}"):
      item["name"] = st.text_input(
          "Item / Coil Name", item["name"], key=f"name_{i}"
      )
      new_val = st.number_input(
          "Current Value (ppm)", value=float(item["val"]), key=f"val_{i}"
      )
      if new_val != item["val"]:
        item["val"] = new_val
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        status_text, _, _ = get_oxygen_status(new_val, item)
        log_to_google_sheet(current_time, item["name"], new_val, status_text)

      item["min"] = st.number_input(
          "Min Limit (Red)", value=float(item["min"]), key=f"min_{i}"
      )
      item["norm_min"] = st.number_input(
          "Normal Min", value=float(item["norm_min"]), key=f"nmin_{i}"
      )
      item["norm_max"] = st.number_input(
          "Normal Max (Green)", value=float(item["norm_max"]), key=f"nmax_{i}"
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

else:
  # NORMAL USER PANEL
  st.sidebar.markdown("---")
  st.sidebar.subheader("⚡ Quick Updates (Coil & Value)")
  for i, item in enumerate(st.session_state.monitoring_points):
    with st.sidebar.expander(f"Update: {item['name']}"):
      item["name"] = st.text_input(
          "Coil Name", item["name"], key=f"user_name_{i}"
      )
      new_val = st.number_input(
          "Value (ppm)", value=float(item["val"]), key=f"user_val_{i}"
      )
      if new_val != item["val"]:
        item["val"] = new_val
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        status_text, _, _ = get_oxygen_status(new_val, item)
        log_to_google_sheet(current_time, item["name"], new_val, status_text)

# --- MAIN DISPLAY CARDS ---
cols = st.columns(3)

for idx, item in enumerate(st.session_state.monitoring_points):
  title = item["name"]
  val = item["val"]
  status_text, bg_color, message = get_oxygen_status(val, item)

  with cols[idx % 3]:
    st.markdown(
        f"""
        <div style="padding: 22px; border-radius: 12px; background-color: rgba(30, 30, 30, 0.9); border: 3px solid {bg_color}; text-align: center; box-shadow: 0 4px 10px rgba(0,0,0,0.5); margin-bottom: 20px;">
            <h3 style="color: #ffffff; margin-bottom: 5px; font-size: 18px;">{title}</h3>
            <h1 style="color: {bg_color}; font-size: 42px; margin: 10px 0;">{val} <span style="font-size: 20px;">ppm</span></h1>
            <p style="color: {bg_color}; font-weight: bold; font-size: 15px; margin-bottom: 5px;">{status_text}</p>
            <p style="color: #b0b0b0; font-size: 12px;">{message}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

# --- CONTINUOUS WEB AUDIO SYNTHESIZER ALARM & POPUP TOAST ---
if any_high_alert:
  st.error("🚨 CRITICAL HIGH ALERT! Oxygen level out of safe limits!")
  st.toast(
      "🚨 CRITICAL ALERT: Oxygen level critical limits se bahar hai!", icon="⚠️"
  )

  synth_alarm_html = """
        <script>
        (function() {
            try {
                var AudioContext = window.AudioContext || window.webkitAudioContext;
                if (!AudioContext) return;
                var ctx = new AudioContext();

                function playBeep() {
                    if (ctx.state === 'suspended') {
                        ctx.resume();
                    }
                    var osc = ctx.createOscillator();
                    var gain = ctx.createGain();
                    osc.type = 'sawtooth';
                    osc.frequency.setValueAtTime(850, ctx.currentTime);
                    gain.gain.setValueAtTime(0.3, ctx.currentTime);
                    osc.connect(gain);
                    gain.connect(ctx.destination);
                    osc.start();
                    osc.stop(ctx.currentTime + 0.4);
                }

                playBeep();
                var alarmInterval = setInterval(playBeep, 800);

                setTimeout(function() {
                    clearInterval(alarmInterval);
                }, 60000);
            } catch(e) {
                console.log("Audio synth error:", e);
            }
        })();
        </script>
    """
  st.markdown(synth_alarm_html, unsafe_allow_html=True)
