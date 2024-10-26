import sys
from time import sleep

from src.conf.conf_parser import ConfigLoader
from src.conf.path_manager import PathManager
import paramiko
from src.main.utils.deploy import DOProvider
from src.main.utils.logger import ConsoleLogger
from src.main.utils.ssh_utils import SshUtils

if __name__ == '__main__':
    logger = ConsoleLogger()

    DOProvider.delete_ssh_key("WebSnitchSshKey")
    DOProvider.destroy_vps("websnitch")
    sutils = SshUtils(keyfile_name="id_rsa", passphrase="rootroot")
    sutils.create_ssh_key_pair(key_bits=4096)
    pub_key = sutils.read_public_key()

    DOProvider().add_ssh_key("WebSnitchSshKey", pub_key)
    ssh_key_fingerprints = DOProvider().get_ssh_key_fingerprints_from_names(["WebSnitchSshKey"])
    droplet_ip = DOProvider().create_vps(droplet_name="websnitch",
                                         api_slug="s-1vcpu-512mb-10gb",
                                         image="debian-12-x64",
                                         count=1,
                                         tag=["websnitch"],
                                         ssh_keys=ssh_key_fingerprints,
                                         region="fra1")

    username = 'root'
    private_key_path = PathManager().root.joinpath(".ssh/id_rsa")
    repo_url = 'https://github.com/blue-hexagon/HyperSnitch.git'
    app_directory = '$HOME/hypersnitch'

    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    retries = 10
    while True:
        try:
            private_key = paramiko.RSAKey.from_private_key_file(private_key_path, password="rootroot")
            ssh.connect(droplet_ip, username=username, pkey=private_key)
            logger.info("Successfully connected to the server.")
            break
        except Exception as e:
            logger.warning(f"Failed to connect to the server: {e}")
            retries -= 1
            if retries == 0:
                sys.exit(1)
            sleep(5)
    conf = ConfigLoader().load_config(with_env=True)
    env_confs = []
    env_confs.append(("api_key", conf.digital_ocean.api_key))
    env_confs.append(("smtp_username", conf.smtp.smtp_username))
    env_confs.append(("smtp_password", conf.smtp.smtp_password))
    env_confs.append(("smtp_server", conf.smtp.smtp_server))
    env_confs.append(("smtp_port", conf.smtp.smtp_port))
    env_confs.append(("sender", conf.smtp.sender))
    env_confs.append(("recipients", conf.smtp.recipients))
    commands = [
        "apt-get update",
        "export DEBIAN_FRONTEND=noninteractive",
        *[f'echo "export {env[0]}={env[1]}" >> $HOME/.bashrc' for env in env_confs],
        "apt-get install -y git",
        "curl -sSL https://install.python-poetry.org | python3 -",
        """echo 'export PATH="$HOME/.local/bin:$PATH"' >> .bashrc """,
        "source $HOME/.bashrc",
        f"git clone {repo_url} {app_directory}",
        f"cd {app_directory} && poetry install",
        f"cd {app_directory} && poetry run playwright install-deps",
        f"cd {app_directory} && poetry run playwright install",
        f"cd {app_directory} && poetry run python main.py",
    ]

    for command in commands:
        while True:
            stdin, stdout, stderr = ssh.exec_command(command)
            logger.info(f"Executing command: {command}")

            output = stdout.read().decode()
            error = stderr.read().decode()
            if "ould not get lock" in error:
                # Happends when Debian is still initializing and trying to use package manager to install git
                logger.info("Failed to get lock")
                sleep(5)
                continue
            if error:
                logger.error(f"Error: {error}")
            if len(output) == 0:
                # Silent command like `export
                break
            if output:
                logger.info(f"Output: {output}")
                break

    ssh.close()
