#!/usr/bin/env python3
import requests
from urllib.parse import urlparse
import os
import socket
import urllib.request
import time
import concurrent.futures
from typing import List
from termcolor import colored

def clear_screen(pepek):
    os.system('cls' if os.name == 'linux' else 'clear')
    return None

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
    COMMON_SERVICES = {
    20: "FTP Data",
    21: "FTP Control",
    22: "SSH",
    23: "Telnet",
    25: "SMTP",
    80: "HTTP", 
    443: "HTTPS", 
    # ini isi port port buat scan tertentunya
}
    for service, number in COMMON_SERVICES.items():
        if port == number:
            return service

def scan_ports(target_host, ports):
    open_ports = []
    try:
        ip = socket.gethostbyname(target_host)
        print(f"\nStarting scan for {target_host} ({ip})")

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
            print(f"{port}     open     {service}")

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
            print(f"\n[+] Port {port} is open")
            sock.close()
        except socket.error:
            pass
            
import socket
import time

def IP_resolver_checker(url):
    try:
        ip_address = socket.gethostbyname(url)
        print(f"IP Address dari {url} adalah {ip_address}")

        # Periksa apakah hostnya aktif atau tidak
        start_time = time.time()
        timeout = 5  # Set waktu timeout dalam detik
        socket.setdefaulttimeout(timeout)
        is_active = False

        try:
            # Coba buka koneksi ke host
            socket.create_connection((ip_address, 80))
            is_active = True
        except Exception as e:
            print(f"Gagal menghubungkan ke {url}: {e}")

        end_time = time.time()
        elapsed_time = end_time - start_time

        if is_active:
            print(f"Host {url} aktif.\nWaktu yang diperlukan untuk menghubungkan: {elapsed_time} detik")
        else:
            print(f"Host {url} tidak aktif")

    except socket.gaierror as e:
        print(f"Gagal mendapatkan IP Address dari {url}: {e}")
    except Exception as e:
        print(f"Terjadi kesalahan: {e}")
         
import requests

def read_contents(url):
    response = requests.get(url)
    if response.status_code == 200:
        return response.text
    else:
        return None

def scan_site(ipsl):
    reallink = ipsl
    lwwww = ipsl.replace("www.", "")
    print("\n[+] Scanning Begins ... \n")
    print("[i] Scanning Site: " + ipsl + "\n")
    print("[S] Scan Type : DNS Lookup")
    print("\n")
    urldlup = "http://api.hackertarget.com/dnslookup/?q=" + lwwww
    resultdlup = read_contents(urldlup)
    if resultdlup:
        dnslookups = resultdlup.split("\n")
        for dnslkup in dnslookups:
            print("[DNS Lookup] " + dnslkup)
        input()
    else:
        print("Error: Unable to fetch DNS lookup data.")
 
import sys

def print_menu():
    print("""
    \033[92m 
___   ___ ___________
|  | |  | |  |      |
|  | |  | |  |   ---|
|  |_|  |_| '|---   |
|____________|______|

\033[97m[\033[92m ADVANCE Web Scanner \033[97m] Made By \033[92m ./Clèmantiné\033[97m
[ \033[92mhttps://github.com/Azarela-Vnk \033[97m]
    """)

    print(colored(' Input   Deskripsi', 'yellow'))
    print(colored('=======  ==============================', 'green'))
    print(colored('  [1]    Scan Port Tertentu', 'white'))
    print(colored('  [2]    Scan Semua Port (Tidak di rekomendasikan)', 'white'))
    print(colored('  [3]    IP resolver checker', 'white'))
    print(colored('  [4]    DNS lookup', 'white'))
    print(colored('  [5]    Kembali ke menu utama', 'white'))

def main():
    while True:
        try:
            print_menu()
            choice = input("\nPilih menu : ")
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
            continue

        if choice == "1":
            scan_port_menu()
            pepek = input(colored("\n[*] Scanning Complete. Press Enter To Continue OR CTRL + C To Stop\n", 'yellow'))
            clear_screen(pepek)
        elif choice == "2":
            target = input("Masukkan alamat IP atau nama Host target: ")
            ports = list(range(1, 65536))
            all_port(target, ports)
            pepek = input(colored("\n[*] Scanning Complete. Press Enter To Continue OR CTRL + C To Stop\n", 'yellow'))
            clear_screen(pepek)
        elif choice == "3":
            url = input("Masukan URL: ")
            IP_resolver_checker(url)
            pepek = input(colored("\n[*] Scanning Complete. Press Enter To Continue OR CTRL + C To Stop\n", 'yellow'))
            clear_screen(pepek)
        elif choice == "4":
            ipsl = input("Masukkan URL: ") 
            scan_site(ipsl)
            pepek = input(colored("\n[*] Scanning Complete. Press Enter To Continue OR CTRL + C To Stop\n", 'yellow'))
            clear_screen(pepek)
        elif choice == "5":
            break
        else:
            print("Pilihan tidak valid")

if __name__ == "__main__":
    main()