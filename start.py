#!/usr/bin/env python3
import core.basic as basic
import core.scan as scan
import core.cms as cms
from termcolor import colored

def main():
    while True:
        print('\n')
        print(colored("""
        ᴍᴀᴅᴇ ʙʏ ./𝐶𝑙𝑒̀𝑚𝑎𝑛𝑡𝑖𝑛𝑒́。        •         ﾟ。
        .    .             .                。    。.
    .         。     ඞ 。     . •
• 𝐼 ℎ𝑜𝑝𝑒 𝑦𝑜𝑢 𝑎𝑟𝑒 𝑛𝑜𝑡 𝑎𝑛 𝑖𝑚𝑝𝑜𝑠𝑡𝑒𝑟 •.
        """, 'green'))
        print(colored(' Input   Deskripsi', 'yellow'))
        print(colored('=======  ==============================', 'green'))
        print(colored('  [1]    Basic Scan', 'white'))
        print(colored('  [2]    IP Scanner', 'white'))
        print(colored('  [3]    CMS', 'white'))
        print(colored('  [4]    Exit', 'white'))
        
        choice = input("\nPilih menu : ")
        if choice == '1':
            basic.main()
        elif choice == '2':
            scan.main()
        elif choice == '3':
            cms.main()
        elif choice == '4':
            print(colored('Terima kasih telah menggunakan program ini.', 'green'))
            break
        else:
            print('Menu yang Anda pilih tidak valid. Silakan coba lagi.')

if __name__ == "__main__":
    main()