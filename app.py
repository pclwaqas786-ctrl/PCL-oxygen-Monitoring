from datetime import datetime
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import streamlit as st

st.set_page_config(
    page_title="CCR Pakistan Cable - Oxygen Monitor",
    page_icon="🏭",
    layout="wide",
)

# --- GOOGLE SHEETS CONNECTION SETUP ---


def log_to_google_sheet(timestamp, item_name, val, status):
  try:
    scope = [
        "https://spreadsheets.google.com/feeds",
        "https://www.googleapis.com/auth/drive",
    ]
    creds = ServiceAccountCredentials.from_json_keyfile_name(
        "credentials.json", scope
    )
    client = gspread.authorize(creds)
    sheet = client.open("CCR_Oxygen_Logs").sheet1
    sheet.append_row([timestamp, item_name, val, status])
  except Exception as e:
    print(f"Google Sheet Logging Error: {e}")


# --- SESSION STATE INITIALIZATION ---
if "logged_in" not in st.session_state:
  st.session_state.logged_in = False

if "monitoring_points" not in st.session_state:
  st.session_state.monitoring_points = [
      {"name": "CR-1586 (Top/Tail)", "val": 449.0},
      {"name": "CR-1601 (Top End)", "val": 107.0},
      {"name": "CR-1603 (Top End)", "val": 577.0},
      {"name": "Shaft Furnace (SF-6)", "val": 292.0},
      {"name": "Tundish-Sample", "val": 512.0},
  ]

# Master Limits (Customizable via Admin Panel)
if "limits" not in st.session_state:
  st.session_state.limits = {
      "min_limit": 200.0,
      "normal_min": 200.0,
      "normal_max": 400.0,
      "caution_max": 600.0,
      "high_alert": 600.0,
  }

# --- HEADER TITLE ---
st.title("🏭 CCR Pakistan Cable (CCR Plant) - Oxygen & Coil Monitoring")
st.markdown(
    "Real-time oxygen tracking system with customizable master limits and 24/7"
    " Google Sheets logging."
)

# --- SIDEBAR: AUTHENTICATION & CONTROLS ---
st.sidebar.header("🔐 User / Admin Panel")

if not st.session_state.logged_in:
  st.sidebar.info("Viewing as Normal User (Quick value updates enabled)")
  admin_pass = st.sidebar.text_input("Enter Admin Password", type="password")
  if st.sidebar.button("Login as Admin"):
    if admin_pass == "admin123":  # Aap yahan apna password change kar sakte hain
      st.session_state.logged_in = True
      st.rerun()
    else:
      st.sidebar.error("Incorrect Password!")
else:
  st.sidebar.success("Logged in as ADMIN ✅")
  if st.sidebar.button("Logout"):
    st.session_state.logged_in = False
    st.rerun()

# --- STATUS FUNCTION WITH CUSTOM COLORS ---
any_high_alert = False


def get_oxygen_status(val, lim):
  global any_high_alert
  # Min or High Alert -> Red
  if val < lim["min_limit"] or val > lim["high_alert"]:
    any_high_alert = True
    return (
        "🔴 CRITICAL ALERT (Red)",
        "#ff4b4b",
        "Oxygen level out of safe limits!",
    )
  # Normal Range -> Green
  elif lim["normal_min"] <= val <= lim["normal_max"]:
    return "🟢 SAFE ZONE (Green)", "#09ab3b", "Normal safe range."
  # Caution Range -> Orange / Yellow
  elif lim["normal_max"] < val <= lim["caution_max"]:
    return "🟠 CAUTION ZONE (Orange)", "#ff8800", "Elevated range, monitor closely."
  else:
    any_high_alert = True
    return (
        "🔴 CRITICAL ALERT (Red)",
        "#ff4b4b",
        "Oxygen level out of safe limits!",
    )


# --- ADMIN-ONLY MASTER SETTINGS & MANAGEMENT ---
if st.session_state.logged_in:
  st.sidebar.markdown("---")
  st.sidebar.subheader("⚙️ Admin: Master Limits Configuration")
  st.session_state.limits["min_limit"] = st.sidebar.number_input(
      "Minimum Limit (Below this = Red)",
      value=st.session_state.limits["min_limit"],
  )
  st.session_state.limits["normal_min"] = st.sidebar.number_input(
      "Normal Range Start", value=st.session_state.limits["normal_min"]
  )
  st.session_state.limits["normal_max"] = st.sidebar.number_input(
      "Normal Range End (Green)", value=st.session_state.limits["normal_max"]
  )
  st.session_state.limits["caution_max"] = st.sidebar.number_input(
      "Caution Max (Up to this = Orange)",
      value=st.session_state.limits["caution_max"],
  )
  st.session_state.limits["high_alert"] = st.sidebar.number_input(
      "High Alert Limit (Above this = Red)",
      value=st.session_state.limits["high_alert"],
  )

  st.sidebar.markdown("---")
  st.sidebar.subheader("📋 Admin: Add / Delete Points")
  new_point = st.sidebar.text_input("Add New Coil / Furnace / Tundish")
  if st.sidebar.button("Add Point"):
    if new_point:
      st.session_state.monitoring_points.append(
          {"name": new_point, "val": 300.0}
      )
      st.rerun()

  for i, item in enumerate(st.session_state.monitoring_points):
    cols = st.sidebar.columns([3, 2])
    with cols[0]:
      item["name"] = st.text_input(
          f"N_{i}", item["name"], key=f"edit_name_{i}"
      )
    with cols[1]:
      new_val = st.number_input(
          f"V_{i}", value=float(item["val"]), key=f"edit_val_{i}"
      )
      if new_val != item["val"]:
        item["val"] = new_val
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        status_text, _, _ = get_oxygen_status(
            new_val, st.session_state.limits
        )
        log_to_google_sheet(
            current_time, item["name"], new_val, status_text
        )

    if st.sidebar.button(f"Del {item['name']}", key=f"del_{i}"):
      st.session_state.monitoring_points.pop(i)
      st.rerun()
else:
  # Normal User Value Updates with Google Sheets Logging
  st.sidebar.markdown("---")
  st.sidebar.subheader("⚡ Quick Value Update")
  for i, item in enumerate(st.session_state.monitoring_points):
    new_val = st.sidebar.number_input(
        f"{item['name']}", value=float(item["val"]), key=f"user_val_{i}"
    )
    if new_val != item["val"]:
      item["val"] = new_val
      current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
      status_text, _, _ = get_oxygen_status(new_val, st.session_state.limits)
      log_to_google_sheet(current_time, item["name"], new_val, status_text)


# --- MAIN DISPLAY CARDS ---
st.markdown("---")
cols = st.columns(3)

lims = st.session_state.limits
for idx, item in enumerate(st.session_state.monitoring_points):
  title = item["name"]
  val = item["val"]
  status_text, bg_color, message = get_oxygen_status(val, lims)

  with cols[idx % 3]:
    st.markdown(
        f"""
        <div style="padding: 22px; border-radius: 12px; background-color: #1e1e1e; border: 3px solid {bg_color}; text-align: center; box-shadow: 0 4px 10px rgba(0,0,0,0.5); margin-bottom: 20px;">
            <h3 style="color: #ffffff; margin-bottom: 5px; font-size: 18px;">{title}</h3>
            <h1 style="color: {bg_color}; font-size: 42px; margin: 10px 0;">{val} <span style="font-size: 20px;">ppm</span></h1>
            <p style="color: {bg_color}; font-weight: bold; font-size: 15px; margin-bottom: 5px;">{status_text}</p>
            <p style="color: #b0b0b0; font-size: 12px;">{message}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

# --- AUDIO ALERT ---
if any_high_alert:
  st.error("🚨 HIGH ALERT! Critical oxygen level detected in the plant!")
  st.markdown(
      """
        <audio autoplay>
          <source src="https://assets.mixkit.co/active_storage/sfx/2869/2869-preview.mp3" type="audio/mpeg">
        </audio>
        """,
      unsafe_allow_html=True,
  )
