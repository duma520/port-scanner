import socket
import sys
import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed
import time

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

def scan_port(host, port):
    """扫描单个端口"""
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(0.5)
    result = sock.connect_ex((host, port))
    if result == 0:
        service = common_ports.get(port, "Unknown")
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
    print("Results saved to port_scan_results.txt")
