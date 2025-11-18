import os

ENVIRONMENTS = ["development", "test", "local", "preview", "production"]

ENV = os.getenv("ENV", "development")
LOG_ON_FILE = int(os.getenv("LOG_ON_FILE", "0"))
