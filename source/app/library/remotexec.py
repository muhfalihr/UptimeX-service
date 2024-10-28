import logging
import asyncssh

from typing import Dict, Any
from .hydra import get_password
from .storage import CRStorage as crstorage
from app.helpers.littletools import CRLittletools as crltools

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)


class RemoteEXec:
    def __init__(self) -> None:
        self.connection = None
        self.crstorage = crstorage()

    async def ssh_client_connect(self, server: str, user: str = "root"):
        await self.crstorage.connect()
        access = await self.crstorage.get_auth_specific_server(server)
        if access:
            try:
                logging.info(
                    f"Connecting to {access['ip_address']} with cached credentials for user '{access['username']}'."
                )
                self.connection = await asyncssh.connect(
                    host=access["ip_address"],
                    username=access["username"],
                    password=access["password"],
                    known_hosts=None,
                )
                logging.info(f"Successfully connected to {access['ip_address']}.")
                return self.connection, True
            except asyncssh.ProcessError:
                logging.warning(
                    f"Cached credentials failed for {access['ip_address']}. Attempting with other credentials..."
                )

        logging.info(
            f"No valid cached credentials found for '{server}'. Trying stored passwords..."
        )

        password = get_password(user, server, threads=64)
        try:
            logging.info(
                f"Attempting to connect to '{server}' with provided password..."
            )
            self.connection = await asyncssh.connect(
                server, username=user, password=password, known_hosts=None
            )
            await self.crstorage.insert_auth_server(server, password)
            logging.info(
                f"Successfully connected to '{server}' and cached the new credentials."
            )
            return self.connection, False
        except asyncssh.ProcessError:
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

    async def execute_command_with_log(self, command):
        """Execute command on SSH with real-time logging of stdout and stderr."""
        logging.info(f"Executing command: {command}")
        try:
            async with self.connection.create_process(command) as process:
                async for line in process.stdout:
                    logging.info(line.strip())
                async for line in process.stderr:
                    logging.error(line.strip())

                await process.wait()
                exit_status = process.returncode

                if exit_status == 0:
                    logging.info(f"Command '{command}' executed successfully.")
                else:
                    logging.error(
                        f"Command '{command}' failed with exit status: {exit_status}"
                    )
                return exit_status

        except Exception as e:
            logging.error(f"An error occurred while executing command '{command}': {e}")
            return

    async def execute_command(self, command):
        """Execute command on SSH and return the output."""
        logging.info(f"Executing command: {command}")
        try:
            result = await self.connection.run(command, check=True)
            logging.info(f"Command '{command}' executed successfully.")
            return result.stdout.strip()
        except asyncssh.ProcessError as e:
            logging.error(f"Command '{command}' failed with error: {e.stderr.strip()}")
            return e.stderr.strip()
        except Exception as e:
            logging.error(f"An error occurred while executing command '{command}': {e}")
            return str(e)

    async def copy_file(self, local_file, remote_file):
        if not self.connection:
            logging.error("No active SSH connection found. Cannot proceed with file transfer.")
            return

        try:
            logging.info(f"Starting file copy: {local_file} to {remote_file} on remote server.")
            await asyncssh.scp(local_file, (self.connection, remote_file))
            logging.info(f"File {local_file} successfully copied to {remote_file} on remote server.")
        except (OSError, asyncssh.Error) as exc:
            logging.error(f"An error occurred while copying the file: {exc}")
