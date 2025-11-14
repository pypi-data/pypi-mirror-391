import os

from mtcli.conf import config

SYMBOL = os.getenv("SYMBOL", config["DEFAULT"].get("symbol", fallback="WIN$N"))
DIGITOS = int(os.getenv("DIGITOS", config["DEFAULT"].getint("digitos", fallback=0)))
PERIOD = os.getenv("PERIOD", config["DEFAULT"].get("period", fallback="M1"))
PERIODOS = int(
    os.getenv("PERIODOS", config["DEFAULT"].getint("periodos", fallback=566))
)
RANGE = float(os.getenv("RANGE", config["DEFAULT"].getfloat("range", fallback=100)))
VOLUME = os.getenv("VOLUME", config["DEFAULT"].get("volume", fallback="tick"))
FROM = os.getenv("FROM", config["DEFAULT"].get("from", fallback=""))
TO = os.getenv("TO", config["DEFAULT"].get("to", fallback=""))
TIMEZONE = os.getenv(
    "TIMEZONE", config["DEFAULT"].get("timezone", fallback="America/Sao_Paulo")
)
