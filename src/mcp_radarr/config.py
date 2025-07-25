from importlib.resources import files
import os
from pathlib import Path
from omegaconf import OmegaConf, DictConfig, ListConfig

class RadarrConfig:
    def __init__(self, url: str | None = None, api_key: str | None = None, config_path: str | None = None):
        self._url: str = url
        self._api_key: str = api_key
        self._config: DictConfig | ListConfig | None = None

        config: DictConfig | ListConfig | None = None
        if config_path is not None and Path(config_path).exists():
            config = OmegaConf.load(config_path)
        
        default_path = self.get_config_path()
        if Path(default_path).exists():
            self._config = OmegaConf.load(default_path)
            if config is not None:
                self._config = OmegaConf.merge(config, self._config)
        elif config is not None:
            self._config = config

    @property
    def url(self):
        if self._url:
            return self._url
        url = self._config_get("RADARR_URL", "radarr.url")
        if not url:
            raise RuntimeError("Radarr URL not set in config")
        return url
    
    @property
    def api_key(self):
        if self._api_key:
            return self._api_key
        api_key = self._config_get("RADARR_API_KEY", "radarr.api_key")
        if not api_key:
            raise RuntimeError("Radarr API key not set in config")
        return api_key
    
    def _config_get(self, env_key: str, config_key: str):
        if env_key in os.environ:
            return os.environ.get(env_key)
        if self._config is not None:
            return OmegaConf.select(self._config, config_key)
        return None

    def get_config_path(self):
        # First check if environment variable is set
        if "RADARR_CONFIG" in os.environ:
            return os.environ["RADARR_CONFIG"]
        
        # Then look in user home directory
        user_config = Path.home() / ".config" / "mcp-radarr" / "config.yaml"
        if user_config.exists():
            return str(user_config)

        # Then look in current directory
        cwd_config = Path.cwd() / "config.yaml"
        if cwd_config.exists():
            return str(cwd_config)
        
        # Finally, fall back to package resource
        try:
            return str(files("mcp_radarr").joinpath("config.yaml"))
        except (ImportError, FileNotFoundError):
            # If package resource not found, return a default path
            return str(Path.home() / ".config" / "mcp-radarr" / "config.yaml")

