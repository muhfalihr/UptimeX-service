import os
import logging

from .remotexec import RemoteEXec
from typing import List, Any

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)


class RemoteRequire(RemoteEXec):
    def __init__(self) -> None:
        super().__init__()

    def which_pkg(self, pkg: str) -> str:
        if self.transport is None or not self.transport.is_active():
            logging.warning("Transport is not connected")
        logging.info(f"Checking location of package '{pkg}'")
        result = self.execute_command("which %s" % pkg)
        if result:
            logging.info(f"Package '{pkg}' is located at: {result}")
        else:
            logging.warning(f"Package '{pkg}' not found on system")
        return result

    def pip_version(self) -> int:
        if self.transport is None or not self.transport.is_active():
            logging.warning("Transport is not connected")
        return_code = self.execute_command_with_log("pip --version")
        if return_code == 0:
            logging.info("Pip is already installed and operational")
        else:
            logging.warning("Pip is not installed or version check failed")
        return return_code

    def installed_pip(self) -> int:
        if self.transport is None or not self.transport.is_active():
            logging.warning("Transport is not connected")
        return_code = self.execute_command_with_log("sudo apt install python3-pip -y")
        if return_code == 0:
            logging.info("Successfully installed pip")
        else:
            logging.error("Failed to install pip")
        return return_code

    def install_pipreqs(self):
        if self.transport is None or not self.transport.is_active():
            logging.warning("Transport is not connected")
        return_code = self.execute_command_with_log(
            "%s install pipreqs" % (self.which_pkg("pip"))
        )
        if return_code == 0:
            logging.info("Successfully installed package pipreqs")
        else:
            logging.error("Failed to install pipreqs")
        return return_code

    def get_requirements_package(self, directory):
        if self.transport is None or not self.transport.is_active():
            logging.warning("Transport is not connected")
        return_code = self.execute_command_with_log(
            "%s %s" % (self.which_pkg("pipreqs"), directory)
        )
        if return_code == 0:
            requirements_file = os.path.join(directory, "requirements.txt")
            logging.info("Successfully get requirements package")
        else:
            logging.error("Failed to get requirements package")
        return requirements_file

    def installed_pip_package(self, requirements_file: str):
        if self.transport is None or not self.transport.is_active():
            logging.warning("Transport is not connected")
        return_code = self.execute_command_with_log(
            "%s install -r %s" % (self.which_pkg("pip"), requirements_file)
        )
        if return_code == 0:
            logging.info(f"Successfully installed packages in {requirements_file}")
        else:
            logging.error(f"Failed to install packages in {requirements_file}")
        return return_code

    def status_directory(self, directory: str) -> str:
        if self.transport is None or not self.transport.is_active():
            logging.warning("Transport is not connected")
        result = self.execute_command(
            f'if [ -d "{directory}" ]; then echo "exists"; else echo "not_exists"; fi'
        )
        logging.info(f"Directory status: {result.strip()}")
        return result

    def create_directory(self, directory: str) -> str:
        if self.transport is None or not self.transport.is_active():
            logging.warning("Transport is not connected")
        result = self.execute_command(f"mkdir -p {directory}")
        if result:
            logging.info(f"Successfully created directory: {directory}")
        else:
            logging.error(f"Failed to create directory: {directory}")
        return result

    def added_env(self, version: str):
        if self.transport is None or not self.transport.is_active():
            logging.warning("Transport is not connected")
        logging.info(
            f"Adding environment variable CHECKER_VERSION with value: {version}"
        )
        result = self.execute_command(
            f"echo 'export CHECKER_VERSION=\"{version}\"' | sudo tee -a /root/.bashrc"
        )
        if result:
            logging.info(
                f"Successfully added environment variable CHECKER_VERSION={version}"
            )
        else:
            logging.error("Failed to add environment variable")
        return result

    def pip_is_installed(self):
        if self.transport is None or not self.transport.is_active():
            logging.warning("Transport is not connected")
        if self.pip_version() != 0:
            logging.info("Pip is not installed, attempting installation")
            if self.installed_pip() == 0:
                logging.info("Pip successfully installed")
            else:
                logging.error("Failed to install pip")
        else:
            logging.info("Pip is already installed")

    def pip_package(self, directory: str):
        if self.transport is None or not self.transport.is_active():
            logging.warning("Transport is not connected")
        self.install_pipreqs()
        if self.installed_pip_package(self.get_requirements_package(directory)) == 0:
            logging.info("Successfully installed missing packages")
        else:
            logging.error(f"Failed to install missing packages")

    def dir_is_exists(self, directory: str):
        if self.transport is None or not self.transport.is_active():
            logging.warning("Transport is not connected")
        if self.status_directory(directory) == "not_exists":
            logging.info(f"Directory '{directory}' does not exist, creating it")
            self.create_directory(directory)
        else:
            logging.info(f"Directory '{directory}' already exists")

    def execute_tools(self, file: str, **action):
        if self.transport is None or not self.transport.is_active():
            logging.warning("Transport is not connected")
        action_type = action.get("action", "detail")
        command = f"{self.which_pkg('python3')} {file} --action {action_type}"
        result = self.execute_command(command)
        return result
