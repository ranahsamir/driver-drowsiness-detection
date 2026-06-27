import requests

BOT_TOKEN = "8283674712:AAHSHouPYyp8EeMbKIVdGRQV0j4IHEED8T4"
CHAT_ID = "996997047"

def send_telegram_photo(image_path, caption="صورة السواق"):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendPhoto"
    #url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendPhoto"
    files = {'photo': open(image_path, 'rb')}
    data = {'chat_id': CHAT_ID, 'caption': caption}
    try:
        r = requests.post(url, files=files, data=data)
        print("تم إرسال الصورة:", r.json())
    except Exception as e:
        print("فشل إرسال الصورة:", e)
