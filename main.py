import platform


from src.utils.logger import ConsoleLogger

if __name__ == '__main__':
    logger = ConsoleLogger().logger
    if platform.system() == "Windows":
        from src.deployment.controller.resource_controller import DeploymentController
        logger.info("Running DeploymentController on Windows")
        DeploymentController()
    else:
        from src.main.controller.executor import Executor
        logger.info("Running ExecutionController on Linux")
        Executor.run_scraper()
