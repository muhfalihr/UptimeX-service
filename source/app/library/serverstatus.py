import asyncio
import asyncssh
import paramiko
import socket
import time

from app.helpers.littletools import CRLittletools as crlt

class CRServerStatus:
    def __init__(self, hostname, ssh_port=22, ssh_username=None, ssh_password=None, ping_timeout=5, ssh_timeout=10):
        self.hostname = hostname
        self.ssh_port = ssh_port
        self.ssh_username = ssh_username
        self.ssh_password = ssh_password
        self.ping_timeout = ping_timeout
        self.ssh_timeout = ssh_timeout

    async def check_ping(self):
        """
        Check if the server responds to a ping request asynchronously.
        Returns True if ping is successful, False otherwise.
        """
        try:
            ping_process = await asyncio.create_subprocess_exec(
                'ping', '-c', '1', '-W', str(self.ping_timeout), self.hostname,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            stdout, stderr = await ping_process.communicate()

            ping_output = stdout.decode()

            if "Destination Host Unreachable" in ping_output:
                return await crlt.to_json(status=False, message="Ping failed: Destination Host Unreachable")
            elif "100% packet loss" in ping_output:
                return await crlt.to_json(status=False, message="Ping failed: No response (100% packet loss)")
            return await crlt.to_json(status=True, message="Ping successful")
        except asyncio.TimeoutError:
            return await crlt.to_json(status=False, message="Ping timed out")
        except asyncio.CancelledError:
            return await crlt.to_json(status=False, message="Ping operation was cancelled")
        except OSError as e:
            return await crlt.to_json(status=False, message=f"OS error during ping: {str(e)}")
        except Exception as e:
            return await crlt.to_json(status=False, message=f"Unexpected error during ping: {str(e)}")


    async def check_ssh(self):
        """
        Check if the server is accessible via SSH asynchronously.
        Returns True if SSH connection is successful, False otherwise.
        """
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        
        try:
            start_time = time.time()
            # Menggunakan asyncio.get_event_loop().run_in_executor untuk menjalankan operasi blocking secara async
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(
                None, 
                lambda: ssh.connect(
                    self.hostname, 
                    port=self.ssh_port, 
                    username=self.ssh_username, 
                    password=self.ssh_password, 
                    timeout=self.ssh_timeout
                )
            )
            
            duration = time.time() - start_time
            await loop.run_in_executor(None, ssh.close)
            
            if duration > self.ssh_timeout:
                return await crlt.to_json(status=False, message=f"SSH successful but connection took too long: {duration:.2f} seconds")
            return await crlt.to_json(status=True, message=f"SSH successful in {duration:.2f} seconds")
            
        except paramiko.AuthenticationException:
            return await crlt.to_json(status=False, message="Authentication failed when connecting to SSH")
        except paramiko.BadAuthenticationType as e:
            return await crlt.to_json(status=False, message=f"Bad authentication type: {str(e)}")
        except paramiko.SSHException as e:
            return await crlt.to_json(status=False, message=f"SSH exception occurred: {str(e)}")
        except socket.timeout:
            return await crlt.to_json(status=False, message="SSH connection timed out")
        except socket.gaierror as e:
            return await crlt.to_json(status=False, message=f"DNS lookup failed: {str(e)}")
        except ConnectionRefusedError:
            return await crlt.to_json(status=False, message="Connection was refused by the server")
        except Exception as e:
            return await crlt.to_json(status=False, message=f"Failed to connect via SSH: {str(e)}")
    
    async def check_port_open(self):
        """
        Check if the SSH port is open on the server asynchronously.
        Returns True if port is open, False otherwise.
        """
        loop = asyncio.get_event_loop()
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(5)

        result = await loop.run_in_executor(None, sock.connect_ex, (self.hostname, self.ssh_port))
        sock.close()

        if result == 0:
            return await crlt.to_json(status=True, message=f"Port {self.ssh_port} on {self.hostname} is open")
        else:
            return await crlt.to_json(status=False, message=f"Port {self.ssh_port} on {self.hostname} is closed or unreachable")

    async def get_server_status(self):
        """
        Determine the server status based on ping and SSH connectivity asynchronously.
        Returns one of the three conditions: active, timeout, or unaccessible.
        """
        ping = await self.check_ping()
        if ping["status"]:
            ssh = await self.check_ssh()
            if ssh["status"]:
                return await crlt.to_json(status="active", message=f"Server is active. {ping['message']}. {ssh['message']}")
            else:
                return await crlt.to_json(status="timeout", message=f"Ping successful, but SSH is slow or has issues. {ssh['message']}")
        else:
            port = await self.check_port_open()
            if port["status"]:
                return await crlt.to_json(status="timeout", message=f"Ping failed but SSH port is open. {port['message']}")
            else:
                return await crlt.to_json(status="unaccessible", message=f"Server is not reachable. {ping['message']}. {port['message']}")
