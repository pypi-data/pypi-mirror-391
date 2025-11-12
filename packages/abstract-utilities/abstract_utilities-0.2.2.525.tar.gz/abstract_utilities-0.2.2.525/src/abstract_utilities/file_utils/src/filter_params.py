
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
def get_replace_strings(string,strings_js):
    for string_key,string_values in strings_js.items():
        string_parts = string.split('_')
        for i,string_part in enumerate(string_parts):
            if string_part in string_values:
                string_parts[i] = string_key
    return '-'.join(string_parts)
    
import re
def get_safe_kwargs(canonical_map,**kwargs):
    # Lowercase all keys for safety
    norm_kwargs = {k.lower(): v for k, v in kwargs.items() if v is not None}

    # Inverse lookup: alias → canonical key
    alias_lookup = {alias: canon for canon, aliases in canonical_map.items() for alias in aliases}

    safe_kwargs = {k: v for k, v in norm_kwargs.items() if k in canonical_map}  # preserve correctly named keys

    for k, v in norm_kwargs.items():
        if k in alias_lookup:
            canonical_key = alias_lookup[k]
            prev = safe_kwargs.get(canonical_key)
            if prev is None:
                safe_kwargs[canonical_key] = v
            else:
                # merge intelligently if both exist
                if isinstance(prev, (set, list)) and isinstance(v, (set, list)):
                    safe_kwargs[canonical_key] = list(set(prev) | set(v))
                else:
                    safe_kwargs[canonical_key] = v  # overwrite for non-iterables

    # fill defaults if missing
    for canon in canonical_map:
        safe_kwargs.setdefault(canon, None)

    return safe_kwargs
def get_dir_filter_kwargs(**kwargs):
    canonical_map = {
        "directories": ["directory", "directories", "dirs", "paths", "path","roots","root"]
        }
    return get_safe_kwargs(canonical_map,**kwargs)
def get_file_filter_kwargs(**kwargs):
    """
    Normalize arbitrary keyword arguments for file scanning configuration.
    
    Examples:
      - 'excluded_ext' or 'unallowed_exts' → 'exclude_exts'
      - 'include_dirs' or 'allow_dir' → 'allowed_dirs'
      - 'excludePattern' or 'excluded_patterns' → 'exclude_patterns'
      - 'allowed_type' or 'include_types' → 'allowed_types'
    """
    # Canonical keys and aliases
    canonical_map = {
        "allowed_exts": ["allow_ext", "allowed_ext", "include_ext", "include_exts", "exts_allowed"],
        "exclude_exts": ["exclude_ext", "excluded_ext", "excluded_exts", "unallowed_ext", "unallowed_exts"],
        "allowed_types": ["allow_type", "allowed_type", "include_type", "include_types", "types_allowed"],
        "exclude_types": ["exclude_type", "excluded_type", "excluded_types", "unallowed_type", "unallowed_types"],
        "allowed_dirs": ["allow_dir", "allowed_dir", "include_dir", "include_dirs", "dirs_allowed"],
        "exclude_dirs": ["exclude_dir", "excluded_dir", "excluded_dirs", "unallowed_dir", "unallowed_dirs"],
        "allowed_patterns": ["allow_pattern", "allowed_pattern", "include_pattern", "include_patterns", "patterns_allowed"],
        "exclude_patterns": ["exclude_pattern", "excluded_pattern", "excluded_patterns", "unallowed_pattern", "unallowed_patterns"],
    }

    return get_safe_kwargs(canonical_map,**kwargs)

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
def derive_file_defaults(**kwargs):
    kwargs = get_file_filter_kwargs(**kwargs)
    add = kwargs.get("add",False)
    allowed_exts = _get_default_modular(
        ensure_exts(kwargs.get("allowed_exts")), DEFAULT_ALLOWED_EXTS, add, set
    )
    exclude_exts = _get_default_modular(
        ensure_exts(kwargs.get("exclude_exts")), DEFAULT_EXCLUDE_EXTS, add, set
    )
    allowed_types = _get_default_modular(
        _normalize_listlike(kwargs.get("allowed_types"), set), DEFAULT_ALLOWED_TYPES, add, set
    )
    exclude_types = _get_default_modular(
        _normalize_listlike(kwargs.get("exclude_types"), set), DEFAULT_EXCLUDE_TYPES, add, set
    )
    allowed_dirs = _get_default_modular(
        _normalize_listlike(kwargs.get("allowed_dirs"), list), DEFAULT_ALLOWED_DIRS, add, list
    )
    exclude_dirs = _get_default_modular(
        _normalize_listlike(kwargs.get("exclude_dirs"), list), DEFAULT_EXCLUDE_DIRS, add, list
    )
    allowed_patterns = _get_default_modular(
        ensure_patterns(kwargs.get("allowed_patterns")), DEFAULT_ALLOWED_PATTERNS, add, list
    )
    exclude_patterns = _get_default_modular(
        ensure_patterns(kwargs.get("exclude_patterns")), DEFAULT_EXCLUDE_PATTERNS, add, list
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

def get_file_filters(*args,**kwargs) -> List[str]:
    directories = []
    for arg in args:
        arg_str = str(arg)
        if is_dir(arg_str,**kwargs):
            directories.append(arg_str)
        elif is_file(arg_str,**kwargs):
            dirname = os.path.dirname(arg_str)
            directories.append(dirname)
    safe_directories = get_dir_filter_kwargs(**kwargs)
    directories+= make_list(safe_directories.get('directories',[]))
    directories = list(set([r for r in directories if r]))
    cfg = kwargs.get('cfg') or define_defaults(**kwargs)
    allowed = kwargs.get('allowed') or make_allowed_predicate(cfg)
    include_files = kwargs.get('include_files',True)
    recursive = kwargs.get('recursive',True)
    return directories,cfg,allowed,include_files,recursive
