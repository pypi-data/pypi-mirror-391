from .core import CalcSet, Category, Filter, If, IfRow, Number, Variable
from .decomp import decompile, decompile_to_string
from .display import display_calcset, display_item, set_theme
from .helpers import Average, Normalize, Product, Sum, WeightedAverage

# Version is managed in pyproject.toml and read dynamically
try:
    from importlib.metadata import PackageNotFoundError, version
except ImportError:
    # Python < 3.8 fallback
    from importlib_metadata import PackageNotFoundError, version

try:
    __version__ = version("lf_pollywog")
except PackageNotFoundError:
    # Package is not installed, use a placeholder
    __version__ = "0.0.0.dev0"

__all__ = [
    # Core classes
    "CalcSet",
    "Variable",
    "Number",
    "Category",
    "Filter",
    "If",
    "IfRow",
    # Helper functions
    "Sum",
    "Average",
    "Product",
    "Normalize",
    "WeightedAverage",
    # Display functions
    "display_calcset",
    "display_item",
    "set_theme",
    # Decompilation
    "decompile",
    "decompile_to_string",
    # Version
    "__version__",
]
