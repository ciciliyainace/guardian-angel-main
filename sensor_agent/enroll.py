#!/usr/bin/env python3
"""
SentinelAI Sensor Enrollment Tool.

Authenticates with the SentinelAI backend as an administrator,
registers a new host network sensor, and generates `sensor_config.json`.
"""

import os
import sys
import json
import socket
import argparse
import httpx


def enroll(backend_url: str, username: str, password: str, sensor_id: str, name: str):
    backend_url = backend_url.rstrip("/")
    login_url = f"{backend_url}/auth/login"
    enroll_url = f"{backend_url}/sensors/enroll"

    print(f"[*] Connecting to SentinelAI backend at: {backend_url}")
    with httpx.Client() as client:
        # 1. Admin Login
        print(f"[*] Authenticating as admin user '{username}'...")
        try:
            res = client.post(login_url, json={"username": username, "password": password}, timeout=10.0)
            if res.status_code != 200:
                print(f"[!] Authentication failed: {res.status_code} - {res.text}")
                sys.exit(1)
            token = res.json().get("access_token")
            if not token:
                print("[!] Did not receive access_token from login.")
                sys.exit(1)
            print("[+] Admin authentication successful.")
        except Exception as e:
            print(f"[!] Failed to reach backend: {e}")
            sys.exit(1)

        # 2. Sensor Enrollment
        headers = {"Authorization": f"Bearer {token}"}
        payload = {
            "sensor_id": sensor_id,
            "name": name,
            "hostname": socket.gethostname(),
            "collector_types": ["windows_sockets", "suricata"],
        }
        print(f"[*] Registering sensor '{sensor_id}' ('{name}')...")
        try:
            res = client.post(enroll_url, json=payload, headers=headers, timeout=10.0)
            if res.status_code not in (200, 201):
                print(f"[!] Sensor enrollment failed: {res.status_code} - {res.text}")
                sys.exit(1)
            data = res.json()
            api_key = data.get("api_key")
            print(f"[+] Sensor successfully registered!")
            print(f"[+] Sensor ID: {data.get('sensor_id')}")
            print(f"[+] Sensor Key: {api_key[:12]}********************")
        except Exception as e:
            print(f"[!] Enrollment request error: {e}")
            sys.exit(1)

        # 3. Write sensor_config.json
        config_data = {
            "backend_url": backend_url,
            "sensor_id": sensor_id,
            "sensor_key": api_key,
            "name": name,
            "hostname": socket.gethostname(),
            "suricata_eve_path": "C:\\Program Files\\Suricata\\log\\eve.json",
            "poll_interval_sec": 5.0,
            "heartbeat_interval_sec": 30.0,
            "batch_size": 50,
        }
        config_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "sensor_config.json")
        with open(config_path, "w", encoding="utf-8") as f:
            json.dump(config_data, f, indent=2)
        print(f"[+] Configuration saved to: {config_path}")
        print("\n[✓] Sensor is ready! Run `python sensor_agent.py` or double-click `run_sensor.bat` to begin live monitoring.\n")


def main():
    parser = argparse.ArgumentParser(description="Enroll SentinelAI Network Sensor")
    parser.add_argument("--backend-url", default="http://127.0.0.1:8000/api/v1", help="SentinelAI API base URL")
    parser.add_argument("--user", default="admin", help="Admin username")
    parser.add_argument("--password", default="Admin123!", help="Admin password")
    parser.add_argument("--sensor-id", default=f"sensor-{socket.gethostname().lower()[:12]}", help="Unique Sensor ID")
    parser.add_argument("--name", default=f"Host Sensor ({socket.gethostname()})", help="Friendly Sensor Name")

    args = parser.parse_args()
    enroll(args.backend_url, args.user, args.password, args.sensor_id, args.name)


if __name__ == "__main__":
    main()
