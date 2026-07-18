"""Flask application factory."""

import logging
import os
from flask import Flask
from flask_cors import CORS

from config import get_config, Config
from utils.logger import LoggerSetup
from api.routes import init_routes


def create_app(env: str = "production") -> Flask:
    """
    Create and configure Flask application.

    Args:
        env: Environment ('development', 'testing', 'production').

    Returns:
        Configured Flask app.
    """
    # Get configuration
    config = get_config(env)

    # Setup logging
    LoggerSetup.setup_logger("stock_scanner", config)
    logger = logging.getLogger(__name__)

    # Create Flask app
    app = Flask(__name__)
    app.config.from_object(config)

    # Enable CORS
    CORS(app)

    # Initialize routes
    init_routes(app, config)

    logger.info(f"Stock Scanner API initialized in {env} mode")

    return app
