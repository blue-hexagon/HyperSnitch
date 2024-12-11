import toml

from src.deployment.conf.conf_classes import DeployConfig, VPSConfig, SSHConfig, FolderConfig, DomainConfig
from src.utils.path_manager import PathManager


class ConfigLoaderDeploy():
    def load_config(self, toml_file: str = PathManager().root.joinpath("deploy.toml")) -> DeployConfig:
        config_data = toml.load(toml_file)

        vps_data = config_data['app']['deploy']['vps']
        ssh_data = config_data['app']['deploy']['ssh']
        folder_data = config_data['app']['deploy']['folder']
        domain_data = config_data['app']['deploy']['domain']


        return DeployConfig(
            vps=VPSConfig(**vps_data),
            ssh=SSHConfig(**ssh_data),
            folder=FolderConfig(**folder_data),
            domain=DomainConfig(**domain_data)
        )
