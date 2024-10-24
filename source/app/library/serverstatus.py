import subprocess
import paramiko
import socket
import time

from app.helpers.littletools import CRLittletools as crlt
from app.library.storage import CRStorage as crstorage

class CRServerStatus:
    def __init__(self, hostname, ssh_port=22, ssh_username=None, ssh_password=None, ping_timeout=5, ssh_timeout=10):
        self.hostname = hostname
        self.ssh_port = ssh_port
        self.ssh_username = ssh_username
        self.ssh_password = ssh_password
        self.ping_timeout = ping_timeout
        self.ssh_timeout = ssh_timeout

    def check_ping(self):
        """
        Check if the server responds to a ping request.
        Returns True if ping is successful, False otherwise.
        """
        try:
            ping_output = subprocess.check_output(
                ["ping", "-c", "1", "-W", str(self.ping_timeout), self.hostname],
                stderr=subprocess.STDOUT,
                universal_newlines=True
            )
            if "Destination Host Unreachable" in ping_output:
                return crlt.to_json(status=False, message="Ping failed: Destination Host Unreachable")
            elif "100% packet loss" in ping_output:
                return crlt.to_json(status=False, message="Ping failed: No response (100% packet loss)")
            return crlt.to_json(status=True, message="Ping successful")
        except subprocess.CalledProcessError as e:
            return crlt.to_json(status=False, message=f"Ping failed: {e.output.strip()}")

    def check_ssh(self):
        """
        Check if the server is accessible via SSH.
        Returns True if SSH connection is successful, False otherwise.
        """
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        try:
            start_time = time.time()
            ssh.connect(self.hostname, port=self.ssh_port, username=self.ssh_username, password=self.ssh_password, timeout=self.ssh_timeout)
            duration = time.time() - start_time
            ssh.close()
            if duration > self.ssh_timeout:
                return crlt.to_json(status=False, message=f"SSH successful but connection took too long: {duration:.2f} seconds")
            return crlt.to_json(status=True, message=f"SSH successful in {duration:.2f} seconds")
        except paramiko.AuthenticationException:
            return crlt.to_json(status=False, message="Authentication failed when connecting to SSH")
        except paramiko.SSHException as e:
            return crlt.to_json(status=False, message=f"SSH exception occurred: {str(e)}")
        except socket.timeout:
            return crlt.to_json(status=False, message="SSH connection timed out")
        except Exception as e:
            return crlt.to_json(status=False, message=f"Failed to connect via SSH: {str(e)}")

    def check_port_open(self):
        """
        Check if the SSH port is open on the server.
        Returns True if port is open, False otherwise.
        """
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(5)
        result = sock.connect_ex((self.hostname, self.ssh_port))
        sock.close()
        if result == 0:
            return crlt.to_json(status=True, message=f"Port {self.ssh_port} on {self.hostname} is open")
        else:
            return crlt.to_json(status=False, message=f"Port {self.ssh_port} on {self.hostname} is closed or unreachable")

    def get_server_status(self):
        """
        Determine the server status based on ping and SSH connectivity.
        Returns one of the three conditions: active, timeout, or unaccessible.
        """
        ping = self.check_ping()
        if ping["status"]:
            ssh = self.check_ssh()
            if ssh["status"]:
                return crlt.to_json(status="active", message=f"Server is active. {ping["message"]}. {ssh["message"]}")
            else:
                return crlt.to_json(status="timeout", message=f"Ping successful, but SSH is slow or has issues. {ssh["message"]}")
        else:
            port = self.check_port_open()
            if port["status"]:
                return crlt.to_json(status="timeout", message=f"Ping failed but SSH port is open. {port["message"]}")
            else:
                return crlt.to_json(status="unaccessible", message=f"Server is not reachable. {ping["message"]}. {port["message"]}")
