import time
import logging

from typing import Dict, Any
from .storage import CRStorage as crstorage
from paramiko import SSHClient as sshclient
from paramiko import AutoAddPolicy as autoaddpolicy

from paramiko import AuthenticationException
from app.helpers.littletools import CRLittletools as crltools

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)


class RemoteEXec:
    def __init__(self) -> None:
        self.crstorage = crstorage()
        self.ssh_client = sshclient()
        self.ssh_client.load_system_host_keys()
        self.ssh_client.set_missing_host_key_policy(autoaddpolicy())
        self.transport = None

    def ssh_client_connect(self, server: str, user: str = "root"):
        access = self.crstorage.get_auth_server(server)
        if access:
            try:
                logging.info(
                    f"Connecting to {access['ip_address']} with cached credentials for user '{access['username']}'."
                )
                self.ssh_client.connect(
                    hostname=access["ip_address"],
                    username=access["username"],
                    password=access["password"],
                    timeout=5.0,
                )
                self.transport = self.ssh_client.get_transport()
                logging.info(f"Successfully connected to {access['ip_address']}.")
                return self.ssh_client.open_sftp(), True
            except AuthenticationException:
                logging.warning(
                    f"Cached credentials failed for {access['ip_address']}. Attempting with other credentials..."
                )

        logging.info(
            f"No valid cached credentials found for '{server}'. Trying stored passwords..."
        )
        for password in self.crstorage.get_all_passwords():
            logging.info(password)
            try:
                logging.info(
                    f"Attempting to connect to '{server}' with provided password..."
                )
                self.ssh_client.connect(
                    hostname=server, username=user, password=password, timeout=1.0
                )
                self.transport = self.ssh_client.get_transport()
                self.crstorage.insert_auth_server(server, password)
                logging.info(
                    f"Successfully connected to '{server}' and cached the new credentials."
                )
                return self.ssh_client.open_sftp(), False
            except AuthenticationException:
                logging.warning(
                    f"Authentication failed for '{server}' with provided password."
                )
            except Exception as e:
                logging.error(
                    f"An unexpected error occurred while connecting to '{server}': {e}"
                )

        logging.error(
            f"Failed to connect to '{server}' with all available credentials."
        )
        return None, False

    def execute_command_with_log(self, command):
        """Execute command on SSH with real-time logging of stdout and stderr."""
        logging.info(f"Executing command: {command}")
        stdin, stdout, stderr = self.ssh_client.exec_command(command)

        try:
            while not stdout.channel.exit_status_ready():
                if stdout.channel.recv_ready():
                    output = stdout.channel.recv(1024).decode().strip()
                    if output:
                        logging.info(output)

                if stderr.channel.recv_ready():
                    error_output = stderr.channel.recv(1024).decode().strip()
                    if error_output:
                        logging.error(error_output)

                time.sleep(0.01)

            exit_status = stdout.channel.recv_exit_status()
            if exit_status == 0:
                logging.info(f"Command '{command}' executed successfully.")
            else:
                logging.error(
                    f"Command '{command}' failed with exit status: {exit_status}"
                )

        except Exception as e:
            logging.error(f"An error occurred while executing command '{command}': {e}")

        finally:
            stdin.close()
            stdout.close()
            stderr.close()

        return exit_status

    def execute_command(self, command):
        """Execute command on SSH and return the output."""
        logging.info(f"Executing command: {command}")
        stdin, stdout, stderr = self.ssh_client.exec_command(command)

        try:
            exit_status = stdout.channel.recv_exit_status()

            if exit_status == 0:
                output = stdout.read().decode("utf-8").strip()
                logging.info(f"Command '{command}' executed successfully.")
                return output
            else:
                error_message = stderr.read().decode("utf-8").strip()
                logging.error(f"Command '{command}' failed with error: {error_message}")
                return error_message
        except Exception as e:
            logging.error(f"An error occurred while executing command '{command}': {e}")
            return str(e)
        finally:
            stdin.close()
            stdout.close()
            stderr.close()
