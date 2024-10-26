import toml

from src.deployment.conf.conf_classes import DeployConfig, VPSConfig, SSHConfig, FolderConfig
from src.utils.path_manager import PathManager


class ConfigLoaderDeploy():
    def load_config(self, toml_file: str = PathManager().root.joinpath("deploy.toml")) -> DeployConfig:
        config_data = toml.load(toml_file)

        vps_data = config_data['app']['deploy']['vps']
        ssh_data = config_data['app']['deploy']['ssh']
        folder_data = config_data['app']['deploy']['folder']

        return DeployConfig(
            vps=VPSConfig(**vps_data),
            ssh=SSHConfig(**ssh_data),
            folder=FolderConfig(**folder_data)
        )
