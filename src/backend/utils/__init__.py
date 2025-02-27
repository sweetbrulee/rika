from functools import cache
import os
import pyshorteners


@cache
def dev_mode() -> bool:
    return os.getenv("RIKA_MODE") == "dev"


shorten_url_service_candidates = [pyshorteners.Shortener().tinyurl.short]


def shorten_url(url):
    for service in shorten_url_service_candidates:
        try:
            short = service(url)
            return short
        except Exception as e:
            print(f"Failed to shorten URL using {service.__name__}.", e)

    raise Exception("Failed to shorten URL using any service.")
