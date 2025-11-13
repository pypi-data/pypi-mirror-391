import logging
import time

import click

logger = logging.getLogger(__name__)


@click.command(help="Quantize your dataset for better performance.")
def quantize():
    """Quantize your dataset for better performance."""
    logger.info("Quantization started...")
    # wait for 5 seconds to simulate quantization
    time.sleep(5)
    logger.info("Quantization completed.")
