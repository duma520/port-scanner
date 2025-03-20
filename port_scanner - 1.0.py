import socket
import sys
import argparse

# 常见的端口及其作用
common_ports = {
    21: "FTP",
    22: "SSH",
    23: "Telnet",
    25: "SMTP",
    53: "DNS",
    80: "HTTP",
    110: "POP3",
    143: "IMAP",
    443: "HTTPS",
    3306: "MySQL",
    3389: "RDP",
    8080: "HTTP-Alt"
}

def scan_ports(host, start_port=1, end_port=1024):
    open_ports = []
    for port in range(start_port, end_port + 1):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(0.5)
        result = sock.connect_ex((host, port))
        if result == 0:
            service = common_ports.get(port, "Unknown")
            open_ports.append((port, service))
            print(f"Port {port} is open - {service}")
        sock.close()
    return open_ports

def save_to_file(open_ports, filename="port_scan_results.txt"):
    with open(filename, "a") as file:
        for port, service in open_ports:
            file.write(f"Port {port} is open - {service}\n")

if __name__ == "__main__":
    # 使用 argparse 解析命令行参数
    parser = argparse.ArgumentParser(description="Scan ports of a given host.")
    parser.add_argument("host", help="The host to scan (e.g., www.163.com)")
    parser.add_argument("-s", "--start-port", type=int, default=1, help="Start port (default: 1)")
    parser.add_argument("-e", "--end-port", type=int, default=1024, help="End port (default: 1024)")
    args = parser.parse_args()

    host = args.host
    start_port = args.start_port
    end_port = args.end_port

    print(f"Scanning {host} from port {start_port} to {end_port}...")
    open_ports = scan_ports(host, start_port, end_port)
    save_to_file(open_ports)
    print("Scan completed. Results saved to port_scan_results.txt")
