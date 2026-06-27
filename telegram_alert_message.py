import requests
from datetime import datetime

TOKEN = "00000000000000"
CHAT_ID = "0000000"

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
