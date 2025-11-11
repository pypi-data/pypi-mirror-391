
from ..imports import *
import re
def combine_params(*values,typ=None):
    nu_values = None
    for value in values:
        if value is not None:
            typ = typ or type(value)
            if nu_values is None:
                nu_values = typ()
            
            if typ is set:
                nu_values = nu_values | typ(value)
            if typ is list:
                nu_values += typ(value)
    return nu_values
# -------------------------
# Default sets
# -------------------------
DEFAULT_ALLOWED_EXTS: Set[str] = {
    ".py", ".pyw", ".js", ".jsx", ".ts", ".tsx", ".mjs",
    ".html", ".htm", ".xml", ".css", ".scss", ".sass", ".less",
    ".json", ".yaml", ".yml", ".toml", ".ini", ".cfg",
    ".md", ".markdown", ".rst", ".sh", ".bash", ".env", ".txt"
}

DEFAULT_EXCLUDE_TYPES: Set[str] = {
    "image", "video", "audio", "presentation",
    "spreadsheet", "archive", "executable"
}

_unallowed = set(get_media_exts(DEFAULT_EXCLUDE_TYPES)) | {
    ".bak", ".shp", ".cpg", ".dbf", ".shx", ".geojson",
    ".pyc", ".prj", ".sbn", ".sbx"
}
DEFAULT_EXCLUDE_EXTS = {e.split('.')[-1] for e in _unallowed if e not in DEFAULT_ALLOWED_EXTS}

DEFAULT_EXCLUDE_DIRS: List[str] = [
    "node_modules", "__pycache__", "backups", "backup",
    "trash", "deprecated", "old", "__init__"
]

DEFAULT_EXCLUDE_PATTERNS: List[str] = [
    "__init__*", "*.tmp", "*.log", "*.lock", "*.zip", "*~"
]

DEFAULT_ALLOWED_PATTERNS: List[str] = ["*"]
DEFAULT_ALLOWED_DIRS: List[str] = ["*"]
DEFAULT_ALLOWED_TYPES: List[str] = ["*"]



REMOTE_RE = re.compile(r"^(?P<host>[^:\s]+@[^:\s]+):(?P<path>/.*)$")
AllowedPredicate = Optional[Callable[[str], bool]]

# -------------------------
# Config dataclass
# -------------------------

@dataclass
class ScanConfig:
    allowed_exts: Set[str]
    exclude_exts: Set[str]
    allowed_types: Set[str]
    exclude_types: Set[str]
    allowed_dirs: List[str] = field(default_factory=list)
    exclude_dirs: List[str] = field(default_factory=list)
    allowed_patterns: List[str] = field(default_factory=list)
    exclude_patterns: List[str] = field(default_factory=list)

# -------------------------
# Utility functions
# -------------------------

def _normalize_listlike(value, typ=list, sep=','):
    """Normalize comma-separated or iterable values into the desired type."""
    if value in [True, None, False]:
        return value
    if isinstance(value, str):
        value = [v.strip() for v in value.split(sep) if v.strip()]
    return typ(value)

def ensure_exts(exts):
    if exts in [True, None, False]:
        return exts
    out = []
    for ext in _normalize_listlike(exts, list):
        if not ext.startswith('.'):
            ext = f".{ext}"
        out.append(ext)
    return set(out)

def ensure_patterns(patterns):
    """Normalize pattern list and ensure they are valid globs."""
    if patterns in [True, None, False]:
        return patterns
    patterns = _normalize_listlike(patterns, list)
    out = []
    for pattern in patterns:
        if not pattern:
            continue
        if '*' not in pattern and '?' not in pattern:
            # Implicitly make it a prefix match
            if pattern.startswith('.') or pattern.startswith('~'):
                pattern = f"*{pattern}"
            else:
                pattern = f"{pattern}*"
        out.append(pattern)
    return out


def _get_default_modular(value, default, add=False, typ=set):
    """Merge user and default values intelligently."""
    if value == None:
        value = add
    if value in [True]:
        return default
    if value is False:
        return value
    if add:
        return combine_params(value,default,typ=None)

    return typ(value)

# -------------------------
# Default derivation logic
# -------------------------
def derive_file_defaults(
    allowed_exts=None, exclude_exts=None,
    allowed_types=None, exclude_types=None,
    allowed_dirs=None, exclude_dirs=None,
    allowed_patterns=None, exclude_patterns=None,
    add=False
):
    allowed_exts = _get_default_modular(
        ensure_exts(allowed_exts), DEFAULT_ALLOWED_EXTS, add, set
    )
    exclude_exts = _get_default_modular(
        ensure_exts(exclude_exts), DEFAULT_EXCLUDE_EXTS, add, set
    )
    allowed_types = _get_default_modular(
        _normalize_listlike(allowed_types, set), DEFAULT_ALLOWED_TYPES, add, set
    )
    exclude_types = _get_default_modular(
        _normalize_listlike(exclude_types, set), DEFAULT_EXCLUDE_TYPES, add, set
    )
    allowed_dirs = _get_default_modular(
        _normalize_listlike(allowed_dirs, list), DEFAULT_ALLOWED_DIRS, add, list
    )
    exclude_dirs = _get_default_modular(
        _normalize_listlike(exclude_dirs, list), DEFAULT_EXCLUDE_DIRS, add, list
    )
    allowed_patterns = _get_default_modular(
        ensure_patterns(allowed_patterns), DEFAULT_ALLOWED_PATTERNS, add, list
    )
    exclude_patterns = _get_default_modular(
        ensure_patterns(exclude_patterns), DEFAULT_EXCLUDE_PATTERNS, add, list
    )

    return {
        "allowed_exts": allowed_exts,
        "exclude_exts": exclude_exts,
        "allowed_types": allowed_types,
        "exclude_types": exclude_types,
        "allowed_dirs": allowed_dirs,
        "exclude_dirs": exclude_dirs,
        "allowed_patterns": allowed_patterns,
        "exclude_patterns": exclude_patterns,
    }

def define_defaults(**kwargs):
    defaults = derive_file_defaults(**kwargs)
    return ScanConfig(**defaults)
