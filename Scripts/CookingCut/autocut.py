import time
import threading
import keyboard
import pyautogui

# ←––––– CONFIG –––––––––––––––––––––––––––––––––––––––––
FPS            = 30            # your sequence’s framerate
INTERVAL_SECS  = 0.5           # cut every 0.5s
DURATION_SECS  = 12 * 60       # total sequence length (seconds)
TIMEBOX_X      = 1340          # your measured X
TIMEBOX_Y      = 1312          # your measured Y
# ────────────────────────────────────────────────────────

# how many slices?
slices = int(DURATION_SECS / INTERVAL_SECS)

def sec_to_timecode(t):
    hh = int(t // 3600)
    mm = int((t % 3600) // 60)
    ss = int(t % 60)
    ff = int((t - int(t)) * FPS)
    return f"{hh:02d}:{mm:02d}:{ss:02d}:{ff:02d}"

running = False

def cutter():
    for i in range(1, slices + 1):
        if not running:
            break
        tc = sec_to_timecode(i * INTERVAL_SECS)
        # 1) click into the TC box
        pyautogui.click(TIMEBOX_X, TIMEBOX_Y)
        time.sleep(0.05)
        # 2) select all and type new timecode
        pyautogui.hotkey('ctrl', 'a')
        pyautogui.typewrite(tc, interval=0)
        pyautogui.press('enter')
        # 3) razor-cut both audio & video
        pyautogui.hotkey('ctrl', 'shift', 'k')
        # tiny pause so Premiere can catch up
        time.sleep(0.02)
    print("✅ Done slicing.")

def toggle():
    global running
    running = not running
    if running:
        print("▶️ Auto-slice started")
        threading.Thread(target=cutter, daemon=True).start()
    else:
        print("⏹ Auto-slice stopped")

print(f"Press F6 to start/stop slicing every {INTERVAL_SECS}s ({int(FPS*INTERVAL_SECS)} frames).")
keyboard.add_hotkey('F6', toggle)
keyboard.wait('esc')
