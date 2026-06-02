import pyautogui
import pyperclip
import time
import sys
import subprocess
from datetime import datetime

EXECUTE_BTN = (436, 143)

def activate_datastudio():
    for attempt in range(3):
        wins = [w for w in pyautogui.getWindowsWithTitle('Data Studio : AhuDB2026')]
        if wins:
            w = wins[0]
            if w.left <= -32000 or w.top <= -32000:
                w.restore()
                time.sleep(0.5)
            w.activate()
            time.sleep(0.3)
            return True
        time.sleep(0.5)
    print("  WARNING: Data Studio not found!")
    return False

def run_sql_file(sql_file, screenshot_name):
    # Read SQL from file
    with open(sql_file, 'r', encoding='utf-8') as f:
        query = f.read()

    if not activate_datastudio():
        print("ERROR: Data Studio not found")
        return None
    time.sleep(0.5)

    # Copy to clipboard — use pyperclip for proper Unicode support
    pyperclip.copy(query)
    time.sleep(0.2)

    # Click in editor, select all, delete, then paste
    pyautogui.click(900, 450)
    time.sleep(0.3)
    pyautogui.hotkey('ctrl', 'a')
    time.sleep(0.1)
    pyautogui.press('delete')
    time.sleep(0.1)
    pyautogui.hotkey('ctrl', 'v')
    time.sleep(0.5)

    # Execute
    pyautogui.click(EXECUTE_BTN[0], EXECUTE_BTN[1])
    print(f"  Exec: {screenshot_name}")

    # Dismiss dialogs
    time.sleep(2)
    pyautogui.press('enter')
    time.sleep(0.5)
    time.sleep(3)
    pyautogui.press('enter')
    time.sleep(0.5)

    fname = f'c:/Users/23692/Desktop/picture/{screenshot_name}.png'
    pyautogui.screenshot(fname)
    print(f"  OK: {fname}")
    return fname

if __name__ == '__main__':
    if len(sys.argv) >= 3:
        run_sql_file(sys.argv[1], sys.argv[2])
    else:
        print("Usage: python query_runner.py <sql_file> <screenshot_name>")
