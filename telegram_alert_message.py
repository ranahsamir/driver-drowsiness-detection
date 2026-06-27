import requests
from datetime import datetime

TOKEN = "8283674712:AAHSHouPYyp8EeMbKIVdGRQV0j4IHEED8T4"
CHAT_ID = "996997047"

def send_drowsiness_alert():

    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    message = f"""
⚠️ DRIVER DROWSINESS ALERT

Status: Driver appears to be sleeping
Time: {current_time}

Please check the driver immediately.
"""

    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"

    data = {
        "chat_id": CHAT_ID,
        "text": message
    }

    requests.post(url, data=data)
