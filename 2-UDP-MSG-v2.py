import socket
import struct
import time

# === Outputs WSJT-X UDP messages payloads as readable text (macOS specific) === #
# Written via ChatGPT prompts 21-Apr-2025 #
# This converts the bytes_chunk in the UDP message to the text of the message #
# Filters and displays printable message text, one line per UDP message #
# adds a timestamp, and is one message per line #

MCAST_GRP = '224.0.0.1'
MCAST_PORT = 2237

def main():
    # Create UDP socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
    
    # Allow reuse of address and port
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    try:
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)  # macOS specific
    except AttributeError:
        print("SO_REUSEPORT not supported on this platform")

    # Bind to the multicast port on all interfaces
    sock.bind(('', MCAST_PORT))

    # Join the multicast group
    mreq = struct.pack("=4sl", socket.inet_aton(MCAST_GRP), socket.INADDR_ANY)
    sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)

    print(f"Listening for WSJT-X UDP multicast on {MCAST_GRP}:{MCAST_PORT}...")

    try:
        while True:
            data, addr = sock.recvfrom(2048)
            # Decode and clean printable characters from payload
            printable = ''.join(chr(b) if 32 <= b <= 126 else '.' for b in data)
            # Get current timestamp
            timestamp = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
            # Print the timestamp followed by the printable payload
            print(f"[{timestamp}] {printable}")
    except KeyboardInterrupt:
        print("\nExiting.")
    finally:
        sock.close()

if __name__ == "__main__":
    main()
