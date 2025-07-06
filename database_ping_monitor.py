import os
import platform
import pync
import pygame
import re
import smtplib
import socket
import subprocess
import threading
import time
import signal
import sys
import asyncio
from datetime import datetime
from dotenv import load_dotenv
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import queue

from db_connect import db_manager

# Initial configuration load
load_dotenv(".env")


def resolve_url_to_ip(url):
    """Resolve URL clearly to IP"""
    try:
        return socket.gethostbyname(url)
    except Exception as e:
        print(f"IP resolution failed for {url}: {e}")
        return None


def send_email(subject, body):
    """Explicitly send an SMTP email clearly"""
    try:
        smtp_server = os.getenv('SMTP_SERVER')
        smtp_port = int(os.getenv('SMTP_PORT', 587))
        sender_email = os.getenv('SENDER_EMAIL')
        sender_password = os.getenv('SENDER_PASSWORD')
        receiver_email = os.getenv('RECEIVER_EMAIL')

        if not all([smtp_server, sender_email, sender_password, receiver_email]):
            print("Email configuration incomplete, skipping email alert")
            return

        msg = MIMEMultipart()
        msg.attach(MIMEText(body))
        msg["From"] = sender_email
        msg["To"] = receiver_email
        msg["Subject"] = subject

        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(sender_email, sender_password)
            server.sendmail(sender_email, receiver_email, msg.as_string())
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
        print(f"Explicit ping failure for {host}: {e}")
        return False, None


def log_to_database(url, ip, status, response_time, counter):
    """Log ping result to PostgreSQL database"""
    try:
        import asyncpg
        
        # Create a new event loop for this thread
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        async def insert_data():
            # Create a direct database connection for this insert
            host = os.getenv('DB_HOST', 'localhost')
            port = os.getenv('DB_PORT', '5432')
            database = os.getenv('DB_NAME', 'ping_monitor')
            username = os.getenv('DB_USER', 'admin')
            password = os.getenv('DB_PASSWORD', 'password')
            
            connection_string = f"postgresql://{username}:{password}@{host}:{port}/{database}"
            
            conn = await asyncpg.connect(connection_string)
            try:
                await conn.execute(
                    "INSERT INTO ping_results (timestamp, url, ip, status, response_time_ms, count) VALUES ($1, $2, $3, $4, $5, $6)",
                    datetime.now(), url, ip, status, response_time, counter
                )
            finally:
                await conn.close()
        
        loop.run_until_complete(insert_data())
        loop.close()
        print(f"[{url}] Logged to database: {status} (count: {counter})")
        
    except Exception as e:
        print(f"Error logging to database for {url}: {e}")


def send_desktop_notification(title, message):
    """Send desktop notification explicitly using pync (macOS); adjust as needed for other OS."""
    try:
        notification_timeout = int(os.getenv('NOTIFICATION_TIMEOUT', 10))
        pync.notify(message, title=title, timeout=notification_timeout)
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


class DynamicPingMonitor:
    def __init__(self):
        self.active_threads = {}  # {url: thread}
        self.stop_events = {}  # {url: threading.Event}
        self.current_urls = set()
        self.config_lock = threading.Lock()
        self.running = True

        # Initialize database connection
        self.init_database()

        # Load initial configuration
        self.reload_config()

        # Start configuration monitoring thread
        self.config_thread = threading.Thread(target=self.monitor_config, daemon=True)
        self.config_thread.start()

        # Setup signal handling for graceful shutdown
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)

    def init_database(self):
        """Initialize database connection"""
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            loop.run_until_complete(db_manager.initialize())
            loop.close()
            print("✅ Database connection pool initialized")
            print("✅ Database initialized successfully")
        except Exception as e:
            print(f"❌ Database initialization failed: {e}")
            sys.exit(1)

    def signal_handler(self, signum, frame):
        print("\n📡 Graceful shutdown initiated...")
        self.shutdown()
        sys.exit(0)

    def reload_config(self):
        """Reload configuration from .env file"""
        try:
            # Reload environment variables
            load_dotenv(".env", override=True)

            # Parse target URLs
            target_urls_str = os.getenv('TARGET_URLS', '')
            new_urls = set(url.strip() for url in target_urls_str.split(',') if url.strip())

            with self.config_lock:
                # Find URLs to add and remove
                urls_to_add = new_urls - self.current_urls
                urls_to_remove = self.current_urls - new_urls

                # Stop monitoring for removed URLs
                for url in urls_to_remove:
                    self.stop_monitoring_url(url)

                # Start monitoring for new URLs
                for url in urls_to_add:
                    self.start_monitoring_url(url)

                # Update current URLs
                self.current_urls = new_urls

                if urls_to_add or urls_to_remove:
                    print(f"\n🔄 Configuration updated:")
                    if urls_to_add:
                        print(f"  ✅ Added: {', '.join(urls_to_add)}")
                    if urls_to_remove:
                        print(f"  ❌ Removed: {', '.join(urls_to_remove)}")
                    print(f"  📍 Currently monitoring: {', '.join(self.current_urls)}")

        except Exception as e:
            print(f"Error reloading config: {e}")

    def monitor_config(self):
        """Monitor .env file for changes"""
        last_modified = 0

        while self.running:
            try:
                if os.path.exists('.env'):
                    current_modified = os.path.getmtime('.env')
                    if current_modified > last_modified:
                        last_modified = current_modified
                        if last_modified > 0:  # Skip initial load
                            print("\n📄 .env file changed, reloading configuration...")
                            self.reload_config()

                time.sleep(2)  # Check every 2 seconds
            except Exception as e:
                print(f"Error monitoring config: {e}")
                time.sleep(5)

    def start_monitoring_url(self, url):
        """Start monitoring a specific URL"""
        if url in self.active_threads:
            return  # Already monitoring

        print(f"🟢 Starting monitoring for {url}")
        stop_event = threading.Event()
        thread = threading.Thread(target=self.monitor_url_with_stop, args=(url, stop_event), daemon=True)

        self.stop_events[url] = stop_event
        self.active_threads[url] = thread
        thread.start()

    def stop_monitoring_url(self, url):
        """Stop monitoring a specific URL"""
        if url in self.stop_events:
            print(f"🔴 Stopping monitoring for {url}")
            self.stop_events[url].set()

            # Wait for thread to finish
            if url in self.active_threads:
                self.active_threads[url].join(timeout=5)
                del self.active_threads[url]

            del self.stop_events[url]

    def monitor_url_with_stop(self, url, stop_event):
        """Monitor URL with ability to stop via event"""
        consecutive_failures = 0
        consecutive_latency_alerts = 0
        counter = 1

        while not stop_event.is_set():
            # Reload config values for this iteration
            ping_threshold = float(os.getenv('PING_THRESHOLD', 100))
            alert_threshold = int(os.getenv('ALERT_THRESHOLD', 3))
            ping_interval = int(os.getenv('PING_INTERVAL', 30))

            ip = resolve_url_to_ip(url)
            if not ip:
                print(f"[{url}] IP resolution failed. Retrying...")
                if stop_event.wait(ping_interval):
                    break
                continue

            print(f"\n[{url}] Checking {url} ({ip}) at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}:")
            success, response_time_ms = ping_host(ip)

            # Determine status
            if not success:
                status = "Ping Failure"
                consecutive_failures += 1
                consecutive_latency_alerts = 0

                if consecutive_failures >= alert_threshold:
                    send_desktop_notification(f"{url} - Ping Failure Warning",
                                              f"Could not reach {url} after {consecutive_failures} tries.")
                    send_email(f"{url} - Ping Failure Warning",
                               f"Could not reach {url} after {consecutive_failures} attempts.")
                    play_alert_sound(os.getenv('ALERT_SOUND_FILE', 'alert.mp3'))
                    consecutive_failures = 0
            else:
                consecutive_failures = 0
                if response_time_ms > ping_threshold:
                    status = "High Latency"
                    consecutive_latency_alerts += 1

                    if consecutive_latency_alerts >= alert_threshold:
                        send_desktop_notification(f"{url} - High Latency Warning",
                                                  f"{url} latency {response_time_ms:.2f}ms")
                        send_email(f"{url} - High Latency Warning",
                                   f"Latency reached {response_time_ms:.2f}ms.")
                        play_alert_sound(os.getenv('ALERT_SOUND_FILE', 'alert.mp3'))
                        consecutive_latency_alerts = 0
                else:
                    status = "Success"
                    consecutive_latency_alerts = 0

            # Log to database instead of CSV
            log_to_database(url, ip, status, response_time_ms if success else None, counter)

            print(f"[{url}] Status: {status} (attempt: {counter})")
            if response_time_ms:
                print(f"[{url}] Response time: {response_time_ms:.2f} ms")
            print(f"[{url}] Counters - Latency: {consecutive_latency_alerts}, Failures: {consecutive_failures}")

            counter += 1

            # Wait for interval or stop signal
            if stop_event.wait(ping_interval):
                break

    def run(self):
        """Run the monitoring system"""
        try:
            print(f"🚀 Dynamic Ping Monitor started with PostgreSQL backend")
            print(f"📡 Monitoring configuration file for changes...")
            print(f"📍 Press Ctrl+C to stop\n")

            while self.running:
                time.sleep(1)
        except KeyboardInterrupt:
            self.shutdown()

    def shutdown(self):
        """Shutdown all monitoring threads"""
        print("\n🛑 Shutting down monitoring...")
        self.running = False

        # Stop all URL monitoring
        with self.config_lock:
            for url in list(self.current_urls):
                self.stop_monitoring_url(url)

        # Close database connection
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            loop.run_until_complete(db_manager.close())
            loop.close()
        except Exception as e:
            print(f"Error closing database: {e}")

        print("✅ All monitoring stopped.")


if __name__ == "__main__":
    monitor = DynamicPingMonitor()
    monitor.run()