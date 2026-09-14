# --- CONTINUOUS ALARM SOUND & VISUAL ALERT ---
if any_high_alert:
  st.toast(
      "🚨 CRITICAL ALERT: Oxygen level critical limits se bahar hai!", icon="⚠️"
  )

  # Loud Red Alert Box with Manual Sound Trigger Button for Browser Permission
  alert_html = """
    <div style="background-color: #8b0000; color: white; padding: 18px; border-radius: 10px; text-align: center; margin-bottom: 20px; border: 2px solid #ff4b4b;">
        <h2 style="margin:0 0 8px 0; color: #ffffff;">🚨 CRITICAL HIGH ALERT!</h2>
        <p style="font-size: 16px; margin:0 0 12px 0;">Oxygen level safe limits se bahar ho gaya hai!</p>
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

        // Auto-play attempt
        playLoudBeep();
        var alarmInterval = setInterval(playLoudBeep, 650);

        // Stop sound automatically after 1 minute
        setTimeout(function() {
            clearInterval(alarmInterval);
        }, 60000);

        // Manual override button trigger if browser blocks autoplay
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
