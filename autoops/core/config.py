import yaml


class Config:
    def __init__(self, path="config.yaml"):
        with open(path, "r") as file:
            self.config = yaml.safe_load(file)

    def get(self, section, key, default=None):
        return self.config.get(section, {}).get(key, default)