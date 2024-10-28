import os
import logging
from .remotexec import RemoteEXec

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)


class RemoteRequire(RemoteEXec):
    def __init__(self) -> None:
        super().__init__()

    async def which_pkg(self, pkg: str) -> str:
        if self.connection is None:
            logging.warning("Transport is not connected")
        logging.info(f"Checking location of package '{pkg}'")
        result = await self.execute_command("which %s" % pkg)
        if result:
            logging.info(f"Package '{pkg}' is located at: {result}")
        else:
            logging.warning(f"Package '{pkg}' not found on system")
        return result

    async def pip_version(self) -> int:
        if self.connection is None:
            logging.warning("Transport is not connected")
        return_code = await self.execute_command_with_log("pip --version")
        if return_code == 0:
            logging.info("Pip is already installed and operational")
        else:
            logging.warning("Pip is not installed or version check failed")
        return return_code

    async def installed_pip(self) -> int:
        if self.connection is None:
            logging.warning("Transport is not connected")
        return_code = await self.execute_command_with_log("sudo apt install python3-pip -y")
        if return_code == 0:
            logging.info("Successfully installed pip")
        else:
            logging.error("Failed to install pip")
        return return_code

    async def install_pipreqs(self):
        if self.connection is None:
            logging.warning("Transport is not connected")
        path_package = await self.which_pkg("pip")
        return_code = await self.execute_command_with_log(
            "%s install pipreqs" % (path_package)
        )
        if return_code == 0:
            logging.info("Successfully installed package pipreqs")
        else:
            logging.error("Failed to install pipreqs")
        return return_code

    async def get_requirements_package(self, directory):
        if self.connection is None:
            logging.warning("Transport is not connected")
        path_package = await self.which_pkg("pipreqs")
        return_code = await self.execute_command_with_log(
            "%s %s" % (path_package, directory)
        )
        if return_code == 0:
            requirements_file = os.path.join(directory, "requirements.txt")
            logging.info("Successfully get requirements package")
        else:
            logging.error("Failed to get requirements package")
        return requirements_file

    async def installed_pip_package(self, requirements_file: str):
        if self.connection is None:
            logging.warning("Transport is not connected")
        path_package = await self.which_pkg("pip")
        return_code = await self.execute_command_with_log(
            "%s install -r %s" % (path_package, requirements_file)
        )
        if return_code == 0:
            logging.info(f"Successfully installed packages in {requirements_file}")
        else:
            logging.error(f"Failed to install packages in {requirements_file}")
        return return_code

    async def status_directory(self, directory: str) -> str:
        if self.connection is None:
            logging.warning("Transport is not connected")
        result = await self.execute_command(
            f'bash -c \'if [ -d "{directory}" ]; then echo "exists"; else echo "not_exists"; fi\''
        )
        logging.info(f"Directory status: {result.strip()}")
        return result

    async def create_directory(self, directory: str) -> str:
        if self.connection is None:
            logging.warning("Transport is not connected")
        result = await self.execute_command(f"mkdir -p {directory}")
        if result:
            logging.info(f"Successfully created directory: {directory}")
        else:
            logging.error(f"Failed to create directory: {directory}")
        return result

    async def added_env(self, version: str):
        if self.connection is None:
            logging.warning("Transport is not connected")
        logging.info(
            f"Adding environment variable CHECKER_VERSION with value: {version}"
        )
        result = await self.execute_command(
            f"echo 'export CHECKER_VERSION=\"{version}\"' | sudo tee -a /root/.bashrc"
        )
        if result:
            logging.info(
                f"Successfully added environment variable CHECKER_VERSION={version}"
            )
        else:
            logging.error("Failed to add environment variable")
        return result

    async def pip_is_installed(self):
        if self.connection is None:
            logging.warning("Transport is not connected")
        if await self.pip_version() != 0:
            logging.info("Pip is not installed, attempting installation")
            if await self.installed_pip() == 0:
                logging.info("Pip successfully installed")
            else:
                logging.error("Failed to install pip")
        else:
            logging.info("Pip is already installed")

    async def pip_package(self, directory: str):
        if self.connection is None:
            logging.warning("Transport is not connected")
        await self.install_pipreqs()
        requirements_package = await self.get_requirements_package(directory)
        if await self.installed_pip_package(requirements_package) == 0:
            logging.info("Successfully installed missing packages")
        else:
            logging.error(f"Failed to install missing packages")

    async def dir_is_exists(self, directory: str):
        if self.connection is None:
            logging.warning("Transport is not connected")
        if await self.status_directory(directory) == "not_exists":
            logging.info(f"Directory '{directory}' does not exist, creating it")
            await self.create_directory(directory)
        else:
            logging.info(f"Directory '{directory}' already exists")

    async def execute_tools(self, file: str, **action):
        action_type = action.get("action", None)
        if self.connection is None:
            logging.warning("Transport is not connected")
        if not action_type:
            logging.error("Action argument empty")
            return
        command = f"{await self.which_pkg('python3')} {file} --action {action_type}"
        result = await self.execute_command(command)
        return result
