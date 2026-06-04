"""Day 8 Bonus Challenge 1: ETL Cron Job

Windows Task Scheduler script for automated weekday 8 PM NAV fetch.

Setup Instructions:
1. Open Task Scheduler (taskschd.msc)
2. Create Basic Task:
   - Name: "MF NAV Auto-Fetch"
   - Trigger: Daily @ 8:00 PM (Mon-Fri only)
   - Action: Start a program
   - Program: C:\Users\HP\OneDrive\Desktop\mutual funds\.venv\Scripts\python.exe
   - Arguments: C:\Users\HP\OneDrive\Desktop\mutual funds\live_nav_fetch.py
3. Conditions: Run only if on AC power (optional)
4. Settings: Run task as soon as possible if missed
"""

import subprocess
import sys
from pathlib import Path
from datetime import datetime

BASE_DIR = Path(__file__).resolve().parent
LIVE_NAV_SCRIPT = BASE_DIR / "live_nav_fetch.py"
LOG_FILE = BASE_DIR / "logs" / "nav_fetch_schedule.log"

def run_nav_fetch():
    """Execute live NAV fetch with logging"""
    LOG_FILE.parent.mkdir(exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    with open(LOG_FILE, "a") as log:
        log.write(f"\n[{timestamp}] Starting NAV fetch...\n")
        
        try:
            result = subprocess.run(
                [sys.executable, str(LIVE_NAV_SCRIPT)],
                capture_output=True,
                text=True,
                timeout=300
            )
            
            log.write(result.stdout)
            if result.stderr:
                log.write(f"STDERR: {result.stderr}")
            
            log.write(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] NAV fetch completed.\n")
            
        except Exception as e:
            log.write(f"ERROR: {str(e)}\n")

if __name__ == "__main__":
    run_nav_fetch()
