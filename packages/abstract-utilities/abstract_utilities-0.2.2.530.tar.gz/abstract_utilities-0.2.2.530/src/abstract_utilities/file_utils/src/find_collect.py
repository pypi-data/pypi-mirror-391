from ..imports import *
from .file_filters import *
from .filter_params import *
from pathlib import Path
from typing import Optional, List, Set

def get_proper_type_str(string):
    if not string:
        return None
    string_lower = string.lower()
    items = {
        "d":["dir","dirs","directory","directories","d","dirname"],
        "f":["file","filepath","file_path","files","filepaths","file_paths","f"]
     }
    for key,values in items.items():
        if string_lower in values:
            return key
    init = string_lower[0] if len(string_lower)>0 else None
    if init in items:
        return init
def check_path_type(
    path: str,
    user: Optional[str] = None,
    host: Optional[str] = None,
    user_as_host: Optional[str] = None,
    use_shell: bool = False
) -> Literal["file", "directory", "missing", "unknown"]:
    """
    Determine whether a given path is a file, directory, or missing.
    Works locally or remotely (via SSH).

    Args:
        path: The path to check.
        user, host, user_as_host: SSH parameters if remote.
        use_shell: Force shell test instead of Python os.path.
    Returns:
        One of: 'file', 'directory', 'missing', or 'unknown'
    """

    # --- remote check if user/host is given ---
    if user_as_host or (user and host):
        remote_target = user_as_host or f"{user}@{host}"
        cmd = f"if [ -f '{path}' ]; then echo file; elif [ -d '{path}' ]; then echo directory; else echo missing; fi"
        try:
            result = subprocess.check_output(
                ["ssh", remote_target, cmd],
                stderr=subprocess.DEVNULL,
                text=True,
                timeout=5
            ).strip()
            return result if result in ("file", "directory", "missing") else "unknown"
        except Exception:
            return "unknown"

    # --- local check ---
    if not use_shell:
        if os.path.isfile(path):
            return "file"
        elif os.path.isdir(path):
            return "directory"
        elif not os.path.exists(path):
            return "missing"
        return "unknown"
    else:
        # fallback using shell tests (useful for sandboxed contexts)
        cmd = f"if [ -f '{path}' ]; then echo file; elif [ -d '{path}' ]; then echo directory; else echo missing; fi"
        try:
            output = subprocess.check_output(
                cmd, shell=True, stderr=subprocess.DEVNULL, text=True
            ).strip()
            return output if output in ("file", "directory", "missing") else "unknown"
        except Exception:
            return "unknown"





def get_find_cmd(
    *args,
    mindepth: Optional[int] = None,
    maxdepth: Optional[int] = None,
    depth: Optional[int] = None,
    file_type: Optional[str] = None,  # 'f' or 'd'
    name: Optional[str] = None,
    size: Optional[str] = None,
    mtime: Optional[str] = None,
    perm: Optional[str] = None,
    user: Optional[str] = None,
    **kwargs
) -> str:
    """
    Construct a Unix `find` command string that supports multiple directories.
    Accepts filtering via ScanConfig-compatible kwargs.
    """
    # Normalize inputs into canonical form
    kwargs = get_safe_canonical_kwargs(*args, **kwargs)
    cfg = define_defaults(**kwargs)

    # Get directory list (may come from args or kwargs)
    directories = [r for r in make_list(kwargs.get("directories")) if r]
    if not directories:
        raise ValueError("No directories specified for `find` command.")

    # Build base command for all directories
    dir_expr = " ".join(shlex.quote(d) for d in directories)
    cmd = [f"find {dir_expr}"]

    # --- depth filters ---
    if depth is not None:
        cmd += [f"-mindepth {depth}", f"-maxdepth {depth}"]
    else:
        if mindepth is not None:
            cmd.append(f"-mindepth {mindepth}")
        if maxdepth is not None:
            cmd.append(f"-maxdepth {maxdepth}")

    # --- file type ---
    if file_type in ("f", "d"):
        cmd.append(f"-type {file_type}")

    # --- basic attributes ---
    if name:
        cmd.append(f"-name {shlex.quote(name)}")
    if size:
        cmd.append(f"-size {shlex.quote(size)}")
    if mtime:
        cmd.append(f"-mtime {shlex.quote(mtime)}")
    if perm:
        cmd.append(f"-perm {shlex.quote(perm)}")
    if user:
        cmd.append(f"-user {shlex.quote(user)}")

    # --- cfg-based filters ---
    if cfg:
        # Allowed extensions
        if cfg.allowed_exts and cfg.allowed_exts != {"*"}:
            ext_expr = " -o ".join(
                [f"-name '*{e}'" for e in cfg.allowed_exts if e]
            )
            cmd.append(f"\\( {ext_expr} \\)")

        # Excluded extensions
        if cfg.exclude_exts:
            for e in cfg.exclude_exts:
                cmd.append(f"! -name '*{e}'")

        # Allowed directories
        if cfg.allowed_dirs and cfg.allowed_dirs != ["*"]:
            dir_expr = " -o ".join(
                [f"-path '*{d}*'" for d in cfg.allowed_dirs if d]
            )
            cmd.append(f"\\( {dir_expr} \\)")

        # Excluded directories
        if cfg.exclude_dirs:
            for d in cfg.exclude_dirs:
                cmd.append(f"! -path '*{d}*'")

        # Allowed patterns
        if cfg.allowed_patterns and cfg.allowed_patterns != ["*"]:
            pat_expr = " -o ".join(
                [f"-name '{p}'" for p in cfg.allowed_patterns if p]
            )
            cmd.append(f"\\( {pat_expr} \\)")

        # Excluded patterns
        if cfg.exclude_patterns:
            for p in cfg.exclude_patterns:
                cmd.append(f"! -name '{p}'")

        # Allowed types (semantic, not `-type`)
        if cfg.allowed_types and cfg.allowed_types != {"*"}:
            type_expr = " -o ".join(
                [f"-path '*{t}*'" for t in cfg.allowed_types if t]
            )
            cmd.append(f"\\( {type_expr} \\)")

        # Excluded types
        if cfg.exclude_types:
            for t in cfg.exclude_types:
                cmd.append(f"! -path '*{t}*'")

    return " ".join(cmd)



def collect_globs(
    *args,
    mindepth: Optional[int] = None,
    maxdepth: Optional[int] = None,
    depth: Optional[int] = None,
    file_type: Optional[str] = None,   # "f", "d", or None
    allowed: Optional[Callable[[str], bool]] = None,
    **kwargs
) -> List[str] | dict:
    """
    Collect file or directory paths recursively.

    - If file_type is None → returns {"f": [...], "d": [...]}
    - If file_type is "f" or "d" → returns a list of that type
    - Supports SSH mode via `user_at_host`
    """
    kwargs= get_safe_canonical_kwargs(*args,**kwargs)
    
    cfg = define_defaults(**kwargs)
    allowed = kwargs.get("allowed") or make_allowed_predicate(cfg)
    type_strs = {"f":"files","d":"dirs"}
    file_type = get_proper_type_str(file_type)
    file_types = make_list(file_type)
    if file_type == None:
        file_types = ["f","d"]
    return_results = {}
    return_result=[]
    for file_type in file_types:
        type_str = type_strs.get(file_type)
        # Remote path (SSH)
        find_cmd = get_find_cmd(
                cfg=cfg,
                mindepth=mindepth,
                maxdepth=maxdepth,
                depth=depth,
                file_type=file_type,
                **{k: v for k, v in kwargs.items() if v},
            )
        result = run_pruned_func(run_cmd,find_cmd,
            **kwargs
            
            )
        return_result = [res for res in result.split('\n') if res]
        return_results[type_str]=return_result
    if len(file_types) == 1:
        return return_result
    return return_results
def get_files_and_dirs(
    *args,
    recursive: bool = True,
    include_files: bool = True,
    **kwargs
    ):
    if recursive == False:
        kwargs['maxdepth']=1
    if include_files == False:
        kwargs['file_type']='d'
    result = collect_globs(*args,**kwargs)
    if include_files == False:
        return result,[]
    dirs = result.get("dirs")
    files = result.get("files")
    return dirs,files
def collect_filepaths(
    *args,
    **kwargs
    ) -> List[str]:
    kwargs['file_type']='f'
    return collect_globs(*args,**kwargs)
