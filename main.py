import os
import ssl

from app.web.app import setup_app
from aiohttp.web import run_app

ssl_context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
ssl_context.load_cert_chain(os.path.join(
                os.path.dirname(os.path.realpath(__file__)),"mkcerts", "together+2.pem"),os.path.join(
                os.path.dirname(os.path.realpath(__file__)),"mkcerts", "together+2-key.pem"))


if __name__ == "__main__":
    run_app(

        setup_app(
            config_path=os.path.join(
                os.path.dirname(os.path.realpath(__file__)), "config.yaml"
            )
        ),
        port=8080,
        ssl_context=ssl_context,
        host = "together"    )
