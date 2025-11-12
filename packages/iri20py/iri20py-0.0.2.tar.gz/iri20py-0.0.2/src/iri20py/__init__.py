from .download import check_files
from .base import Iri2020
from .utils import alt_grid
from . import settings
check_files()

__all__ = [
    "Iri2020", "settings",
    "alt_grid", "check_files"
]
