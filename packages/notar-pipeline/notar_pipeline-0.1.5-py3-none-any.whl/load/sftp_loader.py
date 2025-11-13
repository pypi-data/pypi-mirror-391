import os
import paramiko
from datetime import datetime

class SFTPClient:
    def __init__(self, host: str, port: int, username: str, password: str):
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.ssh = None
        self.sftp = None

    def connect(self):
        """Stellt eine SFTP-Verbindung her"""
        self.ssh = paramiko.SSHClient()
        self.ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        self.ssh.connect(hostname=self.host, port=self.port, username=self.username, password=self.password)
        self.sftp = self.ssh.open_sftp()

    def disconnect(self):
        """Beendet die Verbindung"""
        if self.sftp: 
            self.sftp.close()
        if self.ssh:
            self.ssh.close()

    def list_files(self, remote_dir: str) -> list:
        """Gibt eine Liste aller Dateien im Remote-Verzeichnis zurück"""
        try:
            self.connect()
            files = self.sftp.listdir_attr(remote_dir)
            result = [
                {
                    "filename": f.filename,
                    "size": f.st_size,
                    "modified": datetime.fromtimestamp(f.st_mtime)
                }
                for f in files
            ]
            return sorted(result, key=lambda x: x["modified"], reverse=True)
        finally:
            self.disconnect()

    def download_file(self, remote_path: str, local_path: str):
        """Lädt eine Datei herunter"""
        try:
            self.connect()
            os.makedirs(os.path.dirname(local_path), exist_ok=True)
            self.sftp.get(remote_path, local_path)
            print(f"✅ Datei heruntergeladen: {remote_path} → {local_path}")
        finally:
            self.disconnect()

    def download_latest_file(self, remote_dir: str, local_dir: str, prefix: str = ""):
        """
        Lädt die neueste Datei im Remote-Verzeichnis herunter (optional mit Prefix-Filter)
        """
        try:
            self.connect()
            files = self.sftp.listdir_attr(remote_dir)

            if prefix:
                files = [f for f in files if f.filename.startswith(prefix)]

            if not files:
                print("Keine passenden Dateien gefunden.")
                return None

            latest_file = max(files, key=lambda f: f.st_mtime)
            remote_path = os.path.join(remote_dir, latest_file.filename)
            local_path = os.path.join(local_dir, latest_file.filename)

            os.makedirs(local_dir, exist_ok=True)
            self.sftp.get(remote_path, local_path)
            print(f"Neueste Datei heruntergeladen: {latest_file.filename}")
            return local_path

        finally:
            self.disconnect()
