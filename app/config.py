import os


def get_database_url() -> str:
    return os.getenv("DATABASE_URL", "sqlite:///./dominios.db")


def get_api_timeout() -> float:
    try:
        return float(os.getenv("API_TIMEOUT", "6"))
    except ValueError:
        return 6.0


def get_log_dir() -> str:
    return os.getenv("LOG_DIR", "logs")


def get_vt_api_key() -> str | None:
    return os.getenv("API_KEY_VT")


def get_urlscan_api_key() -> str | None:
    return os.getenv("API_URLSCAN")
