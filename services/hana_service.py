import logging
from typing import Dict
from hana_ml.dataframe import ConnectionContext
from config.config import Config
from contextlib import contextmanager
from functools import lru_cache, wraps
import time

# Configure logging
logger = logging.getLogger(__name__)

# Debugging environment variables
# print("HANA_ADDRESS:", Config.HANA_ADDRESS)
# print("HANA_PORT:", Config.HANA_PORT)
# print("HANA_USER:", Config.HANA_USER)
# print("HANA_PASSWORD:", Config.HANA_PASSWORD)
# print("HANA_SCHEMA:", os.getenv("HANA_SCHEMA"))
# print("HANA_ENCRYPT:", os.getenv("HANA_ENCRYPT"))
# print("HANA_SSL_VALIDATE_CERT:", os.getenv("HANA_SSL_VALIDATE_CERT"))


def get_hana_connection():
    """Establish connection to HANA database."""
    try:
        logger.info("Attempting to establish HANA connection...")
        address = Config.HANA_ADDRESS
        port = Config.HANA_PORT
        user = Config.HANA_USER
        password = Config.HANA_PASSWORD
        encrypt = Config.HANA_ENCRYPT
        ssl_validate_certificate = Config.HANA_SSL_VALIDATE_CERT

        logger.debug(f"Connecting to HANA at {address}:{port} with user {user}")
        logger.debug(
            f"SSL settings - encrypt: {encrypt}, validate_cert: {ssl_validate_certificate}"
        )
        connection = ConnectionContext(
            address=address,
            port=port,
            user=user,
            password=password,
            encrypt=encrypt,
            ssl_validate_certificate=ssl_validate_certificate,
        )

        logger.info("HANA connection established successfully")
        return connection

    except ValueError as e:
        logger.error(
            f"Configuration error while establishing HANA connection: {str(e)}"
        )
        raise RuntimeError(f"Configuration error: {str(e)}")
    except Exception as e:
        logger.error(
            f"Unexpected error while establishing HANA connection: {str(e)}",
            exc_info=True,
        )
        raise RuntimeError(f"Failed to establish HANA connection: {str(e)}")


def test_hana_connection():
    """Test HANA connection and return status."""
    try:
        logger.info("Testing HANA connection...")
        conn = get_hana_connection()
        version = conn.hana_version()
        logger.info(f"Successfully connected to HANA version: {version}")
        return {"status": "connected", "hana_version": version}
    except Exception as e:
        logger.error(f"HANA connection test failed: {str(e)}", exc_info=True)
        return {"status": "error", "message": str(e)}


@contextmanager
def hana_connection():
    """Context manager for HANA connection."""
    conn = None
    try:
        conn = get_hana_connection()
        yield conn
    finally:
        if conn:
            conn.close()
            logger.debug("HANA connection closed")


def timed_lru_cache(seconds: int, maxsize: int = 128):
    def wrapper_decorator(func):
        func = lru_cache(maxsize=maxsize)(func)
        func.lifetime = seconds
        func.expiration = time.time() + seconds

        @wraps(func)
        def wrapped_func(*args, **kwargs):
            if time.time() > func.expiration:
                func.cache_clear()
                func.expiration = time.time() + func.lifetime
            return func(*args, **kwargs)

        wrapped_func.cache_info = func.cache_info
        wrapped_func.cache_clear = func.cache_clear
        return wrapped_func

    return wrapper_decorator


@timed_lru_cache(seconds=3600, maxsize=1)  # Cache for 1 hour
def fetch_countries(page: int = 1, per_page: int = 100) -> Dict[str, any]:
    """
    Fetch countries with pagination support and caching.
    Args:
        page: Page number (default: 1)
        per_page: Number of items per page (default: 100)
    """
    table_name = "SAP_COMMON_COUNTRIES"
    schema = Config.HANA_SCHEMA

    try:
        with hana_connection() as conn:
            logger.info(f"Fetching countries from {schema}.{table_name}")

            # Create DataFrame with pagination
            df = conn.table(table_name, schema=schema).select("NAME", "DESCR", "CODE")
            total_count = len(df.collect())

            # Apply pagination
            start_idx = (page - 1) * per_page
            df = df.head(start_idx + per_page).tail(per_page)

            # Collect and transform results
            result_df = df.collect()
            countries = [
                {"name": row["NAME"], "description": row["DESCR"], "code": row["CODE"]}
                for row in result_df.to_dict(orient="records")
            ]

            return {
                "data": countries,
                "pagination": {
                    "page": page,
                    "per_page": per_page,
                    "total_count": total_count,
                    "total_pages": (total_count + per_page - 1) // per_page,
                },
            }

    except Exception as e:
        logger.error(f"Error fetching countries: {str(e)}", exc_info=True)
        raise RuntimeError(f"Failed to fetch countries: {str(e)}")


def create_country(country_data: Dict[str, str]) -> Dict[str, any]:
    """Create a new country record."""
    table_name = "SAP_COMMON_COUNTRIES"
    schema = Config.HANA_SCHEMA

    try:
        with hana_connection() as conn:
            # Validate required fields
            required_fields = ["NAME", "DESCR", "CODE"]
            if not all(
                field.upper() in map(str.upper, country_data.keys())
                for field in required_fields
            ):
                raise ValueError("Missing required fields: NAME, DESCR, CODE")

            # Execute insert using SQL
            insert_sql = f"""
                INSERT INTO {schema}.{table_name} (NAME, DESCR, CODE) 
                VALUES ('{country_data["NAME"]}', '{country_data["DESCR"]}', '{country_data["CODE"]}')
            """
            logger.debug(f"Executing SQL: {insert_sql}")
            cursor = conn.connection.cursor()
            cursor.execute(insert_sql)

            return {"status": "success", "message": "Country created successfully"}
    except Exception as e:
        logger.error(f"Error creating country: {str(e)}", exc_info=True)
        raise RuntimeError(f"Failed to create country: {str(e)}")


def update_country(code: str, country_data: Dict[str, str]) -> Dict[str, any]:
    """Update an existing country record."""
    table_name = "SAP_COMMON_COUNTRIES"
    schema = Config.HANA_SCHEMA

    try:
        with hana_connection() as conn:
            # Prepare update statement
            update_cols = []
            update_vals = []
            for key, value in country_data.items():
                if key.upper() in ["NAME", "DESCR"]:
                    update_cols.append(key)
                    update_vals.append(value)

            if not update_cols:
                raise ValueError("No valid columns to update")

            # Execute update using SQL
            update_sql = f"""
                UPDATE {schema}.{table_name} 
                SET {", ".join(f"{col} = '{val}'" for col, val in zip(update_cols, update_vals))}
                WHERE CODE = '{code}'
            """
            logger.debug(f"Executing SQL: {update_sql}")
            cursor = conn.connection.cursor()
            cursor.execute(update_sql)

            return {"status": "success", "message": "Country updated successfully"}
    except Exception as e:
        logger.error(f"Error updating country: {str(e)}", exc_info=True)
        raise RuntimeError(f"Failed to update country: {str(e)}")


def delete_country(code: str) -> Dict[str, any]:
    """Delete a country record."""
    table_name = "SAP_COMMON_COUNTRIES"
    schema = Config.HANA_SCHEMA

    try:
        with hana_connection() as conn:
            # Execute delete using SQL
            delete_sql = f"""
                DELETE FROM {schema}.{table_name} 
                WHERE CODE = '{code}'
            """
            logger.debug(f"Executing SQL: {delete_sql}")
            cursor = conn.connection.cursor()
            cursor.execute(delete_sql)

            return {"status": "success", "message": "Country deleted successfully"}
    except Exception as e:
        logger.error(f"Error deleting country: {str(e)}", exc_info=True)
        raise RuntimeError(f"Failed to delete country: {str(e)}")
