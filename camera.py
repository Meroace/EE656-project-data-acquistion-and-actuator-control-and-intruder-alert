import cv2
import yagmail
import time
import os

# Email credentials and receiver
SENDER_EMAIL = "your email"
APP_PASSWORD = "asdd asdc asdd asdd"  # use app password for Gmail or real password for others
RECEIVER_EMAIL = "reciever email"

def capture_image(filename="intruder.jpg"):
    cap = cv2.VideoCapture(1)
    if not cap.isOpened():
        print("Error: Could not open webcam")
        return False

    ret, frame = cap.read()
    if ret:
        cv2.imwrite(filename, frame)
        print(f"Image saved as {filename}")
    else:
        print("Failed to capture image")
    cap.release()
    return ret

def send_email(subject, body, attachment_path):
    try:
        yag = yagmail.SMTP(SENDER_EMAIL, APP_PASSWORD)
        yag.send(to=RECEIVER_EMAIL, subject=subject, contents=body, attachments=attachment_path)
        print("Email sent!")
    except Exception as e:
        print("Error sending email:", e)

def intruder_alert():
    image_path = "intruder.jpg"
    if capture_image(image_path):
        subject = "Intruder Alert!"
        body = "Motion detected! See the attached image."
        send_email(subject, body, image_path)
        # Optionally delete image after sending
        os.remove(image_path)

if __name__ == "__main__":
    print("Starting Intruder Alert System...")
    while True:
        # For demo, simulate motion detection by user input
        input("Press Enter to simulate motion detection...")
        intruder_alert()
        print("Waiting for next detection...")
        time.sleep(5)  # prevent spam, wait 5 seconds before next

