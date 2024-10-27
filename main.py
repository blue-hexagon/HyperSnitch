import platform

from src.deployment.controller.resource_controller import DeploymentController
from src.main.controller.executor import Executor

if __name__ == '__main__':
    if platform.system() == "Windows":
        DeploymentController()
    else:
        Executor.run_scraper()
