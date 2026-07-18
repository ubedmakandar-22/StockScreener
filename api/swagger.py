"""Swagger/OpenAPI configuration."""

from flask import Blueprint
from flask_restx import Api, Namespace, fields, Resource
from typing import Any

# Create blueprint
swagger_bp = Blueprint("swagger", __name__)

# API documentation
api = Api(
    swagger_bp,
    title="NSE Stock Scanner API",
    version="1.0.0",
    description="REST API for scanning NSE stocks with technical indicators",
    doc="/docs",
    prefix="/api/v1",
)

# Namespaces
health_ns = Namespace(
    "health", description="Health check endpoints"
)
scanner_ns = Namespace(
    "scan", description="Stock scanning endpoints"
)

# Models for Swagger documentation
indicators_model = api.model(
    "Indicators",
    {
        "symbol": fields.String(required=True, description="Stock symbol"),
        "ema10": fields.Float(description="10-day EMA"),
        "ema20": fields.Float(description="20-day EMA"),
        "ema50": fields.Float(description="50-day EMA"),
        "ema200": fields.Float(description="200-day EMA"),
        "rsi": fields.Float(description="RSI (14)"),
        "average_volume": fields.Float(description="Average volume"),
        "volume_ratio": fields.Float(description="Volume ratio"),
        "high_52w": fields.Float(description="52-week high"),
        "distance_from_52w_high": fields.Float(
            description="Distance from 52-week high (%)"
        ),
    },
)

scan_result_model = api.model(
    "ScanResult",
    {
        "symbol": fields.String(required=True, description="Stock symbol"),
        "price": fields.Float(required=True, description="Current price"),
        "daily": fields.Boolean(description="Daily scanner result"),
        "weekly": fields.Boolean(description="Weekly scanner result"),
        "monthly": fields.Boolean(description="Monthly scanner result"),
        "indicators": fields.Nested(indicators_model),
        "error": fields.String(description="Error message if any"),
    },
)

health_response_model = api.model(
    "HealthResponse",
    {
        "status": fields.String(required=True, description="Health status"),
        "timestamp": fields.String(description="Timestamp"),
    },
)

api_response_model = api.model(
    "APIResponse",
    {
        "status": fields.String(required=True, description="Response status"),
        "data": fields.List(fields.Nested(scan_result_model)),
        "count": fields.Integer(description="Number of results"),
        "error": fields.String(description="Error message if any"),
    },
)

# Add namespaces
api.add_namespace(health_ns, path="/health")
api.add_namespace(scanner_ns, path="/scan")
