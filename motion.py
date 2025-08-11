from flask import Flask, render_template_string, Response, jsonify
import cv2
import threading
import smtplib
import ssl
from email.message import EmailMessage
import time
import numpy as np

app = Flask(__name__)

# Webcam capture
camera = cv2.VideoCapture(1)

# Motion detection state
motion_detected = False
last_motion_time = 0
motion_lock = threading.Lock()

# Email config — update with your info
EMAIL_ADDRESS = "greenrobotics0710@gmail.com"
EMAIL_PASSWORD = "jhdu cpqs ormu ynxi"
EMAIL_RECEIVER = "anojreji710@gmail.com"

# HTML template embedded in the Python file
HTML_PAGE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <title>Intruder Alert Dashboard</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; }
        #status { font-weight: bold; color: red; }
        #alert-img { max-width: 640px; margin-top: 10px; display: none; }
    </style>
    <script>
        async function checkMotion() {
            const res = await fetch('/motion_status');
            const data = await res.json();
            const statusEl = document.getElementById('status');
            const alertImg = document.getElementById('alert-img');
            if(data.motion) {
                statusEl.textContent = "Motion Detected! 🚨";
                alertImg.style.display = "block";
                alertImg.src = "/static/alert.jpg?" + new Date().getTime();
            } else {
                statusEl.textContent = "No Motion";
                alertImg.style.display = "none";
            }
        }
        setInterval(checkMotion, 3000);
        window.onload = checkMotion;
    </script>
</head>
<body>
    <h1>Intruder Alert System</h1>
    <div>
        <img src="{{ url_for('video_feed') }}" width="640" height="480" />
    </div>
    <div>
        <p>Status: <span id="status">Checking...</span></p>
        <img id="alert-img" alt="Alert Snapshot"/>
    </div>
</body>
</html>
"""

def send_email_alert(image_path):
    msg = EmailMessage()
    msg['Subject'] = 'Intruder Alert!'
    msg['From'] = EMAIL_ADDRESS
    msg['To'] = EMAIL_RECEIVER
    msg.set_content('Motion detected! See attached image.')

    with open(image_path, 'rb') as img:
        img_data = img.read()
    msg.add_attachment(img_data, maintype='image', subtype='jpeg', filename='alert.jpg')

    context = ssl.create_default_context()
    with smtplib.SMTP_SSL('smtp.gmail.com', 465, context=context) as smtp:
        smtp.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
        smtp.send_message(msg)

def motion_detection(frame, avg_frame, threshold=25, min_area=5000):
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    gray = cv2.GaussianBlur(gray, (21, 21), 0)

    if avg_frame is None:
        return gray, False

    frame_delta = cv2.absdiff(avg_frame.astype("uint8"), gray)
    thresh = cv2.threshold(frame_delta, threshold, 255, cv2.THRESH_BINARY)[1]
    thresh = cv2.dilate(thresh, None, iterations=2)
    contours, _ = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    for c in contours:
        if cv2.contourArea(c) > min_area:
            return gray, True
    return gray, False

def gen_frames():
    global motion_detected, last_motion_time
    avg_frame = None
    while True:
        success, frame = camera.read()
        if not success:
            break
        else:
            avg_frame, detected = motion_detection(frame, avg_frame)
            with motion_lock:
                if detected:
                    motion_detected = True
                    last_motion_time = time.time()
                    cv2.imwrite('static/alert.jpg', frame)
                    threading.Thread(target=send_email_alert, args=('static/alert.jpg',), daemon=True).start()

            ret, buffer = cv2.imencode('.jpg', frame)
            frame_bytes = buffer.tobytes()
            yield (b'--frame\r\nContent-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')

@app.route('/')
def index():
    return render_template_string(HTML_PAGE)

@app.route('/video_feed')
def video_feed():
    return Response(gen_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/motion_status')
def motion_status():
    with motion_lock:
        if time.time() - last_motion_time > 10:
            status = False
        else:
            status = motion_detected
    return jsonify({'motion': status})

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)

