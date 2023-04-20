import os

from aiohttp.web import run_app

from app.core.application import setup_app


def main():
    run_app(
        setup_app(
            config_path=os.path.join(
                os.path.dirname(os.path.realpath(__file__)), "config.yml"
            )
        ),
        port=8080,
    )


if __name__ == "__main__":
    main()
