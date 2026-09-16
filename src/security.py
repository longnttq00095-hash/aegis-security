import hashlib
import os


def calculate_sha256(file_path):
    sha256 = hashlib.sha256()

    with open(file_path, "rb") as file:
        while chunk := file.read(8192):
            sha256.update(chunk)

    return sha256.hexdigest()


def calculate_md5(file_path):
    md5 = hashlib.md5()

    with open(file_path, "rb") as file:
        while chunk := file.read(8192):
            md5.update(chunk)

    return md5.hexdigest()


def security_status():
    return {
        "Firewall": "Unknown",
        "Antivirus": "Unknown",
        "System": "Normal"
    }