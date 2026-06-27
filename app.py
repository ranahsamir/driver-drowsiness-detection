import os, cv2, config, threading, time
from flask import Flask, render_template, Response, jsonify, request
from detector import Detector

# Force TCP and set a shorter timeout to prevent the 30-second hang
os.environ["OPENCV_FFMPEG_CAPTURE_OPTIONS"] = "rtsp_transport;tcp|timeout;5000000"

app = Flask(__name__, static_folder='static')

detector = Detector()
# Added cv2.CAP_FFMPEG for better compatibility with network streams
cap = cv2.VideoCapture(config.ESP32_STREAM_URL, cv2.CAP_FFMPEG)

if not os.path.exists('static/alerts'):
    os.makedirs('static/alerts')

state_global = '0'
latest_frame = None

def background_detection():
    global state_global, latest_frame
    print("AI Background Thread Started...")  # make sure thread has started

    while True:
        ret, frame = cap.read()
        if not ret:
            #Print in terminal if camera is not working
            print("❌ Camera Signal Lost. Reconnecting...")
            cap.open(config.ESP32_STREAM_URL, cv2.CAP_FFMPEG)
            time.sleep(2)
            continue

        # Saving frames for webp
        latest_frame = frame.copy()

        # Letting the detection work / start
        try:
            state, ear = detector.analyze(frame)
            state_global = state
            # print(f"EAR: {ear} | State: {state}") # values of ear shown in terminal while running the app.py
        except Exception as e:
            print(f"AI Analysis Error: {e}")

# Immediate Detection
threading.Thread(target=background_detection, daemon=True).start()

def generate_frames():
    global latest_frame
    while True:
        if latest_frame is not None:
            #Showing the frames of the detection and camera immediate
            frame_resized = cv2.resize(latest_frame, (480, 360))
            #_, buffer = cv2.imencode('.jpg', frame_resized)
            _, buffer = cv2.imencode('.jpg', frame_resized,
            [int(cv2.IMWRITE_JPEG_QUALITY), 70])  # reduce resolution so the increase the perfomamce
            yield (b'--frame\r\nContent-Type: image/jpeg\r\n\r\n' + buffer.tobytes() + b'\r\n')
            time.sleep(0.04)  # give chance for the processor
        else:
            time.sleep(0.1)

@app.route('/')
def home():
    return render_template('index.html', active_page='home')

@app.route('/video')
def video():
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/status')
def status():
    return jsonify({"state": state_global})

@app.route('/history')
def history():
    images = os.listdir('static/alerts')
    images.sort(reverse=True)
    return render_template('history.html', active_page='history', images=images)

@app.route('/settings', methods=['GET', 'POST'])
def settings():
    if request.method == 'POST':
        config.EAR_THRESHOLD = float(request.form.get('threshold'))
    return render_template('settings.html', active_page='settings', threshold=config.EAR_THRESHOLD)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=False, threaded=True, use_reloader=False)