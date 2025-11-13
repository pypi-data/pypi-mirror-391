import os
import sys


def load_envs(env_path: str):
    """
    Returns a stream of export statements
    """
    if not os.path.exists(env_path):
        print("Env path", env_path, "doesn't exist")
        sys.exit(1)

    with open(env_path, "r") as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                key, value = line.split("=", 1)
                value = value.strip().strip('"').strip("'")
                print(f"export {key}='{value}'")
