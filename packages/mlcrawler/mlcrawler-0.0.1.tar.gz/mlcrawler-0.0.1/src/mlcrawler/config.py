"""Configuration management using Dynaconf for unified config/env/CLI support."""

from pathlib import Path
from typing import List, Optional, Union
from dynaconf import Dynaconf


def create_config(config_files: List[Path], **overrides) -> Dynaconf:
    """Create a Dynaconf configuration instance.

    Args:
        config_files: List of configuration file paths
        **overrides: Additional configuration overrides

    Returns:
        Dynaconf configuration instance
    """
    # Default configuration values
    defaults = {
        "mode": "sitemap",
        "user_agent": "mlcrawler/0.1 (+contact-url)",
        "obey_robots": True,
        "same_domain_only": True,
        "max_depth": 2,
        "seeds": [],
        "limits": {"max_pages": 0},
        "concurrency": {"global": 8, "per_host": 4},
        "rate_limit": {"per_host_delay_ms": 500},
        "cache": {
            "dir": ".cache/mlcrawler",
            "respect_conditional": True,
            "mode": "conditional",
            "ttl_seconds": 3600,  # 1 hour default TTL for entries without proper cache headers
        },
        "output": {"dir": "output", "metadata_backend": "json"},
        "sitemap": {"url": "", "use_lastmod": True},
        "discovery": {
            "follow_links": True,
            "include_patterns": [],
            "exclude_patterns": [],
        },
        "filter": {"dom_remove": ["script", "style", "svg"], "extra_remove": []},
        "extract": {"main_article": False},
        "storage": {"duckdb": {"path": "mlcrawler.duckdb"}},
    }

    # Merge overrides into defaults
    config_data = defaults.copy()
    config_data.update(overrides)

    # Convert file paths to strings for Dynaconf
    settings_files = [str(f) for f in config_files if f.exists()]

    # Create Dynaconf instance
    config = Dynaconf(
        envvar_prefix="MLCRAWLER",
        settings_files=settings_files,
        load_dotenv=True,
        lowercase_read=True,
        **config_data,
    )

    return config


def validate_config(config: Dynaconf) -> None:
    """Validate configuration values.

    Args:
        config: Dynaconf configuration object

    Raises:
        ValueError: If configuration is invalid
    """
    # Validate mode
    mode = getattr(config, "mode", "sitemap")
    if mode not in ["sitemap", "seed"]:
        raise ValueError(f"Invalid mode '{mode}'. Must be 'sitemap' or 'seed'")

    # Validate metadata backend
    output_config = getattr(config, "output", {})
    metadata_backend = getattr(output_config, "metadata_backend", "json")
    if metadata_backend not in ["json", "duckdb"]:
        raise ValueError(
            f"Invalid metadata_backend '{metadata_backend}'. Must be 'json' or 'duckdb'"
        )

    # Mode-specific validation
    seeds = getattr(config, "seeds", [])
    if mode == "seed" and not seeds:
        raise ValueError("Seed mode requires at least one seed URL")

    sitemap_config = getattr(config, "sitemap", {})
    sitemap_url = getattr(sitemap_config, "url", None)

    if mode == "sitemap" and not sitemap_url and not seeds:
        raise ValueError(
            "Sitemap mode requires either sitemap URL or seed URLs for discovery"
        )


# For backward compatibility, create a Config-like interface
class Config:
    """Wrapper to provide a more familiar interface over Dynaconf."""

    def __init__(self, dynaconf_config: Dynaconf):
        self._config = dynaconf_config

    @property
    def mode(self) -> str:
        return str(self._config["mode"])

    @mode.setter
    def mode(self, value: str):
        # Dynaconf doesn't have a simple set method for individual keys
        # We'll handle this through file updates or environment variables
        pass

    @property
    def user_agent(self) -> str:
        return str(self._config["user_agent"])

    @property
    def obey_robots(self) -> bool:
        return bool(self._config["obey_robots"])

    @property
    def same_domain_only(self) -> bool:
        return bool(self._config["same_domain_only"])

    @property
    def max_depth(self) -> int:
        return int(self._config["max_depth"])

    @property
    def seeds(self) -> List[str]:
        return list(self._config["seeds"])

    @seeds.setter
    def seeds(self, value: List[str]):
        # Dynaconf doesn't have a simple set method for individual keys
        # We'll handle this through file updates or environment variables
        pass

    @property
    def limits(self):
        return ConfigSection(self._config["limits"])

    @property
    def concurrency(self):
        return ConfigSection(self._config["concurrency"])

    @property
    def rate_limit(self):
        return ConfigSection(self._config["rate_limit"])

    @property
    def cache(self):
        return ConfigSection(self._config["cache"])

    @property
    def output(self):
        return OutputConfigSection(self._config["output"])

    @property
    def sitemap(self):
        return SitemapConfigSection(self._config["sitemap"])

    @property
    def discovery(self):
        return ConfigSection(self._config["discovery"])

    @property
    def filter(self):
        return ConfigSection(self._config["filter"])

    @property
    def extract(self):
        return ConfigSection(self._config["extract"])

    @property
    def storage(self):
        return ConfigSection(self._config["storage"])


class ConfigSection:
    """Generic configuration section wrapper."""

    def __init__(self, section):
        self._section = section

    def __getattr__(self, name):
        # Handle Python reserved words with trailing underscore
        if name.endswith("_") and name[:-1] in self._section:
            actual_name = name[:-1]
        else:
            actual_name = name

        try:
            return self._section[actual_name]
        except (KeyError, TypeError):
            raise AttributeError(
                f"'{type(self).__name__}' object has no attribute '{name}'"
            )


class OutputConfigSection(ConfigSection):
    """Output configuration section with Path conversion."""

    @property
    def dir(self) -> Path:
        return Path(str(self._section["dir"]))

    @dir.setter
    def dir(self, value: Union[str, Path]):
        # Dynaconf doesn't have a simple set method for nested keys
        pass

    @property
    def metadata_backend(self) -> str:
        return str(self._section["metadata_backend"])


class SitemapConfigSection(ConfigSection):
    """Sitemap configuration section."""

    @property
    def url(self) -> Optional[str]:
        url = self._section.get("url", "")
        return url if url else None

    @url.setter
    def url(self, value: Optional[str]):
        # Dynaconf doesn't have a simple set method for nested keys
        pass

    @property
    def use_lastmod(self) -> bool:
        return bool(self._section["use_lastmod"])


def load_config(config_files: List[Path]) -> Config:
    """Load configuration using Dynaconf (backward compatibility function).

    Args:
        config_files: List of configuration file paths

    Returns:
        Config wrapper object
    """
    dynaconf_config = create_config(config_files)
    validate_config(dynaconf_config)
    return Config(dynaconf_config)
