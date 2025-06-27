#!/usr/bin/env python3
"""
Simple HTTP server to serve CSV data for the Flutter frontend.
This allows the Flutter app to fetch ping data via HTTP requests.
"""

import json
import csv
import os
from datetime import datetime
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
import threading
import time

CSV_FILENAME = 'ping_results.csv'

class CSVHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        parsed_path = urlparse(self.path)
        
        if parsed_path.path == '/ping-data':
            self.serve_ping_data(parsed_path.query)
        elif parsed_path.path == '/url-statuses':
            self.serve_url_statuses()
        elif parsed_path.path == '/health':
            self.serve_health()
        elif parsed_path.path == '/env-config':
            self.serve_env_config()
        else:
            self.send_error(404, "Endpoint not found")
    
    def do_POST(self):
        parsed_path = urlparse(self.path)
        
        if parsed_path.path == '/env-config':
            self.update_env_config()
        else:
            self.send_error(404, "POST endpoint not found")
    
    def do_OPTIONS(self):
        # Handle CORS preflight requests
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

    def serve_ping_data(self, query_string):
        """Serve all ping data as JSON"""
        try:
            ping_data = self.read_csv_data()
            
            # Parse query parameters for filtering
            params = parse_qs(query_string)
            url_filter = params.get('url', [None])[0]
            limit = int(params.get('limit', [1000])[0])
            
            # Filter by URL if specified
            if url_filter:
                ping_data = [row for row in ping_data if row.get('url') == url_filter]
            
            # Limit results
            ping_data = ping_data[-limit:] if limit > 0 else ping_data
            
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
            self.send_header('Access-Control-Allow-Headers', 'Content-Type')
            self.end_headers()
            self.wfile.write(json.dumps(ping_data).encode())
            
        except Exception as e:
            self.send_error(500, f"Error reading CSV data: {str(e)}")

    def serve_url_statuses(self):
        """Serve aggregated URL status data"""
        try:
            ping_data = self.read_csv_data()
            url_statuses = self.aggregate_url_statuses(ping_data)
            
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
            self.send_header('Access-Control-Allow-Headers', 'Content-Type')
            self.end_headers()
            self.wfile.write(json.dumps(url_statuses).encode())
            
        except Exception as e:
            self.send_error(500, f"Error processing URL statuses: {str(e)}")

    def serve_health(self):
        """Health check endpoint"""
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
        health_data = {
            'status': 'healthy',
            'timestamp': datetime.now().isoformat(),
            'csv_exists': os.path.exists(CSV_FILENAME)
        }
        self.wfile.write(json.dumps(health_data).encode())

    def serve_env_config(self):
        """Serve current .env configuration"""
        try:
            env_config = self.read_env_config()
            
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
            self.send_header('Access-Control-Allow-Headers', 'Content-Type')
            self.end_headers()
            self.wfile.write(json.dumps(env_config).encode())
            
        except Exception as e:
            self.send_error(500, f"Error reading .env config: {str(e)}")

    def update_env_config(self):
        """Update .env configuration from POST data"""
        try:
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            config_data = json.loads(post_data.decode('utf-8'))
            
            self.write_env_config(config_data)
            
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
            self.send_header('Access-Control-Allow-Headers', 'Content-Type')
            self.end_headers()
            
            response = {'status': 'success', 'message': 'Configuration updated successfully'}
            self.wfile.write(json.dumps(response).encode())
            
        except Exception as e:
            self.send_error(500, f"Error updating .env config: {str(e)}")

    def read_env_config(self):
        """Read current .env configuration"""
        env_file = '.env'
        config = {}
        
        if os.path.exists(env_file):
            with open(env_file, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#') and '=' in line:
                        key, value = line.split('=', 1)
                        config[key.strip()] = value.strip()
        
        # Provide defaults if not found
        defaults = {
            'SMTP_SERVER': 'smtp.gmail.com',
            'SMTP_PORT': '587',
            'SENDER_EMAIL': '',
            'SENDER_PASSWORD': '',
            'RECEIVER_EMAIL': '',
            'PING_THRESHOLD': '100',
            'ALERT_THRESHOLD': '3',
            'PING_INTERVAL': '10',
            'NOTIFICATION_TIMEOUT': '10',
            'CSV_FILENAME': 'ping_results.csv',
            'TARGET_URLS': 'g.co,github.com,microsoft.com',
            'ALERT_SOUND_FILE': 'alert.mp3'
        }
        
        for key, default_value in defaults.items():
            if key not in config:
                config[key] = default_value
        
        return config

    def write_env_config(self, config):
        """Write configuration to .env file"""
        env_file = '.env'
        
        with open(env_file, 'w') as f:
            f.write("# SMTP Configuration\n")
            f.write(f"SMTP_SERVER={config.get('SMTP_SERVER', 'smtp.gmail.com')}\n")
            f.write(f"SMTP_PORT={config.get('SMTP_PORT', '587')}\n")
            f.write(f"SENDER_EMAIL={config.get('SENDER_EMAIL', '')}\n")
            f.write(f"SENDER_PASSWORD={config.get('SENDER_PASSWORD', '')}\n")
            f.write(f"RECEIVER_EMAIL={config.get('RECEIVER_EMAIL', '')}\n")
            f.write("\n# Ping Configuration\n")
            f.write(f"PING_THRESHOLD={config.get('PING_THRESHOLD', '100')}\n")
            f.write(f"ALERT_THRESHOLD={config.get('ALERT_THRESHOLD', '3')}\n")
            f.write(f"PING_INTERVAL={config.get('PING_INTERVAL', '10')}\n")
            f.write(f"NOTIFICATION_TIMEOUT={config.get('NOTIFICATION_TIMEOUT', '10')}\n")
            f.write("\n# Output File\n")
            f.write(f"CSV_FILENAME={config.get('CSV_FILENAME', 'ping_results.csv')}\n")
            f.write("\n# Target URLS\n")
            f.write(f"TARGET_URLS={config.get('TARGET_URLS', 'g.co,github.com,microsoft.com')}\n")
            f.write("\n# Alert Sound\n")
            f.write(f"ALERT_SOUND_FILE={config.get('ALERT_SOUND_FILE', 'alert.mp3')}\n")

    def read_csv_data(self):
        """Read and parse CSV data"""
        if not os.path.exists(CSV_FILENAME):
            return []
        
        ping_data = []
        with open(CSV_FILENAME, 'r', newline='') as csvfile:
            lines = csvfile.readlines()
            
            for i, line in enumerate(lines[1:], 1):  # Skip header
                line = line.strip()
                if not line:
                    continue
                    
                try:
                    values = line.split(',')
                    
                    if len(values) >= 6:
                        # Standard format: Timestamp,URL,IP,Status,Response Time (ms),Count
                        timestamp = values[0]
                        url = values[1]
                        ip = values[2]
                        status = values[3]
                        response_time = values[4] if values[4] != 'N/A' else None
                        count = int(values[5]) if values[5].isdigit() else 0
                    elif len(values) >= 4:
                        # Handle inconsistent format - use last known URL
                        timestamp = values[0]
                        url = getattr(self, '_last_url', 'unknown')
                        ip = getattr(self, '_last_ip', 'unknown')
                        status = values[1] if len(values) >= 4 else 'Unknown'
                        response_time = values[2] if len(values) >= 3 and values[2] != 'N/A' else None
                        count = int(values[3]) if len(values) >= 4 and values[3].isdigit() else 0
                    else:
                        continue
                    
                    # Store last known URL/IP
                    if url != 'unknown':
                        self._last_url = url
                    if ip != 'unknown':
                        self._last_ip = ip
                    
                    ping_record = {
                        'timestamp': timestamp,
                        'url': url,
                        'ip': ip,
                        'status': status,
                        'response_time': float(response_time) if response_time and response_time != 'N/A' else None,
                        'count': count
                    }
                    ping_data.append(ping_record)
                    
                except Exception as e:
                    print(f"Error parsing line {i}: {line} - {e}")
                    continue
        
        return ping_data

    def aggregate_url_statuses(self, ping_data):
        """Aggregate ping data by URL for status overview"""
        url_groups = {}
        
        for ping in ping_data:
            url = ping['url']
            if url not in url_groups:
                url_groups[url] = []
            url_groups[url].append(ping)
        
        url_statuses = []
        for url, pings in url_groups.items():
            # Sort by timestamp (most recent first)
            pings.sort(key=lambda x: x['timestamp'], reverse=True)
            
            latest_ping = pings[0] if pings else None
            recent_pings = pings[:50]  # Last 50 pings
            
            # Calculate statistics
            successful_pings = [p for p in recent_pings if p['status'] == 'Success']
            uptime = (len(successful_pings) / len(recent_pings)) * 100 if recent_pings else 0
            
            avg_latency = None
            if successful_pings:
                latencies = [p['response_time'] for p in successful_pings if p['response_time'] is not None]
                if latencies:
                    avg_latency = sum(latencies) / len(latencies)
            
            # Count consecutive failures
            consecutive_failures = 0
            for ping in pings:
                if ping['status'] == 'Ping Failure':
                    consecutive_failures += 1
                else:
                    break
            
            url_status = {
                'url': url,
                'ip': latest_ping['ip'] if latest_ping else None,
                'latest_ping': latest_ping,
                'uptime_percentage': uptime,
                'average_response_time': avg_latency,
                'consecutive_failures': consecutive_failures,
                'total_pings': len(pings),
                'recent_pings': recent_pings
            }
            url_statuses.append(url_status)
        
        return url_statuses

def run_server(port=8000):
    """Run the HTTP server"""
    server_address = ('', port)
    httpd = HTTPServer(server_address, CSVHandler)
    print(f"Starting CSV server on port {port}...")
    print(f"Endpoints available:")
    print(f"  http://localhost:{port}/ping-data - All ping data")
    print(f"  http://localhost:{port}/url-statuses - Aggregated URL statuses")
    print(f"  http://localhost:{port}/health - Health check")
    httpd.serve_forever()

if __name__ == '__main__':
    import sys
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8000
    run_server(port)
