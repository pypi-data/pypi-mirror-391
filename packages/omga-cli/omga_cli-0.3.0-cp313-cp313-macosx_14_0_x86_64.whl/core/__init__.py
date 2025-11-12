from __future__ import annotations

import sys
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path

__version__ = "0.2.0"


def _prefer_pure_python(module_name: str) -> None:
    """Force loading the pure-Python implementation when C extensions exist."""
    package_dir = Path(__file__).resolve().parent
    source_path = package_dir / f"{module_name}.py"

    if not source_path.exists():
        return

    qualified_name = f"{__name__}.{module_name}"

    try:
        spec = spec_from_file_location(qualified_name, str(source_path))
        if spec is None or spec.loader is None:
            return
        module = module_from_spec(spec)
        sys.modules[qualified_name] = module
        spec.loader.exec_module(module)
        sys.modules[qualified_name] = module
        setattr(sys.modules[__name__], module_name, module)
    except Exception:
        # Fallback silently to the default loader if custom loading fails.
        # Logging is avoided here to prevent circular imports during init.
        return


# Ensure rich UI enhancements use the updated Python module
_prefer_pure_python("ui")