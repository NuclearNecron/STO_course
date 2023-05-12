import asyncio
import os
from asyncio import Runner

from aiohttp.web import AppRunner, TCPSite

from app.core.application import setup_app


async def main():
    app_runner = AppRunner(
        setup_app(
            config_path=os.path.join(
                os.path.dirname(os.path.realpath(__file__)), "config.yml"
            ),
            redis_connect_on_startup=True,
            gRPC_serve_on_startup=True,
        )
    )
    await app_runner.setup()
    site = TCPSite(app_runner, "localhost", 8080)
    await site.start()
    # wait for finish signal
    # await app_runner.cleanup()
    await asyncio.Event().wait()


if __name__ == "__main__":
    runner: Runner
    with asyncio.Runner() as runner:
        runner.run(main())
