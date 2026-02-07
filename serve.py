import logging

import waitress

import app

if __name__ == "__main__":
    logger = logging.getLogger("waitress")
    logger.setLevel(logging.INFO)
    waitress.serve(app.app, host="localhost", port=8080, threads=4)