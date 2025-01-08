import asyncio

import click
from dotenv import load_dotenv

load_dotenv()


def main():
    # from mtmai.cli.build import register_build_commands
    # from mtmai.cli.clean import register_clean_commands
    # from mtmai.cli.db import register_db_commands
    # from mtmai.cli.dp import register_deploy_commands
    # from mtmai.cli.gen import register_gen_commands
    # from mtmai.cli.init import register_init_commands
    # from mtmai.cli.release import register_release_commands
    # from mtmai.cli.selenium import register_selenium_commands

    @click.group()
    def cli():
        pass

    @cli.command()
    def serve():
        from mtmai.core.config import settings
        from mtmai.core.logging import get_logger
        from mtmai.server import serve

        logger = get_logger()
        logger.info("🚀 call serve : %s:%s", settings.HOSTNAME, settings.PORT)
        asyncio.run(serve())

    @cli.command()
    @click.option("--url", required=False)
    def worker(url):
        from mtmai.worker import WorkerApp

        worker_app = WorkerApp(url)
        asyncio.run(worker_app.deploy_mtmai_workers(url))

    @cli.command()
    @click.option("--url", required=False)
    def worker2(url):
        from mtmai.worker import WorkerApp

        worker_app = WorkerApp(url)
        asyncio.run(worker_app.deploy_mtmai_workers(url))

    cli()


if __name__ == "__main__":
    main()
