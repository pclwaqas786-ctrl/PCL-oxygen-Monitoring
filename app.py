import streamlit as st

st.set_page_config(
    page_title="CCR Pakistan Cable - Oxygen Monitor",
    page_icon="🏭",
    layout="wide",
)

# --- SESSION STATE INITIALIZATION ---
if "logged_in" not in st.session_state:
  st.session_state.logged_in = False

if "monitoring_points" not in st.session_state:
  st.session_state.monitoring_points = [
      {"name": "CR-1586 (Top/Tail)", "val": 449.0},
      {"name": "CR-1601 (Top End)", "val": 107.0},
      {"name": "CR-1603 (Top End)", "val": 577.0},
      {"name": "Shaft Furnace (SF-6)", "val": 292.0},
      {"name": "Tundish-03 Sample", "val": 512.0},
  ]

if "limits" not in st.session_state:
  st.session_state.limits = {
      "normal_min": 200.0,
      "normal_max": 400.0,
      "warning_max": 600.0,
      "high_alert": 600.0,
  }

# --- HEADER TITLE ---
st.title("🏭 CCR Pakistan Cable (CCR Plant) - Oxygen & Coil Monitoring")
st.markdown("Real-time oxygen tracking system with admin security.")

# --- SIDEBAR: ADMIN LOGIN ---
st.sidebar.header("🔐 Admin Security Panel")
if not st.session_state.logged_in:
  admin_pass = st.sidebar.text_input("Enter Admin Password", type="password")
  if st.sidebar.button("Login"):
    if admin_pass == "admin123":  # Yahan aap apna marzi ka password rakh sakte hain
      st.session_state.logged_in = True
      st.sidebar.success("Logged in successfully!")
      st.rerun()
    else:
      st.sidebar.error("Wrong Password!")
else:
  st.sidebar.success("Status: Logged In as Admin ✅")
  if st.sidebar.button("Logout"):
    st.session_state.logged_in = False
    st.rerun()

# --- ADMIN CONTROLS (Only visible after login) ---
if st.session_state.logged_in:
  st.sidebar.markdown("---")
  st.sidebar.subheader("⚙️ Edit Limits & Thresholds")
  st.session_state.limits["normal_min"] = st.sidebar.number_input(
      "Normal Min", value=st.session_state.limits["normal_min"]
  )
  st.session_state.limits["normal_max"] = st.sidebar.number_input(
      "Normal Max", value=st.session_state.limits["normal_max"]
  )
  st.session_state.limits["warning_max"] = st.sidebar.number_input(
      "Caution Max", value=st.session_state.limits["warning_max"]
  )
  st.session_state.limits["high_alert"] = st.sidebar.number_input(
      "High Alert Limit", value=st.session_state.limits["high_alert"]
  )

  st.sidebar.markdown("---")
  st.sidebar.subheader("📋 Add / Delete / Edit Points")

  new_point = st.sidebar.text_input("Add New Coil / Furnace")
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
      item["val"] = st.number_input(
          f"V_{i}", value=float(item["val"]), key=f"edit_val_{i}"
      )
    if st.sidebar.button(f"Del {item['name']}", key=f"del_{i}"):
      st.session_state.monitoring_points.pop(i)
      st.rerun()

# --- STATUS CHECK FUNCTION ---
any_high_alert = False


def get_oxygen_status(val, lim):
  global any_high_alert
  if val < lim["normal_min"] or val > lim["high_alert"]:
    any_high_alert = True
    return "🔴 KHATRA (Critical Alert)", "#ff4b4b", "Oxygen out of limits!"
  elif lim["normal_min"] <= val <= lim["normal_max"]:
    return "🟢 THEEK (Safe Zone)", "#09ab3b", "Normal safe range."
  elif lim["normal_max"] < val <= lim["warning_max"]:
    return "🟡 CAUTION (Yellow Zone)", "#f6b93b", "Elevated range."
  else:
    any_high_alert = True
    return "🔴 KHATRA (Alert)", "#ff4b4b", "Critical level!"


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
  st.error("🚨 HIGH ALERT! Critical oxygen level detected!")
  st.markdown(
      """
        <audio autoplay>
          <source src="https://assets.mixkit.co/active_storage/sfx/2869/2869-preview.mp3" type="audio/mpeg">
        </audio>
        """,
      unsafe_allow_html=True,
  )
