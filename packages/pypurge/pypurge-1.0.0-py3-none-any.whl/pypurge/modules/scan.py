import fnmatch
import os
import re
from collections import defaultdict
from pathlib import Path

from .utils import is_old_enough


def scan_for_targets(
    root_path: Path,
    dir_groups: dict,
    file_groups: dict,
    exclude_dirs: set,
    exclude_patterns: list,
    older_than_sec: int,
    age_type: str,
    delete_symlinks: bool,
) -> dict:
    targets = defaultdict(list)
    for root, dirs, files in os.walk(root_path, topdown=True, followlinks=False):
        dirs[:] = [d for d in dirs if d not in exclude_dirs]
        try:
            rel_root = Path(root).relative_to(root_path)
        except Exception:
            rel_root = Path(".")
        for d in list(dirs):
            d_path = Path(root) / d
            if d_path.is_symlink() and not delete_symlinks:
                continue
            if older_than_sec and not is_old_enough(d_path, older_than_sec, age_type):
                continue
            rel_str = str(rel_root / d)
            if any(
                (pt == "re" and pat.search(rel_str))
                or (pt == "glob" and fnmatch.fnmatch(rel_str, pat))
                for pt, pat in exclude_patterns
            ):
                dirs.remove(d)
                continue
            matched = False
            for g, pats in dir_groups.items():
                for pat in pats:
                    try:
                        if fnmatch.fnmatch(d, pat) or fnmatch.fnmatch(rel_str, pat):
                            targets[g].append(d_path)
                            matched = True
                            break
                    except Exception:
                        continue
                if matched:
                    break
            if matched and d in dirs:
                dirs.remove(d)
        for f in files:
            f_path = Path(root) / f
            if f_path.is_symlink() and not delete_symlinks:
                continue
            if older_than_sec and not is_old_enough(f_path, older_than_sec, age_type):
                continue
            rel_str = str(rel_root / f)
            if any(
                (pt == "re" and pat.search(rel_str))
                or (pt == "glob" and fnmatch.fnmatch(rel_str, pat))
                for pt, pat in exclude_patterns
            ):
                continue
            for g, pats in file_groups.items():
                matched = False
                for pat in pats:
                    try:
                        if fnmatch.fnmatch(f, pat) or fnmatch.fnmatch(rel_str, pat):
                            targets[g].append(f_path)
                            matched = True
                            break
                    except Exception:
                        continue
                if matched:
                    break
    return targets
