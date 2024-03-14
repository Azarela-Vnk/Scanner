#!/usr/bin/env python3

import re
import requests
import json
from subprocess import DEVNULL, STDOUT, run
from typing import Optional
from termcolor import colored
from bs4 import BeautifulSoup
from urllib.parse import urlparse

WP_CONTENT_MARKER = "wp-content"
WP_README_URL = "/readme.html"
WP_LICENSE_URL = "/license.txt"
WP_UPLOADS_URL = "/wp-content/uploads/"
WP_XMLRPC_URL = "/xmlrpc.php"

headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
    }

def read_contents(url: str) -> str:
    if not url.startswith("http"):
        url = "http://" + url
    response = requests.get(url, headers=headers)
    return response.text if response.status_code == 200 else ""


def is_wordpress(url: str) -> bool:
    return WP_CONTENT_MARKER in read_contents(url)


def get_wordpress_version(url: str) -> str:
    srccd = read_contents(url)

    matches = re.search(r'<meta name="generator" content="WordPress (.*?)"', srccd, re.I | re.S)
    if matches:
        return matches.group(1)

    feedsrc = read_contents(url + WP_README_URL)
    matches = re.search(r'<generator>https://wordpress.org/\?v=(.*?)</generator>', feedsrc, re.I | re.S)
    if matches:
        return matches.group(1)

    lopmlsrc = read_contents(url + "/wp-links-opml.php")
    matches = re.search(r'generator="wordpress/(.*?)"', lopmlsrc, re.I | re.S)
    if matches:
        return matches.group(1)

    return None


def get_wordpress_plugins(url: str) -> list[str]:
    srccd = read_contents(url)
    plugin_regex = r'<a href="(.*?)" title="(.*?)" rel="(.*?)">(.*?)</a>'
    matches = re.findall(plugin_regex, srccd, re.I | re.S)
    return [match[3] for match in matches]


def get_wordpress_themes(url: str) -> list[str]:
    srccd = read_contents(url + "/wp-content/themes/")
    theme_regex = r'<a href="(.*?)" title="(.*?)">(.*?)</a>'
    matches = re.findall(theme_regex, srccd, re.I | re.S)
    return [match[2] for match in matches]


def scan_wordpress(url: str):
    # ANSI color codes
    RED = '\033[91m'
    GREEN = '\033[92m'
    BLUE = '\033[94m'
    END_COLOR = '\033[0m'

    print("Scanning Begins ... ")
    print("Scanning Site: " + url)
    print(GREEN + "[S] Scan Type : WordPress Scanner." + END_COLOR)
    print("\n")
    print(GREEN + "[+] Checking if the site is built on WordPress: " + END_COLOR)

    if is_wordpress(url):
        print(GREEN + "Determined !" + END_COLOR)
        print("\n\t WordPress Information ")
        print("\t======================")

        wp_version = get_wordpress_version(url)
        if wp_version:
            print("\t" + GREEN + " WordPress Version   : " + wp_version + END_COLOR)
        else:
            print("\t WordPress Version   : " + RED + "Unknown" + END_COLOR)

        print("\n\t Basic Checks ")
        print("\t==============")

        wp_rm_src = read_contents(url + WP_README_URL)
        if "Welcome. WordPress is a very special project to me." in wp_rm_src:
            print("\t" + GREEN + " Readme File Found, Link: " + url + WP_README_URL + END_COLOR)
        else:
            print("\t Readme File Not Found!")

        wp_lic_src = read_contents(url + WP_LICENSE_URL)
        if "WordPress - Web publishing software" in wp_lic_src:
            print("\t" + GREEN + " License File Found, Link: " + url + WP_LICENSE_URL + END_COLOR)
        else:
            print("\t License File Not Found!")

        wp_updir_src = read_contents(url + WP_UPLOADS_URL)
        if "Index of /wp-content/uploads" in wp_updir_src:
            print("\t" + GREEN + url + WP_UPLOADS_URL + " Is Browseable" + END_COLOR)
        else:
            print("\t" + RED + " Could Not Find wp-content/uploads" + END_COLOR)

        wp_xmlrpc_src = read_contents(url + WP_XMLRPC_URL)
        if "XML-RPC server accepts POST requests only." in wp_xmlrpc_src:
            print("\t" + GREEN + " XML-RPC interface Available Under " + url + WP_XMLRPC_URL + END_COLOR)
        else:
            print("\t" + RED + " Could Not Find XML-RPC interface" + END_COLOR)

        print("\n\tPlugins ")
        print("\t=======")

        plugins = get_wordpress_plugins(url)
        if plugins:
            print("\t" + GREEN + " Plugins Found:" + END_COLOR)
            for plugin in plugins:
                print("\t - " + plugin)
        else:
            print("\t" + RED + "No Plugins Found!" + END_COLOR)

        print("\n\tThemes ")
        print("\t======")

        themes = get_wordpress_themes(url)
        if themes:
            print("\t" + GREEN + " Themes Found:" + END_COLOR)
            for theme in themes:
                print("\t - " + theme)
        else:
            print("\t" + RED + "No Themes Found!" + END_COLOR)

        print("\n\tStarting Username Harvest")
        print("\t===========================")
        # Harvest usernames via site's json api
        print('Harvesting usernames from wp-json api')
        wpjsonuser = []
        try:
            for protocol in ['http://', 'https://']:
              response = requests.get(protocol + url + '/wp-json/wp/v2/users', timeout=5, verify=False, headers=headers)
              response.raise_for_status()
              data = response.json()
            for user in data:
                wpjsonuser.append(user['slug'])
                print("Found user from wp-json : " + GREEN + user['slug'])
        except requests.exceptions.RequestException as err:
           print(f"Error while fetching data: {err}")
        except (json.JSONDecodeError, ValueError):
           print("Failed to parse JSON response")
        except KeyError:
           print("Failed to find 'slug' key in JSON response")

        # Combine all the usernames that we collected
        usernames = set(wpjsonuser)
        if len(usernames) > 0:
            usernamesgen = '1'  # Some usernames were harvested
            if len(usernames) == 1:
                print(str(len(usernames)) + " Username" + " was enumerated")
            else:
                print(str(len(usernames)) + " Usernames" + " were enumerated")
        else:
            usernamesgen = '0'  # Failure
            print("Couldn't enumerate usernames :( ")

        return [usernamesgen, usernames]
    else:
        print(RED + "WordPress not detected on the site." + END_COLOR)


    # Drupal
import requests
from bs4 import BeautifulSoup

def scan_drupal(target_url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
    }

    if not target_url.startswith("http://") and not target_url.startswith("https://"):
        target_url = "http://" + target_url

    try:
        response = requests.get(target_url, headers=headers, timeout=5)

        if response.status_code == 200:
            if 'Drupal' in response.text:
                print("Target website runs on Drupal CMS. Potential vulnerabilities detected.")
                soup = BeautifulSoup(response.text, 'html.parser')
                admin_links = soup.find_all('a', href=True, text='admin')
                if admin_links:
                    print("Potential admin panel found:", admin_links[0]['href'])
                else:
                    print("No admin panel found")
                
                # Check for specific vulnerable plugins
                vulnerable_plugin = check_vulnerable_plugin(target_url)
                if vulnerable_plugin:
                    print("Detected vulnerable plugin:", vulnerable_plugin)
                else:
                    print("No vulnerable plugin found")
                
                # Check for vulnerable configurations
                check_vulnerable_config(target_url)
            else:
                print("Target website does not run on Drupal CMS.")
        else:
            print("Failed to fetch URL:", target_url)
    except Exception as e:
        print("Error occurred while scanning:", str(e))

def check_vulnerable_plugin(target_url):
    vulnerable_plugins = ['plugin1', 'plugin2', 'plugin3']

    try:
        response = requests.get(target_url)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            vulnerable_plugin_links = soup.find_all(class_='plugin-class', id='plugin-id')
            for link in vulnerable_plugin_links:
                plugin_name = link.text.strip()
                if plugin_name in vulnerable_plugins:
                    return plugin_name
    except Exception as e:
        print("Error occurred while checking vulnerable plugins:", str(e))

    return None

def check_vulnerable_config(target_url):
    if "admin" in target_url:
        print("Vulnerable configuration detected: Admin access enabled")

    if "phpmyadmin" in target_url:
        print("Vulnerable configuration detected: phpMyAdmin access enabled")

    if "wp-admin" in target_url:
        print("Vulnerable configuration detected: WordPress admin access enabled")

    if "drupal" in target_url:
        print("Vulnerable configuration detected: Drupal CMS detected")

    if "config" in target_url:
        print("Vulnerable configuration detected: Configuration files accessible")
    return None

def detect_cms(target_url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
    }
    
    pet = re.compile('<meta name="generator" content="(.*)" />')
    
    if not target_url.startswith("http://") and not target_url.startswith("https://"):
        target_url = "http://" + target_url
    
    try:
        response = requests.get(target_url, headers=headers, timeout=15)
        if response.status_code == 200:
            src = response.text
            generator_match = re.search(pet, src)
            if generator_match:
                generator = generator_match.group(1)
                if 'WordPress' in generator:
                    print('--| ' + target_url + ' --> [WordPress]')
                    with open('wordpress.txt', mode='a') as d:
                        d.write(target_url + '/\n')
                elif 'Joomla' in generator:
                    print('--| ' + target_url + ' --> [Joomla]')
                    with open('joomla.txt', mode='a') as d:
                        d.write(target_url + '/\n')
                elif 'Drupal' in generator:
                    print('--| ' + target_url + ' --> [Drupal]')
                    with open('drupal.txt', mode='a') as d:
                        d.write(target_url + '/\n')
                elif 'PrestaShop' in generator:
                    print('--| ' + target_url + ' --> [PrestaShop]')
                    with open('prestashop.txt', mode='a') as d:
                        d.write(target_url + '/\n')
                else:
                    if 'wp-content/themes' in src:
                        print('--| ' + target_url + ' --> [WordPress]')
                        with open('wordpress.txt', mode='a') as d:
                            d.write(target_url + '/\n')
                    elif 'catalog/view/theme' in src:
                        print('--| ' + target_url + ' --> [OpenCart]')
                        with open('opencart.txt', mode='a') as d:
                            d.write(target_url + '/\n')
                    elif 'sites/all/themes' in src:
                        print('--| ' + target_url + ' --> [Drupal]')
                        with open('drupal.txt', mode='a') as d:
                            d.write(target_url + '/\n')
                    elif '<script type="text/javascript" src="/media/system/js/mootools.js"></script>' in src or '/media/system/js/' in src or 'com_content' in src:
                        print('--| ' + target_url + ' --> [Joomla]')
                        with open('joomla.txt', mode='a') as d:
                            d.write(target_url + '/\n')
                    elif 'js/jquery/plugins/' in src:
                        print('--| ' + target_url + ' --> [PrestaShop]')
                        with open('prestashop.txt', mode='a') as d:
                            d.write(target_url + '/\n')
                    else:
                        print('--| ' + target_url + ' --> [Other]')
                        with open('other.txt', mode='a') as d:
                            d.write(target_url + '/\n')
            else:
                print('--| ' + target_url + ' --> [Other]')
                with open('other.txt', mode='a') as d:
                    d.write(target_url + '/\n')
        else:
            print('--| ' + target_url + ' --> [Failed to fetch URL]')
    except requests.exceptions.Timeout:
        print('--| ' + target_url + ' --> [Time Out]')
    except requests.exceptions.RequestException as e:
        print('--| ' + target_url + ' --> [Request Exception: {}]'.format(str(e)))

def scan_joomla(target_url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
    }

    if not target_url.startswith("http://") and not target_url.startswith("https://"):
        target_url = "http://" + target_url

    try:
        response = requests.get(target_url, headers=headers, timeout=5)

        if response.status_code == 200:
            if 'Joomla' in response.text:
                print("Hacked into the target website! Joomla CMS compromised.")
                soup = BeautifulSoup(response.text, 'html.parser')
                admin_links = soup.find_all('a', href=True, text='administrator')
                if admin_links:
                    print("Admin credentials stolen: Check this link:", admin_links[0]['href'])
                    steal_user_data(target_url)
                    install_malware(target_url)
                    delete_website(target_url)
                else:
                    print("No admin panel found, but we are already in!")
            else:
                print("Target website does not run on Joomla CMS.")
        else:
            print("Failed to fetch URL:", target_url)
    except Exception as e:
        print("Error occurred while hacking:", str(e))

def steal_user_data(target_url):
    print("Stealing user data from the database...")

def install_malware(target_url):
    print("Installing malware to gain full control...")

def delete_website(target_url):
    print("Deleting the entire website...")

def main():
    while True:
        print(colored("""
        ╭──────────༺♡༻──────────╮
           Made By ./Azarela
        ╰──────────༺♡༻──────────╯
        """, 'green'))
        print(colored(' Input   Deskripsi', 'yellow'))
        print(colored('=======  ==============================', 'green'))
        print(colored('  [1]    CMS Scan', 'white'))
        print(colored('  [2]    WordPress Scan', 'white'))
        print(colored('  [3]    Drupal Scan', 'white'))
        print(colored('  [4]    Joomla Scan (Joke Features)', 'white'))
        print(colored('  [5]    Kembali ke menu utama', 'white'))
        
        choice = input("\nEnter the number of your choice: ")
        if choice == "1":
            target_url = input("\nEnter the IP or domain name of the website: ")
            detect_cms(target_url)
        elif choice == "2":
            ipsl = input("\nEnter the IP or domain name of the website: ")
            scan_wordpress(ipsl)
        elif choice == "3":
            target_url = input("\nURL: ")
            scan_drupal(target_url)
        elif choice == "4":
            target_url = input("\nURL: ")
            scan_joomla(target_url)
        elif choice == "5":
            break
        else:
            print("Invalid choice. Please try again.")

if __name__ == "__main__":
    main()