import requests

TOKEN = "00000000000000"
CHAT_ID = "0000000"

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
