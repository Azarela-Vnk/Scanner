import re
import requests
import json
from subprocess import DEVNULL, STDOUT, run
from typing import Optional
from termcolor import colored

# Constants
WP_CONTENT_MARKER = "wp-content"
WP_README_URL = "/readme.html"
WP_LICENSE_URL = "/license.txt"
WP_UPLOADS_URL = "/wp-content/uploads/"
WP_XMLRPC_URL = "/xmlrpc.php"
WP_LOGIN_USERNAME_REGEX = "/wp-json/wp/v2/users"

def read_contents(url: str) -> str:
    if not url.startswith("http"):
        url = "http://" + url
    response = requests.get(url)
    return response.text if response.status_code == 200 else ""

def is_wordpress(url: str) -> bool:
    return WP_CONTENT_MARKER in read_contents(url)

def get_wordpress_version(url: str) -> Optional[str]:
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
            response = requests.get(protocol + url + '/wp-json/wp/v2/users', timeout=5, verify=False)
            response.raise_for_status()
            data = response.json()
            for user in data:
                wpjsonuser.append(user['slug'])
                print("Found user from wp-json : " + GREEN + user['slug'])
    except requests.exceptions.RequestException as err:
        print(f"Error while fetching data: {err}")
    except (KeyError, TypeError):
        print("Failed to parse json")

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

def main():
    while True:
        print(colored("""
        ╭──────────༺♡༻──────────╮
           Made By ./Clèmantiné
        ╰──────────༺♡༻──────────╯
        """, 'green'))
        print(colored(' Input   Deskripsi', 'yellow'))
        print(colored('=======  ==============================', 'green'))
        print(colored('  [1]    WordPress Scan', 'white'))
        print(colored('  [2]    Kembali ke menu utama', 'white'))
        
        choice = input("\nEnter the number of your choice: ")
        if choice == "1":
            ipsl = input("\nEnter the IP or domain name of the website: ")
            scan_wordpress(ipsl)
        elif choice == "2":
            print("Exiting...")
            break
        else:
            print("Invalid choice. Please try again.")

if __name__ == "__main__":
    main()