import logging
import time

import click

logger = logging.getLogger(__name__)


@click.command(help="Data manipulation, cleaning, transformation, and preparation activities before model training")
def preprocess():
    """Data manipulation, cleaning, transformation, and preparation activities before model training"""
    logger.info("Preprocessing started...")
    # wait for 5 seconds to simulate preprocessing
    time.sleep(5)
    logger.info("Preprocessing completed.")
