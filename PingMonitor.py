import csv
import os
import platform
import pync  # if macOS notifications are required
import pygame
import re
import smtplib
import socket
import subprocess
import time

from datetime import datetime
from dotenv import load_dotenv
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

# Explicitly load configurations from sample.env
load_dotenv(".env")

SMTP_SERVER = os.getenv('SMTP_SERVER')
SMTP_PORT = int(os.getenv('SMTP_PORT'))
SENDER_EMAIL = os.getenv('SENDER_EMAIL')
SENDER_PASSWORD = os.getenv('SENDER_PASSWORD')
RECEIVER_EMAIL = os.getenv('RECEIVER_EMAIL')

PING_THRESHOLD = float(os.getenv('PING_THRESHOLD'))  # in milliseconds, explicitly cast to float
ALERT_THRESHOLD = int(os.getenv('ALERT_THRESHOLD'))
PING_INTERVAL = int(os.getenv('PING_INTERVAL'))
NOTIFICATION_TIMEOUT = int(os.getenv('NOTIFICATION_TIMEOUT'))
CSV_FILENAME = os.getenv('CSV_FILENAME')
TARGET_URL = os.getenv('TARGET_URL')
ALERT_SOUND_FILE = os.getenv('ALERT_SOUND_FILE')


def resolve_url_to_ip(url):
    """Resolve URL clearly to IP"""
    try:
        return socket.gethostbyname(url)
    except Exception as e:
        print(f"IP resolution failed clearly: {e}")
        return None


def send_email(subject, body):
    """Explicitly send an SMTP email clearly"""
    try:
        msg = MIMEMultipart()
        msg.attach(MIMEText(body))
        msg["From"] = SENDER_EMAIL
        msg["To"] = RECEIVER_EMAIL
        msg["Subject"] = subject

        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(SENDER_EMAIL, SENDER_PASSWORD)
            server.sendmail(SENDER_EMAIL, RECEIVER_EMAIL, msg.as_string())
        print("Email sent.")
    except Exception as e:
        print(f"Error sending email: {e}")


def ping_host(host):
    """Ping host explicitly, returns (bool success, float response_time_ms)"""
    try:
        cmd = ["ping", "-n", "1", host] if platform.system().lower() == "windows" else ["ping", "-c", "1", host]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=5)
        output = result.stdout + result.stderr

        match = re.search(r'time[=<]\s*(\d+(?:\.\d+)?)\s*(ms|s)?', output, re.I)
        if match:
            time_val = float(match.group(1))
            unit = match.group(2)
            response_time_ms = time_val * 1000 if unit == 's' else time_val
            return True, response_time_ms
        return False, None
    except Exception as e:
        print(f"Explicit ping failure: {e}")
        return False, None


def log_to_csv(url, ip, status, response_time, counter):
    file_exists = os.path.isfile(CSV_FILENAME)
    response_time_str = f"{response_time:.2f}" if response_time else "N/A"

    with open(CSV_FILENAME, "a", newline="") as csvfile:
        writer = csv.writer(csvfile)
        if not file_exists:
            writer.writerow(["Timestamp", "URL", "IP", "Status", "Response Time (ms)", "Count"])

        writer.writerow([datetime.now().strftime("%Y-%m-%d %H:%M:%S"), url, ip, status, response_time_str, counter])
    print(f"Logged: {status} (count: {counter}).")


def send_desktop_notification(title, message):
    """Send desktop notification explicitly using pync (macOS); adjust as needed for other OS."""
    try:
        pync.notify(message, title=title, timeout=NOTIFICATION_TIMEOUT)
        print(f"Desktop notification sent: {title}")
    except Exception as e:
        print(f"Desktop notification error: {e}")


def play_alert_sound(sound_file):
    """Play sound explicitly clearly"""
    try:
        pygame.mixer.init()
        pygame.mixer.music.load(sound_file)
        pygame.mixer.music.play()
        while pygame.mixer.music.get_busy():
            pygame.time.wait(100)
        pygame.mixer.quit()
        print("Sound played.")
    except Exception as e:
        print(f"Sound play issue: {e}")


def monitor_url(url):
    consecutive_failures = 0
    consecutive_latency_alerts = 0

    while True:
        ip = resolve_url_to_ip(url)
        if not ip:
            print("IP resolution failed. Retrying...")
            time.sleep(PING_INTERVAL)
            continue

        print(f"\nChecking {url} ({ip}) at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}:")
        success, response_time_ms = ping_host(ip)

        if success:
            print(f"Success: Response time = {response_time_ms:.2f} ms")

            if response_time_ms > PING_THRESHOLD:
                consecutive_latency_alerts += 1
                print(f"High latency detected! ({consecutive_latency_alerts}/{ALERT_THRESHOLD})")

                if consecutive_latency_alerts >= ALERT_THRESHOLD:
                    log_to_csv(url, ip, "High Latency", response_time_ms, consecutive_latency_alerts)
                    send_desktop_notification("High Latency Warning", f"{url} latency {response_time_ms:.2f}ms")
                    send_email(f"{url} - High Latency Warning", f"Latency reached {response_time_ms:.2f}ms.")
                    play_alert_sound(ALERT_SOUND_FILE)
                    consecutive_latency_alerts = 0
            else:
                consecutive_latency_alerts = 0
        else:
            consecutive_failures += 1
            print(f"Ping failure! ({consecutive_failures}/{ALERT_THRESHOLD})")

            if consecutive_failures >= ALERT_THRESHOLD:
                log_to_csv(url, ip, "Ping Failure", None, consecutive_failures)
                send_desktop_notification("Ping Failure Warning",
                                          f"Could not reach {url} after {consecutive_failures} tries.")
                send_email(f"{url} - Ping Failure Warning",
                           f"Could not reach {url} after {consecutive_failures} attempts.")
                play_alert_sound(ALERT_SOUND_FILE)
                consecutive_failures = 0

        print(f"Status counters: Latency: {consecutive_latency_alerts}, Failures: {consecutive_failures}")
        print(f"Next check in {PING_INTERVAL} seconds...")
        time.sleep(PING_INTERVAL)


if __name__ == "__main__":
    if TARGET_URL:
        monitor_url(TARGET_URL)
    else:
        print("TARGET_URL not found in env configuration. Check sample.env.")
