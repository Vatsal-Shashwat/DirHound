#!/usr/bin/python3

import os
import requests
import threading
import sys
from argparse import ArgumentParser
from queue import Queue

# Color codes
reset = "\033[0m"
red = "\033[91m"
green = "\033[92m"
yellow = "\033[93m"
blue = "\033[94m"
purple = "\033[95m"
cyan = "\033[96m"
bold = "\033[1m"

# Banner with styling and GitHub username
banner = f"""{red}                   
 ________  .__         ___ ___                         .___
\______ \ |_________ /   |   \  ____  __ __  ____   __| _/
 |    |  \|  \_  __ /    ~    \/  _ \|  |  \/    \ / __ | 
 |    `   |  ||  | \\    Y    (  <_> |  |  |   |  / /_/ | 
/_______  |__||__|   \___|_  / \____/|____/|___|  \____ | 
        \/                 \/                   \/     \/ {reset}
                           {cyan}Advanced Directory Bruteforcing Tool{reset}  
             {purple}Created by: {reset}{yellow}Vatsal Kashyap (GitHub: Vatsal-Shashwat){reset}
"""

class DirectoryBruteforcer:
    def __init__(self, domain, wordlist, threads=10, proxy=None, status_filter=None, recursive=False):
        self.domain = domain
        self.wordlist = wordlist
        self.threads = threads
        self.proxy = {"http": proxy, "https": proxy} if proxy else None
        self.status_filter = status_filter
        self.recursive = recursive
        self.headers = {'User-Agent': 'Mozilla/5.0'}
        self.queue = Queue()
        self.found_dirs = []  # stores valid found directories
        self.total_tests = 0  # progress counter

    def read_wordlist(self):
        """this function reads the wordlist file and add words to the queue."""
        try:
            with open(self.wordlist, 'r') as file:
                for line in file:
                    self.queue.put(line.strip())
                    self.total_tests += 1  # counts total entries
        except FileNotFoundError:
            print(f'{red}[ERROR]{reset} Wordlist file "{self.wordlist}" not found!\n')
            return False
        return True

    def scan_directory(self):
        """Process each directory in the queue."""
        while not self.queue.empty():
            word = self.queue.get()
            url = f'http://{self.domain}/{word}'
            
            sys.stdout.write(f'\r{yellow}[TESTING]{reset} {url} ({self.queue.qsize()} left)    ')
            sys.stdout.flush()

            try:
                response = requests.get(url, allow_redirects=False, headers=self.headers, proxies=self.proxy)
                if response.status_code == 200:
                    self.found_dirs.append(url)  
                    print(f'\n{green}[FOUND]{reset} {bold}{url}{reset}')
                    if self.recursive:
                        self.queue.put(f'{word}/')
                elif self.status_filter and response.status_code in self.status_filter:
                    print(f'\n{blue}[FILTERED]{reset} {url} ({response.status_code})')
            except requests.exceptions.ConnectionError:
                print(f'\n{red}[ERROR] Connection Error!{reset}')
            except requests.RequestException as e:
                print(f'\n{red}[ERROR]{reset} {url}: {str(e)}')
            self.queue.task_done()

    def bruteforce(self):
        """Starts multi-threaded bruteforcing."""
        if not self.read_wordlist():
            return
        
        print(f'\n{blue}[INFO]{reset} Starting directory bruteforce with {self.threads} threads...\n')
        threads = []
        for _ in range(self.threads):
            t = threading.Thread(target=self.scan_directory)
            t.start()
            threads.append(t)
        
        for t in threads:
            t.join()

        print(f"\n{bold}{cyan}[SUMMARY]{reset} Bruteforcing complete!")
        if self.found_dirs:
            print(f"\n{green}[VALID DIRECTORIES]{reset}")
            for url in sorted(self.found_dirs):
                print(f"  {green}✔ {url}{reset}")
        else:
            print(f"\n{red}[NO VALID DIRECTORIES FOUND]{reset}")

if __name__ == '__main__':
    parser = ArgumentParser(description='DirHound - Advanced Directory Bruteforcing Tool')
    parser.add_argument('-d', '--domain', required=True, help='Target domain (e.g., example.com)')
    parser.add_argument('-w', '--wordlist', required=True, help='Path to the wordlist file')
    parser.add_argument('-t', '--threads', type=int, default=10, help='Number of threads (default: 10)')
    parser.add_argument('-p', '--proxy', help='Proxy (e.g., http://127.0.0.1:8080)')
    parser.add_argument('-s', '--status', nargs='+', type=int, help='Filter specific status codes (e.g., 403 404)')
    parser.add_argument('-r', '--recursive', action="store_true", help="Enable recursive scanning")
    
    args = parser.parse_args()
    
    os.system('clear')
    print(banner)

    bruteforcer = DirectoryBruteforcer(args.domain, args.wordlist, args.threads, args.proxy, args.status, args.recursive)
    bruteforcer.bruteforce()

