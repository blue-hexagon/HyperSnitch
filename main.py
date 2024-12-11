import os
import platform
import sys

from src.utils.logger import ConsoleLogger

if __name__ == '__main__':
    logger = ConsoleLogger().logger
    if platform.system() == "Windows":
        """ Delpoyment on a Windows client """
        from src.deployment.controller.resource_controller import DeploymentController
        logger.info("Running DeploymentController on Windows")
        DeploymentController()
    else:
        """ Running on Linux server """
        # Extensive diagnostic logging
        logger.info("Starting application")
        logger.debug(f"Current working directory: {os.getcwd()}")
        logger.debug(f"Python executable: {sys.executable}")
        logger.debug(f"Python path: {sys.path}")
        logger.debug(f"Environment variables: {os.environ}")
        from src.main.controller.executor import Executor
        Executor.run()
