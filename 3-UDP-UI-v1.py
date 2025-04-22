import socket
import struct
import re
import threading
from datetime import datetime
import tkinter as tk
from tkinter import scrolledtext

# === Opens a basic GUI messsages window and filters for the DXCALL === #
# Written via ChatGPT prompts 21-Apr-2025 #

MCAST_GRP = '224.0.0.1'
MCAST_PORT = 2237

def extract_message(printable):
    # Extract everything after ~ + 4 chars
    match = re.search(r'~.{4}(.*)', printable)
    return match.group(1).strip() if match else None

class WSJTXListener(threading.Thread):
    def __init__(self, dxcall_var, display_callback):
        super().__init__(daemon=True)
        self.dxcall_var = dxcall_var
        self.display_callback = display_callback
        self.running = True

    def run(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        try:
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
        except AttributeError:
            pass

        sock.bind(('', MCAST_PORT))
        mreq = struct.pack("=4sl", socket.inet_aton(MCAST_GRP), socket.INADDR_ANY)
        sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)

        while self.running:
            try:
                data, _ = sock.recvfrom(2048)
                printable = ''.join(chr(b) if 32 <= b <= 126 else '.' for b in data)
                dxcall = self.dxcall_var.get().strip().upper()

                if dxcall and dxcall in printable:
                    message = extract_message(printable)
                    if message:
                        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                        self.display_callback(f"[{timestamp}] {message}")
            except Exception as e:
                self.display_callback(f"Error: {e}")
                break

        sock.close()

    def stop(self):
        self.running = False

def main():
    root = tk.Tk()
    root.title("WSJT-X Message Viewer")

    tk.Label(root, text="DXCALL:").pack(anchor='w', padx=5, pady=(5, 0))
    dxcall_var = tk.StringVar()
    dxcall_entry = tk.Entry(root, textvariable=dxcall_var)
    dxcall_entry.pack(fill='x', padx=5)

    output_box = scrolledtext.ScrolledText(root, wrap=tk.WORD, height=20)
    output_box.pack(fill='both', expand=True, padx=5, pady=5)

    def display_message(msg):
        output_box.insert(tk.END, msg + "\n")
        output_box.see(tk.END)

    listener = WSJTXListener(dxcall_var, display_message)
    listener.start()

    def on_close():
        listener.stop()
        root.destroy()

    root.protocol("WM_DELETE_WINDOW", on_close)
    root.mainloop()

if __name__ == "__main__":
    main()
