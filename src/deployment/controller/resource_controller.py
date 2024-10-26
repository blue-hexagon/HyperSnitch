import sys
from time import sleep

import paramiko
from src.deployment.controller.api_wrapper import DOProvider
from src.deployment.conf.conf_loader import ConfigLoaderDeploy
from src.main.conf.conf_parser import ConfigLoader
from src.utils.logger import ConsoleLogger
from src.deployment.utils.ssh_utils import SshUtils
from src.utils.path_manager import PathManager


class DeploymentController:
    def __init__(self):
        # Initialize
        logger = ConsoleLogger()
        config = ConfigLoaderDeploy().load_config()

        # Delete existing resources
        DOProvider.delete_ssh_key(config.ssh.pubkey_remote_name)
        DOProvider.destroy_vps(config.vps.tags)

        # Create and upload SSH key
        sutils = SshUtils(keyfile_name=config.ssh.keyfile_name, passphrase=config.ssh.passphrase)
        sutils.create_ssh_key_pair(key_bits=config.ssh.key_bits)
        pub_key = sutils.read_public_key()
        DOProvider().add_ssh_key(config.ssh.pubkey_remote_name, pub_key)

        # Get SSH key fingerprint and create VPS
        ssh_key_fingerprints = DOProvider().get_ssh_key_fingerprints_from_names([config.ssh.pubkey_remote_name])
        droplet_ip = DOProvider().create_vps(droplet_name=config.vps.vps_name, api_slug=config.vps.api_slug, image=config.vps.image,
                                             count=config.vps.count, tag=config.vps.tags, ssh_keys=ssh_key_fingerprints,
                                             region=config.vps.region)

        # Setup Paramiko
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        retries = 10
        while True:
            try:
                # Connect with Paramiko
                private_key = paramiko.RSAKey.from_private_key_file(
                    PathManager().root.joinpath(".ssh/id_rsa"),
                    password=config.ssh.passphrase
                )
                ssh.connect(droplet_ip, username='root', pkey=private_key)
                logger.info("Successfully connected to the server.")
                break
            except Exception as e:
                logger.warning(f"Failed to connect to the server: {e}")
                retries -= 1
                if retries == 0:
                    sys.exit(1)
                sleep(5)

        # Setup commands
        conf = ConfigLoader().load_config(with_env=True)
        env_confs = [("api_key", conf.digital_ocean.api_key),
                     ("smtp_username", conf.smtp.smtp_username),
                     ("smtp_password", conf.smtp.smtp_password),
                     ("smtp_server", conf.smtp.smtp_server),
                     ("smtp_port", conf.smtp.smtp_port),
                     ("sender", conf.smtp.sender),
                     ("recipients", conf.smtp.recipients),
                     ("DEBIAN_FRONTEND", "noninteractive")]

        app_directory = '~/hypersnitch'

        commands = [
            "echo 'debconf debconf/frontend select Noninteractive' | sudo debconf-set-selections",
            *[f'echo "export {env[0]}={env[1]}" >> ~/.bashrc' for env in env_confs],
            "apt-get install -y git",
            "curl -sSL https://install.python-poetry.org | python3 -",
            """echo 'export PATH="~/.local/bin:$PATH"' >> .bashrc """,
            "source ~/.bashrc",
            f"git clone 'https://github.com/blue-hexagon/HyperSnitch.git' {app_directory}",
            f"cd {app_directory} && poetry install",
            f"cd {app_directory} && poetry run playwright install-deps",
            f"cd {app_directory} && poetry run playwright install",
            f"cd {app_directory} && chmod a+x *",
            f"cp {app_directory}/src/deployment/systemd/hypersnitch.service /etc/systemd/system/hypersnitch.service",
            f"systemctl daemon-reload",
            f"sudo systemctl enable hypersnitch.service",
            f"sudo systemctl start hypersnitch.service"
        ]

        # Execute commands
        for cmd in commands:
            while True:
                stdin, stdout, stderr = ssh.exec_command(cmd)
                logger.info(f"Executing command: {cmd}")

                output = stdout.read().decode()
                error = stderr.read().decode()
                if "ould not get lock" in error:
                    # Happends when Debian is still initializing and trying to use package manager to install git
                    logger.info("Failed to get lock")
                    sleep(5)
                    continue
                if error:
                    logger.error(f"Error while executing command '{cmd}': {error.strip()}")
                if len(output) == 0:
                    # Silent command like `export
                    break
                if output:
                    logger.info(f"Output: {output.strip()}")
                    break
        ssh.close()
