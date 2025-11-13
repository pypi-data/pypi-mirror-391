import requests
import time
from typing import Dict
from threading import Lock

_cached_settings: Dict[str, Dict[str, str]] = {}
_last_fetch_times: Dict[str, float] = {}
_cache_lock = Lock()


def get_service_settings(service_name: str = "DEFAULT_SERVICE", force_refresh: bool = False) -> Dict[str, str]:
    """Fetch and cache service settings from a remote API."""
    with _cache_lock:
        if not force_refresh and service_name in _cached_settings:
            return _cached_settings[service_name].copy()

    url = "https://servicemanagementdevapi.carevance.solutions/api/ServiceParameter/service-parameter-by-service-name"
    params = {"serviceName": service_name}

    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()

        if data and "settings" in data and isinstance(data["settings"], list):
            setting_dict = {item["key"]: item["value"]
                            for item in data["settings"] if "key" in item and "value" in item}
            with _cache_lock:
                _cached_settings[service_name] = setting_dict.copy()
                _last_fetch_times[service_name] = time.time()
            return setting_dict
        else:
            return _cached_settings.get(service_name, {}).copy()

    except requests.exceptions.RequestException as e:
        print(f"❌ Error fetching service settings: {e}")
        return _cached_settings.get(service_name, {}).copy()


def reset_service_settings_cache(service_name: str = "DEFAULT_SERVICE") -> Dict[str, str]:
    """Reset cache and force fresh fetch."""
    with _cache_lock:
        _cached_settings.pop(service_name, None)
        _last_fetch_times.pop(service_name, None)
    return get_service_settings(service_name=service_name, force_refresh=True)
