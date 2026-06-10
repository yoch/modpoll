import importlib.metadata as importlib_metadata

try:
    __version__ = importlib_metadata.version("modpoll2mqtt")
except importlib_metadata.PackageNotFoundError:
    __version__ = "0.0.0"
