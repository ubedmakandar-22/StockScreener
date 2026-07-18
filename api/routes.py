"""API routes for stock scanner."""

import logging
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Optional

from flask import Blueprint, jsonify, request
from flask_restx import Resource, fields

from config import Config, get_config
from models.stock import APIResponse, ScannerResult
from services.nse_service import NSEService
from services.cache import CacheManager
from scanner.daily import DailyScanner
from scanner.weekly import WeeklyScanner
from scanner.monthly import MonthlyScanner
from api.swagger import api, health_ns, scanner_ns

logger = logging.getLogger(__name__)


class ScannerEngine:
    """Main scanner engine."""

    def __init__(self, config: Config):
        """Initialize scanner engine."""
        self.config = config
        self.nse_service = NSEService(config)
        self.daily_scanner = DailyScanner(config)
        self.weekly_scanner = WeeklyScanner(config)
        self.monthly_scanner = MonthlyScanner(config)
        self.cache = CacheManager(ttl=config.CACHE_TTL)

    def scan_stock(
        self, symbol: str, scan_type: str = "all"
    ) -> Optional[ScannerResult]:
        """
        Scan a single stock.

        Args:
            symbol: Stock symbol.
            scan_type: Type of scan ('daily', 'weekly', 'monthly', 'all').

        Returns:
            ScannerResult or None if failed.
        """
        try:
            # Check cache
            cache_key = f"{symbol}_{scan_type}"
            if self.config.CACHE_ENABLED:
                cached = self.cache.get(cache_key)
                if cached:
                    return cached

            # Fetch data
            df = self.nse_service.get_stock_data(symbol)
            if df is None:
                logger.warning(f"Failed to fetch data for {symbol}")
                return None

            result = ScannerResult(symbol=symbol, price=0.0)

            if scan_type in ["daily", "all"]:
                daily_result = self.daily_scanner.scan(df, symbol)
                result.daily = daily_result.daily
                result.indicators = daily_result.indicators

            if scan_type in ["weekly", "all"]:
                weekly_result = self.weekly_scanner.scan(df, symbol)
                result.weekly = weekly_result.weekly

            if scan_type in ["monthly", "all"]:
                monthly_result = self.monthly_scanner.scan(df, symbol)
                result.monthly = monthly_result.monthly

            result.price = self.nse_service.get_current_price(df) or 0.0

            # Cache result
            if self.config.CACHE_ENABLED:
                self.cache.set(cache_key, result)

            return result

        except Exception as e:
            logger.error(f"Error scanning {symbol}: {e}", exc_info=True)
            return None

    def scan_all(
        self, scan_type: str = "all", limit: Optional[int] = None
    ) -> list[ScannerResult]:
        """
        Scan all NSE stocks.

        Args:
            scan_type: Type of scan ('daily', 'weekly', 'monthly', 'all').
            limit: Limit number of stocks to scan.

        Returns:
            List of ScannerResult objects.
        """
        try:
            logger.info(f"Starting {scan_type} scan")
            symbols = self.nse_service.get_nse_index_symbols()

            if limit:
                symbols = symbols[:limit]

            results = []
            failed = 0

            with ThreadPoolExecutor(
                max_workers=self.config.SCANNER_MAX_WORKERS
            ) as executor:
                futures = {
                    executor.submit(self.scan_stock, symbol, scan_type): symbol
                    for symbol in symbols
                }

                for future in as_completed(futures):
                    try:
                        result = future.result(timeout=self.config.SCANNER_TIMEOUT)
                        if result:
                            results.append(result)
                    except Exception as e:
                        failed += 1
                        logger.error(f"Error processing future: {e}")

            logger.info(
                f"Scan complete: {len(results)} stocks processed, {failed} failed"
            )
            return results

        except Exception as e:
            logger.error(f"Error in scan_all: {e}", exc_info=True)
            return []


# Initialize scanner engine (will be set during app creation)
scanner_engine: Optional[ScannerEngine] = None


# Health endpoints
@health_ns.route("")
class HealthCheck(Resource):
    """Health check endpoint."""

    def get(self):
        """
        GET /api/v1/health

        Returns:
            Health status.
        """
        return jsonify(
            {
                "status": "UP",
                "timestamp": datetime.utcnow().isoformat(),
            }
        )


# Scanner endpoints
@scanner_ns.route("/daily")
class DailyScan(Resource):
    """Daily momentum scan endpoint."""

    def get(self):
        """
        GET /api/v1/scan/daily

        Returns:
            Stocks matching daily momentum conditions.
        """
        if not scanner_engine:
            return jsonify({"status": "error", "error": "Scanner not initialized"}), 500

        limit = request.args.get("limit", type=int, default=None)
        results = scanner_engine.scan_all(scan_type="daily", limit=limit)

        # Filter for daily matches
        daily_matches = [r for r in results if r.daily]

        return jsonify(
            {
                "status": "success",
                "data": [r.to_dict() for r in daily_matches],
                "count": len(daily_matches),
            }
        )


@scanner_ns.route("/weekly")
class WeeklyScan(Resource):
    """Weekly strength scan endpoint."""

    def get(self):
        """
        GET /api/v1/scan/weekly

        Returns:
            Stocks matching weekly strength conditions.
        """
        if not scanner_engine:
            return jsonify({"status": "error", "error": "Scanner not initialized"}), 500

        limit = request.args.get("limit", type=int, default=None)
        results = scanner_engine.scan_all(scan_type="weekly", limit=limit)

        # Filter for weekly matches
        weekly_matches = [r for r in results if r.weekly]

        return jsonify(
            {
                "status": "success",
                "data": [r.to_dict() for r in weekly_matches],
                "count": len(weekly_matches),
            }
        )


@scanner_ns.route("/monthly")
class MonthlyScan(Resource):
    """Monthly trend scan endpoint."""

    def get(self):
        """
        GET /api/v1/scan/monthly

        Returns:
            Stocks matching monthly trend conditions.
        """
        if not scanner_engine:
            return jsonify({"status": "error", "error": "Scanner not initialized"}), 500

        limit = request.args.get("limit", type=int, default=None)
        results = scanner_engine.scan_all(scan_type="monthly", limit=limit)

        # Filter for monthly matches
        monthly_matches = [r for r in results if r.monthly]

        return jsonify(
            {
                "status": "success",
                "data": [r.to_dict() for r in monthly_matches],
                "count": len(monthly_matches),
            }
        )


@scanner_ns.route("/all")
class AllScans(Resource):
    """All scanners endpoint."""

    def get(self):
        """
        GET /api/v1/scan/all

        Returns:
            Stocks matching any scanner condition.
        """
        if not scanner_engine:
            return jsonify({"status": "error", "error": "Scanner not initialized"}), 500

        limit = request.args.get("limit", type=int, default=None)
        results = scanner_engine.scan_all(scan_type="all", limit=limit)

        return jsonify(
            {
                "status": "success",
                "data": [r.to_dict() for r in results],
                "count": len(results),
            }
        )


def init_routes(app, config: Config) -> None:
    """
    Initialize routes and scanner engine.

    Args:
        app: Flask app instance.
        config: Configuration object.
    """
    global scanner_engine
    scanner_engine = ScannerEngine(config)
    app.register_blueprint(swagger_bp)
