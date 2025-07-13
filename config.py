import yaml

def load_config(path="config.yaml"):
    with open(path, "r") as f:
        return yaml.safe_load(f)

_config = load_config()

def get_ollama_url(endpoint="chat"):
    base = _config.get("ollama_url_base", "http://localhost:11434")
    return f"{base.rstrip('/')}/api/{endpoint}"
