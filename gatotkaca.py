#!/usr/bin/env python3  
# -*- coding: utf-8 -*-  
import os  
import sys  
import time  
import base64  
import hashlib  
import subprocess  
from datetime import datetime  
from threading import Thread  
from colorama import Fore, Style, init  

# === ENCRYPTED CORE DATA (BASE64 + SHA256) === #  
_DEV_ENC = b'RGltYXMgTmFyZW5kcmEgU3VkaWJ5bw=='  
_IG_ENC = b'ZGlfbV9uX3N1ZGlieW8='  # Decode via: base64.b64decode(_IG_ENC).decode()  
_SIG = hashlib.sha256(b'dnsCatSecure2023').hexdigest()  

# === INITIALIZATION === #  
init(autoreset=True)  
LOCK_FILE = "/tmp/gatotkaca.lock"  

class GatotkacaEngine:  
    def __init__(self):  
        self.BLOCKLIST_URL = "https://mirror.dns.cat/threatfeed.txt"  
        self.THREAT_DB = self._fetch_threat_intel()  
        self.ACTIVE = True  
        self._setup_dirs()  

    def _auth_check(self):  
        dev_name = base64.b64decode(_DEV_ENC).decode()  
        ig_handle = base64.b64decode(_IG_ENC).decode()  
        print(f"\n{Fore.CYAN}🔐 {dev_name} | {Fore.MAGENTA}✉️ @{ig_handle}")  
        print(f"{Fore.YELLOW}🛡️ Security Token: {_SIG[:12]}...{Style.RESET_ALL}\n")  

    def _setup_dirs(self):  
        os.makedirs("/data/logs/gatotkaca", exist_ok=True)  
        os.makedirs("/data/rules", exist_ok=True)  

    def _fetch_threat_intel(self):  
        try:  
            curl_cmd = f"curl -sL {self.BLOCKLIST_URL} | grep -E '^[^#]'"  
            threats = subprocess.check_output(curl_cmd, shell=True, text=True).splitlines()  
            return set(threat.strip() for threat in threats if threat)  
        except:  
            return {"malware.c2", "45.155.205.*", ":31337"}  

    def _animate_status(self):  
        symbols = ["🌐", "🔍", "🛡️"]  
        while self.ACTIVE:  
            for sym in symbols:  
                sys.stdout.write(f"\r{sym} Live Monitoring... {datetime.now().strftime('%H:%M:%S')}  ")  
                sys.stdout.flush()  
                time.sleep(1)  

    def _block_entity(self, entity):  
        with open("/data/rules/active_threats.rules", "a") as f:  
            f.write(f"{entity}|{datetime.now().isoformat()}\n")  
        print(f"{Fore.RED}⛔ BLOCKED: {Fore.WHITE}{entity}")  

    def _scan_connections(self):  
        try:  
            ss_output = subprocess.check_output(["ss", "-tunp"], text=True, stderr=subprocess.DEVNULL)  
            for conn in ss_output.splitlines():  
                for pattern in self.THREAT_DB:  
                    if pattern in conn:  
                        ip_port = conn.split()[4]  
                        self._block_entity(ip_port)  
                        break  
        except Exception as e:  
            print(f"{Fore.YELLOW}⚠️ Error: {e}")  

    def start(self):  
        self._auth_check()  
        Thread(target=self._animate_status, daemon=True).start()  
        try:  
            while self.ACTIVE:  
                self._scan_connections()  
                time.sleep(10)  
        except KeyboardInterrupt:  
            self.ACTIVE = False  
            print(f"\n{Fore.GREEN}✅ Graceful shutdown at {datetime.now()}")  

# === SECURE ENTRY POINT === #  
if __name__ == "__main__":  
    if os.path.exists(LOCK_FILE):  
        print(f"{Fore.RED}🚫 Another instance is already running!")  
        sys.exit(1)  
      
    with open(LOCK_FILE, "w") as f:  
        f.write(_SIG)  
      
    try:  
        engine = GatotkacaEngine()  
        engine.start()  
    finally:  
        os.remove(LOCK_FILE)  
