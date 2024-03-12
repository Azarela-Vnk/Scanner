import requests
from urllib.parse import urlparse
import os
import socket
from bs4 import BeautifulSoup
from termcolor import colored
import time
import concurrent.futures
from typing import List
from geopy.geocoders import Nominatim
import geocoder

# Fungsi untuk memeriksa keberadaan payload XSS pada halaman web
def scan_xss(url, payloads):
    for payload in payloads:
        try:
            response = requests.get(url, params={'q': payload}, headers=headers)
            soup = BeautifulSoup(response.text, 'html.parser')

            if payload in soup.text:
                print(f"Terdapat vuln XSS pada URL: {url} dengan payload: {payload}")

        except Exception as e:
            print("Error:", e)

# Penambahan payloads XSS
payloads = [
    "><script>alert('XSS')</script>",
    "<script>alert(document.cookie)</script>",
    "<img src=x onerror=alert('XSS')>",
    "';alert('XSS');//", 
    "<A%0aONMouseOvER%0d=%0d[8].find(confirm)>z",
    "</tiTlE/><a%0donpOintErentER%0d=%0d(prompt)``>z",
    "</SCRiPT/><DETAILs/+/onpoINTERenTEr%0a=%0aa=prompt,a()//", 
]

# ... (sisa kode)

# Definisikan headers untuk permintaan
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
}

def banner_grabbing():
    target_url = input("\nMasukkan URL target: ")
    if not target_url.startswith('http://') and not target_url.startswith('https://'):
        target_url = 'http://' + target_url
    try:
        response = requests.get(target_url)
        print("Sedang mengambil banner", target_url)
        print("\nBanner berhasil di ambil")
        print("\n=======================================\n", response.headers)
    except Exception as e:
        print("Error:", e)

def ip_grabbing():
    target_url = input("Masukkan URL target: ")

    try:
        # Resolve the IP address
        ip_address = socket.gethostbyname(target_url)
        print(f"IP Address: {ip_address}")

        try:
            # Resolve the hostname
            host_name = socket.gethostbyaddr(ip_address)[0]
            print(f"Nama Website: {host_name}")
        except socket.herror as he:
            print(f"Tidak dapat menemukan nama host: {he}")

        # Find location by IP address
        geolocator = Nominatim(user_agent="myGeocoder")
        g = geocoder.ip('{}'.format(ip_address))

        if g.latlng:
            location = geolocator.reverse([g.latlng[0], g.latlng[1]])

            if location is not None:
                print(f"Lokasi: {location.address}")
            else:
                print(f"Tidak dapat menemukan lokasi IP address: {ip_address}")

        else:
            print(f"Tidak dapat menemukan lokasi IP address: {ip_address}")

    except socket.gaierror as ge:
        print(f"Error: {ge}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

def detect_cms(soup):
    # Deteksi CMS berdasarkan tanda khas pada elemen HTML
    # Contoh: WordPress memiliki meta tag generator dengan nilai WordPress
    cms_tags = soup.find_all("meta", attrs={"name": "generator"})
    for tag in cms_tags:
        if "WordPress" in tag["content"]:
            return "WordPress"
    return "Unknown"


def detect_cloudflare(response):
    # Deteksi Cloudflare berdasarkan header server
    server_header = response.headers.get("Server")
    if server_header and "cloudflare" in server_header.lower():
        return "Detected"
    return "Not Detected"


def basic_scan():
    target_url = input("\nMasukkan URL target untuk basic scan: ")
    if not target_url.startswith('http://') and not target_url.startswith('https://'):
        target_url = 'http://' + target_url
    try:
        response = requests.get(target_url, headers=headers)
        if response.status_code == 200:
            print("\nSedang Scan untuk", target_url)
            print("\nBasic Scan untuk", target_url, "berhasil:")
            print("\n========================================")
            # Site Title
            soup = BeautifulSoup(response.text, 'html.parser')
            site_title = soup.title.string
            print("Site Title:", site_title)
            
            # IP Address
            ip_address = socket.gethostbyname(urlparse(target_url).netloc)
            print("IP Address:", ip_address)

            # CMS (Content Management System) Detection
            cms = detect_cms(soup)
            print("CMS:", cms)

            # Cloudflare Detection
            cloudflare = detect_cloudflare(response)
            print("Cloudflare Detection:", cloudflare)

            # Robots.txt Scanner
            robots_url = target_url + "/robots.txt"
            try:
                robots_response = requests.get(robots_url)
                if robots_response.status_code == 200:
                    print("Robots.txt Content:")
                    print(robots_response.text)
                else:
                    print("Robots.txt tidak ditemukan.")
            except Exception as e:
                print("Gagal mengakses robots.txt:", e)

            print("========================================")
        else:
            print("Basic Scan untuk", target_url, "gagal. Kode status:", response.status_code)
    except Exception as e:
        print("Error:", e)

def grabbing_cookie():
    target_url = input("Masukkan URL target untuk grabbing cookie: ")
    if not target_url.startswith('http://') and not target_url.startswith('https://'):
        target_url = 'http://' + target_url
    try:
        response = requests.get(target_url)
        if response.status_code == 200:
            cookies = response.cookies
            print("Cookie yang diperoleh:")
            for cookie in cookies:
                print(cookie.name, ":", cookie.value)
        else:
            print("Gagal mengambil cookie untuk", target_url, "Kode status:", response.status_code)
    except Exception as e:
        print("Error:", e)

def parse_ports(port_arg):
    if port_arg.lower() == 'all':
        return range(1, 65536)  # Scan all ports
    ports = []
    try:
        if '-' in port_arg:
            start, end = map(int, port_arg.split('-'))
            ports = list(range(start, end + 1))
        else:
            ports.append(int(port_arg))
    except ValueError:
        print("Invalid port range")
    return ports

def scan_port(ip, port):
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(0.2)
        result = sock.connect_ex((ip, port))
        sock.close()
        if result == 0:
            return port, "open"
        else:
            return port, "closed"
    except Exception as e:
        return port, f"error: {e}"

def get_service(port):
    return "unknown"

COMMON_SERVICES = {
    20: "FTP Data",
    21: "FTP Control",
    22: "SSH",
    23: "Telnet",
    25: "SMTP",
    # ini isi port port buat scan tertentunya
}


def scan_ports(target_host, ports):
    open_ports = []
    try:
        ip = socket.gethostbyname(target_host)
        print(f"Starting scan for {target_host} ({ip})")

        start_time = time.time()

        with concurrent.futures.ThreadPoolExecutor() as executor:
            futures = [executor.submit(scan_port, ip, port) for port in ports]

            for future in concurrent.futures.as_completed(futures):
                port, state = future.result()
                if state == "open":
                    open_ports.append(port)

        end_time = time.time()

        print("PORT    STATE    SERVICE")
        for port in open_ports:
            service = get_service(port) 
            print(f"{port}/tcp  open     {service}")

        total_time = end_time - start_time
        print(f"Scan completed in {total_time:.2f} seconds")

    except socket.gaierror:
        print("Hostname could not be resolved")
    except socket.error as e:
        print(f"Error occurred while scanning ports: {e}")

def scan_port_menu():
    target_host = input("Masukkan alamat IP atau nama host target: ")
    port_input = input("Masukkan port yang ingin dipindai (misalnya: 80 atau 80-100): ")
    ports = parse_ports(port_input)

    scan_ports(target_host, ports)
    
def parse_ports(port_arg: str) -> List[int]:
    """
    Parse a string representing a port range and return a list of integers.
    """
    if port_arg.lower() == 'all':
        return list(range(1, 65536))  # Scan all ports
    ports = []
    try:
        if '-' in port_arg:
            start, end = map(int, port_arg.split('-'))
            if start < 1 or end > 65535:
                raise ValueError("Invalid port range")
            ports = list(range(start, end + 1))
        else:
            port = int(port_arg)
            if port < 1 or port > 65535:
                raise ValueError("Invalid port number")
            ports.append(port)
    except ValueError as e:
        print(f"Error: {e}")
    return ports

def all_port(target: str, ports: List[int]):
    """
    Scan all ports of a target host.
    """
    print(f"Scanning all port {target}")
    for port in ports:
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(0.2)
            sock.connect((target, port))
            print(f"Port {port} is open")
            sock.close()
        except socket.error:
            pass
            
import requests
from bs4 import BeautifulSoup

def grabbing_csrf_token():
    target_url = input("Masukkan URL target untuk grabbing CSRF Token: ")
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36'}
    if not target_url.startswith('http://') and not target_url.startswith('https://'):
        target_url = 'http://' + target_url
    try:
        response = requests.get(target_url, headers=headers)
        soup = BeautifulSoup(response.text, 'html.parser')
        csrf_token_element = soup.find("input", {"name": "_csrf"})
        if csrf_token_element:
            csrf_token = csrf_token_element["value"]
            print("CSRF Token:", csrf_token)
        else:
            print("CSRF Token not found.")
    except Exception as e:
        print("Error:", e)

def ip_checker(ip_address):
    url = f"https://ipinfo.io/{ip_address}/json"
    response = requests.get(url)
    data = response.json()
    print("Informasi IP:")
    print(f"IP Address: {data['ip']}")
    print(f"Negara: {data['country']}")
    print(f"Kota: {data['city']}")
    print(f"Koordinat: {data['loc']}")
    print(f"ISP: {data['org']}")
    print(f"Zona Waktu: {data['timezone']}")
    print(f"Kode Pos: {data['postal']}")

def main():
    while True:
        print(colored('\n')) 
        print(colored(' Input   Deskripsi', 'yellow'))
        print(colored('=======  ==============================', 'green'))
        print(colored('  [0]    Basic Scan', 'white'))
        print(colored('  [1]    Banner Grabbing', 'white'))
        print(colored('  [2]    IP Grabbing', 'white'))
        print(colored('  [3]    Grabbing Cookie', 'white'))
        print(colored('  [4]    Grabbing CSRF Token', 'white'))
        print(colored('  [5]    XSS Scan', 'white'))
        print(colored('  [6]    IP Checker', 'white')) 
        print(colored('  [7]    Kembali', 'white'))
        
        choice = input("\nPilih menu : ")
        if choice == '0':
            basic_scan()
        elif choice == "1":
            banner_grabbing()
        elif choice == "2":
            ip_grabbing()
        elif choice == "3":
            grabbing_cookie()
        elif choice == "4":
            grabbing_csrf_token()
        elif choice == "5":
            url = input("Contoh: https://example.com/index.php?id=1\nMasukkan URL untuk scan vuln XSS: ")
            scan_xss(url, payloads)
        elif choice == "6":
            ip_address = input("Masukkan alamat IP: ")
            ip_checker(ip_address)
        elif choice == "7":
            print(colored("Kembali ke menu utama", 'green'))
            break
        else:
            print("Pilihan tidak valid")

if __name__ == "__main__":
   main()