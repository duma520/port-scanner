import socket
import threading
import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import requests

# 常见的端口及其作用（中文说明）
common_ports = {
    21: "FTP（文件传输协议）",
    22: "SSH（安全外壳协议）",
    23: "Telnet（远程登录协议）",
    25: "SMTP（简单邮件传输协议）",
    53: "DNS（域名系统）",
    80: "HTTP（超文本传输协议）",
    110: "POP3（邮局协议版本3）",
    143: "IMAP（互联网消息访问协议）",
    443: "HTTPS（安全的超文本传输协议）",
    3306: "MySQL 数据库",
    3389: "RDP（远程桌面协议）",
    8080: "HTTP-Alt（备用HTTP端口）"
}

def get_service_name(port):
    """尝试从系统数据库获取端口的服务名称"""
    try:
        return socket.getservbyport(port)
    except (OSError, socket.error):
        return None

def get_iana_service_name(port):
    """从 IANA 端口注册表查询端口信息"""
    url = f"https://www.iana.org/assignments/service-names-port-numbers/service-names-port-numbers.xhtml?search={port}"
    try:
        response = requests.get(url)
        if response.status_code == 200:
            # 解析 HTML 页面（这里简单判断是否包含端口信息）
            if f"Port {port}" in response.text:
                return f"详细信息请访问: {url}"
        return None
    except requests.RequestException:
        return None

def scan_port(host, port):
    """扫描单个端口"""
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(0.5)
    result = sock.connect_ex((host, port))
    if result == 0:
        # 获取端口服务名称
        service = common_ports.get(port)
        if not service:
            service = get_service_name(port)
            if not service:
                iana_info = get_iana_service_name(port)
                if iana_info:
                    service = iana_info
                else:
                    service = "未知"
        return port, service
    sock.close()
    return None

def scan_ports(host, start_port, end_port, max_threads, progress_callback, result_callback):
    """多线程扫描端口"""
    open_ports = []
    total_ports = end_port - start_port + 1
    scanned_ports = 0

    def worker(port):
        nonlocal scanned_ports
        result = scan_port(host, port)
        scanned_ports += 1
        progress = (scanned_ports / total_ports) * 100
        progress_callback(progress, port)
        if result:
            open_ports.append(result)
            result_callback(result)

    threads = []
    for port in range(start_port, end_port + 1):
        while threading.active_count() > max_threads:
            pass
        thread = threading.Thread(target=worker, args=(port,))
        thread.start()
        threads.append(thread)

    for thread in threads:
        thread.join()

    return open_ports

class PortScannerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("端口扫描工具")
        self.root.geometry("600x400")

        # 输入框
        self.host_label = tk.Label(root, text="主机地址:")
        self.host_label.grid(row=0, column=0, padx=10, pady=10)
        self.host_entry = tk.Entry(root, width=30)
        self.host_entry.grid(row=0, column=1, padx=10, pady=10)

        self.port_range_label = tk.Label(root, text="端口范围:")
        self.port_range_label.grid(row=1, column=0, padx=10, pady=10)
        self.start_port_entry = tk.Entry(root, width=10)
        self.start_port_entry.grid(row=1, column=1, padx=10, pady=10)
        self.end_port_entry = tk.Entry(root, width=10)
        self.end_port_entry.grid(row=1, column=2, padx=10, pady=10)

        self.threads_label = tk.Label(root, text="线程数:")
        self.threads_label.grid(row=2, column=0, padx=10, pady=10)
        self.threads_entry = tk.Entry(root, width=10)
        self.threads_entry.grid(row=2, column=1, padx=10, pady=10)

        # 扫描按钮
        self.scan_button = tk.Button(root, text="开始扫描", command=self.start_scan)
        self.scan_button.grid(row=3, column=0, columnspan=3, pady=10)

        # 进度条
        self.progress = ttk.Progressbar(root, orient="horizontal", length=400, mode="determinate")
        self.progress.grid(row=4, column=0, columnspan=3, pady=10)

        # 结果显示区域
        self.result_text = scrolledtext.ScrolledText(root, width=70, height=15)
        self.result_text.grid(row=5, column=0, columnspan=3, padx=10, pady=10)

    def start_scan(self):
        """开始扫描"""
        host = self.host_entry.get()
        start_port = int(self.start_port_entry.get())
        end_port = int(self.end_port_entry.get())
        max_threads = int(self.threads_entry.get())

        if not host or start_port > end_port:
            messagebox.showerror("错误", "请输入有效的主机地址和端口范围！")
            return

        # 清空结果区域
        self.result_text.delete(1.0, tk.END)

        # 重置进度条
        self.progress["value"] = 0

        # 启动扫描线程
        scan_thread = threading.Thread(
            target=self.run_scan,
            args=(host, start_port, end_port, max_threads)
        )
        scan_thread.start()

    def run_scan(self, host, start_port, end_port, max_threads):
        """运行扫描"""
        def update_progress(progress, port):
            self.progress["value"] = progress
            self.root.update_idletasks()

        def update_result(result):
            port, service = result
            self.result_text.insert(tk.END, f"端口 {port} 已打开 - {service}\n")
            self.result_text.see(tk.END)

        open_ports = scan_ports(host, start_port, end_port, max_threads, update_progress, update_result)

        # 扫描完成
        self.result_text.insert(tk.END, "\n扫描完成。\n")
        self.result_text.see(tk.END)

if __name__ == "__main__":
    root = tk.Tk()
    app = PortScannerApp(root)
    root.mainloop()
