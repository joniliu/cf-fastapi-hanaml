import os
from dotenv import load_dotenv
from cfenv import AppEnv

# Load .env file for local development
load_dotenv()

# Initialize Cloud Foundry environment
env = AppEnv()


class Config:
    # Try to get HANA credentials from Cloud Foundry first
    try:
        hana_service = env.get_service(label="hana")
        HANA_ADDRESS = hana_service.credentials.get("host")
        HANA_PORT = int(hana_service.credentials.get("port", 443))
        HANA_USER = hana_service.credentials.get("user")
        HANA_PASSWORD = hana_service.credentials.get("password")
        HANA_SCHEMA = hana_service.credentials.get("schema")
        # In CF, we always want to encrypt and validate certs
        HANA_ENCRYPT = True
        HANA_SSL_VALIDATE_CERT = True
    except (Exception, AttributeError):
        # Fallback to environment variables for local development
        HANA_ADDRESS = os.getenv("HANA_ADDRESS")
        HANA_PORT = int(os.getenv("HANA_PORT", 443))
        HANA_USER = os.getenv("HANA_USER")
        HANA_PASSWORD = os.getenv("HANA_PASSWORD")
        HANA_SCHEMA = os.getenv("HANA_SCHEMA")
        HANA_ENCRYPT = os.getenv("HANA_ENCRYPT", "True").lower() == "true"
        HANA_SSL_VALIDATE_CERT = (
            os.getenv("HANA_SSL_VALIDATE_CERT", "True").lower() == "true"
        )
