import json
import os

class Config:
    def __init__(self):
        self.config_path = os.path.expanduser("~/.datamule/config.json")
        self._ensure_config_exists()
        
    def _ensure_config_exists(self):
        os.makedirs(os.path.dirname(self.config_path), exist_ok=True)
        if not os.path.exists(self.config_path):
            self._save_config({"default_source": None})

    def _save_config(self, config):
        with open(self.config_path, 'w') as f:
            json.dump(config, f)

    def set_default_source(self, source):
        config = self._load_config()
        config["default_source"] = source
        self._save_config(config)

    def get_default_source(self):
        config = self._load_config()
        return config.get("default_source")

    def _load_config(self):
        with open(self.config_path) as f:
            return json.load(f)