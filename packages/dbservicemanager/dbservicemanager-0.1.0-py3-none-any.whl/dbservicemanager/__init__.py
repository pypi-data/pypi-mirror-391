from pathlib import Path
from .loader import load_environment, AppConfig
from .client import reset_service_settings_cache


def init_service_env(
    service_name: str = "DEFAULT_SERVICE",
    root_path: Path = None,
    env_file: str = ".env",
    cache_file: str = "remote_env.json",
    force_refresh: bool = False
) -> AppConfig:
    """Load environment and return dynamic AppConfig instance."""
    load_environment(
        service_name=service_name,
        root_path=root_path,
        env_file=env_file,
        cache_file=cache_file,
        force_refresh=force_refresh
    )
    return AppConfig()
