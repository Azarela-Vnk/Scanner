#!/usr/bin/env python3
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
    target_url = input("\nMasukkan URL target: ")

    try:
        # Resolve the IP address
        ip_address = socket.gethostbyname(target_url)
        print("\n==========================")
        print(f"IP Address: {ip_address}")

        # Find location by IP address
        geolocator = Nominatim(user_agent="myGeocoder")
        g = geocoder.ip(ip_address)

        if g.latlng:
            location = geolocator.reverse((g.latlng[0], g.latlng[1]))

            if location is not None:
                print(f"Lokasi: {location.address}")
            else:
                print(f"Tidak dapat menemukan lokasi IP address: {ip_address}")

        else:
            print(f"Tidak dapat menemukan lokasi IP address: {ip_address}")

    except socket.gaierror as e:
        print(f"Gagal mendapatkan IP address: {e}")

    except socket.gaierror as ge:
        print(f"Error: {ge}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

def detect_cms(soup):
    cms_tags = soup.find_all("meta", attrs={"name": "generator"})
    for tag in cms_tags:
        if "WordPress" in tag["content"]:
            return "WordPress"
    
    # Deteksi Drupal
    drupal_tags = soup.find_all("meta", attrs={"name": "Generator", "content": "Drupal"})
    if drupal_tags:
        return "Drupal"
    
    # Deteksi Joomla
    joomla_tags = soup.find_all("meta", attrs={"name": "generator", "content": "Joomla!"})
    if joomla_tags:
        return "Joomla"

    return "Unknown"

def detect_cloudflare(response):
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
    target_url = input("\nMasukkan URL target untuk grabbing cookie: ")
    if not target_url.startswith('http://') and not target_url.startswith('https://'):
        target_url = 'http://' + target_url
    try:
        response = requests.get(target_url)
        if response.status_code == 200:
            cookies = response.cookies
            if cookies:
                print("\nCookie yang diperoleh:")
                for cookie in cookies:
                    print(cookie.name, ":", cookie.value)
            else:
                print("\nTidak ada cookie yang ditemukan untuk", target_url)
        else:
            print("\nGagal mengambil cookie untuk", target_url, "Kode status:", response.status_code)
    except requests.RequestException as e:
        print("Error:", e)

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
        print(colored('  [5]    IP Checker', 'white')) 
        print(colored('  [6]    Kembali', 'white'))
        
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
            ip_address = input("Masukkan alamat IP: ")
            ip_checker(ip_address)
        elif choice == "6":
            print(colored("Kembali ke menu utama", 'green'))
            break
        else:
            print("Pilihan tidak valid")

if __name__ == "__main__":
   main()