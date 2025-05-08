
import requests
import re
import sys
import os
from colorama import Fore, Style, init

init(autoreset=True)

def clear():
    os.system('clear' if os.name == 'posix' else 'cls')

def banner():
    print(Fore.GREEN + r"""
        (\(\ 
        (-.-)
       o_(")(")

     RATScan Pro By Codex91
""" + Style.RESET_ALL)

def main_menu():
    print(Fore.CYAN + """Pilih menu berikut:
1. Scan Headers
2. Cari Link dalam Halaman
3. SQL Injection Scan (simple)
4. XSS Scan (basic)
5. Brute Force Login (dictionary)
6. Extract Subdomains
7. Cek Robots.txt
8. Cari Admin Panel
9. Cek Status HTTP
10. Cek Keamanan Header
0. Keluar""")

def scan_headers(url):
    try:
        res = requests.get(url)
        print(Fore.YELLOW + "\n[+] Header Website:\n")
        for k, v in res.headers.items():
            print(f"{k}: {v}")
    except Exception as e:
        print(f"[!] Gagal mengambil headers: {e}")

def find_links(url):
    try:
        res = requests.get(url)
        links = re.findall(r'href=["\']?([^"\' >]+)', res.text)
        print(Fore.YELLOW + "\n[+] Ditemukan Link:\n")
        for link in links:
            print(link)
    except Exception as e:
        print(f"[!] Gagal mengambil link: {e}")

def sql_scan(url):
    payloads = ["'", "'--", '"', '"--']
    print(Fore.YELLOW + f"\n[+] Memindai SQL Injection pada {url}\n")
    for p in payloads:
        try:
            r = requests.get(url + p)
            if any(x in r.text.lower() for x in ["sql syntax", "mysql_fetch", "warning"]):
                print(f"[!] Kemungkinan rentan SQLi dengan payload: {p}")
        except:
            continue

def xss_scan(url):
    payload = '<script>alert(1)</script>'
    try:
        r = requests.get(url + "?q=" + payload)
        if payload in r.text:
            print("[!] XSS ditemukan!")
        else:
            print("[-] Tidak rentan terhadap XSS.")
    except Exception as e:
        print(f"[!] Error: {e}")

def brute_login(url, user_list, pass_list):
    print(Fore.YELLOW + "\n[+] Bruteforce login...")
    for u in open(user_list):
        for p in open(pass_list):
            u, p = u.strip(), p.strip()
            try:
                r = requests.post(url, data={'username': u, 'password': p})
                if "Login sukses" in r.text or r.url != url:
                    print(f"[+] Berhasil login: {u}:{p}")
                    return
            except: continue
    print("[-] Gagal login dengan kombinasi yang diberikan.")

def extract_subdomains(domain):
    subdomains = ["www", "mail", "ftp", "test", "dev"]
    for sub in subdomains:
        subdomain = f"http://{sub}.{domain}"
        try:
            res = requests.get(subdomain)
            if res.status_code < 400:
                print(f"[+] Aktif: {subdomain}")
        except: continue

def check_robots(url):
    if not url.endswith("/"): url += "/"
    try:
        res = requests.get(url + "robots.txt")
        print(Fore.YELLOW + "\n[+] Isi robots.txt:\n")
        print(res.text if res.status_code == 200 else "Tidak ditemukan.")
    except Exception as e:
        print(f"[!] Error: {e}")

def find_admin_panel(url):
    paths = ["admin", "admin/login", "administrator"]
    for path in paths:
        full = url + "/" + path
        try:
            r = requests.get(full)
            if r.status_code == 200:
                print(f"[+] Ditemukan panel admin: {full}")
        except: continue

def check_status(url):
    try:
        r = requests.get(url)
        print(f"[+] Status Code: {r.status_code}")
    except Exception as e:
        print(f"[!] Error: {e}")

def check_security_headers(url):
    try:
        r = requests.get(url)
        headers = r.headers
        print("\n[+] Keamanan Header:\n")
        for header in ["Content-Security-Policy", "X-Frame-Options", "X-XSS-Protection", "Strict-Transport-Security"]:
            print(f"{header}: {headers.get(header, 'Tidak ditemukan')}")
    except Exception as e:
        print(f"[!] Error: {e}")

def main():
    while True:
        clear()
        banner()
        main_menu()
        choice = input("\nPilih menu: ").strip()

        if choice == '0':
            print("Keluar...")
            break

        url = input("Masukkan URL target (contoh: https://example.com): ").strip()
        if not url.startswith("http"):
            url = "http://" + url

        print("\n" + "="*40)
        if choice == '1': scan_headers(url)
        elif choice == '2': find_links(url)
        elif choice == '3': sql_scan(url)
        elif choice == '4': xss_scan(url)
        elif choice == '5':
            user_list = input("Path file username list: ").strip()
            pass_list = input("Path file password list: ").strip()
            brute_login(url, user_list, pass_list)
        elif choice == '6':
            domain = url.replace("http://","").replace("https://","").split("/")[0]
            extract_subdomains(domain)
        elif choice == '7': check_robots(url)
        elif choice == '8': find_admin_panel(url)
        elif choice == '9': check_status(url)
        elif choice == '10': check_security_headers(url)
        else:
            print("Pilihan tidak valid.")

        input("\nTekan ENTER untuk kembali ke menu...")

if __name__ == "__main__":
    main()
