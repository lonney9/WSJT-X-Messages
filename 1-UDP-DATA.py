import socket
import struct
import binascii

# === Outputs WSJT-X UDP messages payloads to console (macOS specific) === #
# Written via ChatGPT prompts 21-Apr-2025 #
# Sim output as "sudo tcpdump -i lo0 udp port 2237 -X" #
# Next version display the message text from the payloads #

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

    print(f"Listening for UDP multicast on {MCAST_GRP}:{MCAST_PORT}...")

    try:
        while True:
            data, addr = sock.recvfrom(2048)
            print(f"\nFrom {addr}:")
            hex_output = binascii.hexlify(data).decode('utf-8')
            for i in range(0, len(hex_output), 32):
                hex_part = hex_output[i:i+32]
                bytes_chunk = bytes.fromhex(hex_part)
                ascii_part = ''.join(chr(b) if 32 <= b <= 126 else '.' for b in bytes_chunk)
                print(f"{i//2:04x}  {' '.join(hex_part[j:j+2] for j in range(0, len(hex_part), 2)):48}  {ascii_part}")
    except KeyboardInterrupt:
        print("\nExiting.")
    finally:
        sock.close()

if __name__ == "__main__":
    main()
