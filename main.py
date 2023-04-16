from aiohttp.web import run_app

from app.core.application import setup_app


def main():
    run_app(setup_app(), port=8080)


if __name__ == "__main__":
    main()
