import pyautogui
import time
import sys
import subprocess
from datetime import datetime

EXECUTE_BTN = (436, 143)  # 执行按钮坐标

def activate_datastudio():
    """Force activate Data Studio window - must be called before each query"""
    # Try multiple times
    for attempt in range(3):
        wins = [w for w in pyautogui.getWindowsWithTitle('Data Studio : AhuDB2026')]
        if not wins:
            wins = [w for w in pyautogui.getWindowsWithTitle('Data Studio') if 'AhuDB2026' in w.title]
        if not wins:
            wins = [w for w in pyautogui.getWindowsWithTitle('Data Studio') if w.visible]

        if wins:
            w = wins[0]
            # Restore if minimized
            if w.left <= -32000 or w.top <= -32000:
                w.restore()
                time.sleep(0.5)
            # Bring to front
            w.activate()
            time.sleep(0.3)
            # Ensure maximized
            if w.width < 500:
                w.maximize()
                time.sleep(0.3)
            return True
        time.sleep(0.5)

    print("  WARNING: Data Studio window not found!")
    return False

def copy_to_clipboard(text):
    """Copy text to clipboard using clip.exe"""
    try:
        process = subprocess.Popen(
            ['clip.exe'],
            stdin=subprocess.PIPE,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
        process.communicate(input=text.encode('utf-8'))
        process.wait()
        return True
    except Exception as e:
        print(f"  Clipboard error: {e}")
        return False

def dismiss_error_dialog():
    """Dismiss any error dialogs by pressing Enter"""
    time.sleep(2)
    pyautogui.press('enter')
    time.sleep(0.5)

def run_query(query, screenshot_name):
    # Step 1: ALWAYS switch to Data Studio first
    if not activate_datastudio():
        print("ERROR: Data Studio not found - aborting")
        return None
    time.sleep(0.5)

    # Step 2: Copy query to clipboard
    copy_to_clipboard(query)
    time.sleep(0.2)

    # Step 3: Click in the SQL editor area
    pyautogui.click(900, 450)
    time.sleep(0.3)

    # Step 4: Select all and paste
    pyautogui.hotkey('ctrl', 'a')
    time.sleep(0.1)
    pyautogui.hotkey('ctrl', 'v')
    time.sleep(0.5)

    # Step 5: Click execute button
    pyautogui.click(EXECUTE_BTN[0], EXECUTE_BTN[1])
    print(f"  Exec: {screenshot_name}")

    # Step 6: Dismiss error dialogs and wait
    dismiss_error_dialog()
    time.sleep(3)
    dismiss_error_dialog()

    # Step 7: Screenshot
    fname = f'c:/Users/23692/Desktop/picture/{screenshot_name}.png'
    pyautogui.screenshot(fname)
    print(f"  OK: {fname}")
    return fname

if __name__ == '__main__':
    if len(sys.argv) >= 3:
        run_query(sys.argv[1], sys.argv[2])
    elif len(sys.argv) >= 2:
        run_query(sys.argv[1], 'query_result')
    else:
        print("Usage: python run_query.py 'SQL' 'screenshot_name'")
