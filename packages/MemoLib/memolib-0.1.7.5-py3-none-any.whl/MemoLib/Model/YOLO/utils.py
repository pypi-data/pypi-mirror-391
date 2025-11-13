import yaml

class Utils:
    def load_yaml(file_path):
            """Load and parse a YAML file."""
            with open(file_path, 'r') as file:
                return yaml.safe_load(file)