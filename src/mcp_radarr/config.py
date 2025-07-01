import os
from pathlib import Path
from omegaconf import OmegaConf, DictConfig, ListConfig

config: DictConfig | ListConfig = None

# Load configuration at startup
def load_config():
    global config
    config_path = os.environ.get("RADARR_CONFIG", str(Path(__file__).parent.parent.parent / "config.yaml"))
    if not Path(config_path).exists():
        raise RuntimeError(f"Config file not found: {config_path}")
    config = OmegaConf.load(config_path)
    return config

def get_config() -> DictConfig | ListConfig:
    if not config:
        raise RuntimeError("Config not loaded. Call load_config() first.")
    return config
