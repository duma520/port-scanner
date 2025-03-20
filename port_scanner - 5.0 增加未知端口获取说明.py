import socket
import sys
import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed

# 常见的端口及其作用
common_ports = {
    21: "FTP (File Transfer Protocol)",
    22: "SSH (Secure Shell)",
    23: "Telnet (Remote Login Protocol)",
    25: "SMTP (Simple Mail Transfer Protocol)",
    53: "DNS (Domain Name System)",
    80: "HTTP (Hypertext Transfer Protocol)",
    110: "POP3 (Post Office Protocol version 3)",
    143: "IMAP (Internet Message Access Protocol)",
    443: "HTTPS (HTTP Secure)",
    3306: "MySQL Database",
    3389: "RDP (Remote Desktop Protocol)",
    8080: "HTTP-Alt (Alternative HTTP Port)"
}

def get_service_name(port):
    """尝试获取端口的服务名称"""
    try:
        return socket.getservbyport(port)
    except (OSError, socket.error):
        return "Unknown"

def scan_port(host, port):
    """扫描单个端口"""
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(0.5)
    result = sock.connect_ex((host, port))
    if result == 0:
        service = common_ports.get(port, get_service_name(port))
        return port, service
    sock.close()
    return None

def scan_ports(host, start_port=1, end_port=1024, max_threads=100):
    """多线程扫描端口"""
    open_ports = []
    total_ports = end_port - start_port + 1
    scanned_ports = 0

    with ThreadPoolExecutor(max_workers=max_threads) as executor:
        futures = {
            executor.submit(scan_port, host, port): port
            for port in range(start_port, end_port + 1)
        }
        for future in as_completed(futures):
            scanned_ports += 1
            port = futures[future]
            progress = (scanned_ports / total_ports) * 100
            print(f"\rScanning port {port}... Progress: {progress:.2f}%", end="")
            result = future.result()
            if result:
                port, service = result
                open_ports.append((port, service))
                print(f"\nPort {port} is open - {service}")
    print("\nScan completed.")
    return open_ports

def save_to_file(open_ports, filename="port_scan_results.txt"):
    """保存扫描结果到文件"""
    with open(filename, "a") as file:
        for port, service in open_ports:
            file.write(f"Port {port} is open - {service}\n")

def display_results(open_ports):
    """显示扫描结果并解释端口作用"""
    if not open_ports:
        print("No open ports found.")
        return

    print("\nScan Results:")
    print("-" * 50)
    for port, service in open_ports:
        if service == "Unknown":
            print(f"Port {port}: Unknown (This port may be used by a custom or uncommon service. Further investigation is recommended.)")
        else:
            print(f"Port {port}: {service}")
    print("-" * 50)

if __name__ == "__main__":
    # 使用 argparse 解析命令行参数
    parser = argparse.ArgumentParser(description="Scan ports of a given host.")
    parser.add_argument("host", help="The host to scan (e.g., www.163.com)")
    parser.add_argument("-s", "--start-port", type=int, default=1, help="Start port (default: 1)")
    parser.add_argument("-e", "--end-port", type=int, default=1024, help="End port (default: 1024)")
    parser.add_argument("-t", "--threads", type=int, default=100, help="Max threads (default: 100)")
    args = parser.parse_args()

    host = args.host
    start_port = args.start_port
    end_port = args.end_port
    max_threads = args.threads

    print(f"Scanning {host} from port {start_port} to {end_port} with {max_threads} threads...")
    open_ports = scan_ports(host, start_port, end_port, max_threads)
    save_to_file(open_ports)
    display_results(open_ports)
    print("Results saved to port_scan_results.txt")
