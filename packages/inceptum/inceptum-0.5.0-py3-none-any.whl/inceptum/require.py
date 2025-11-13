__all__ = ['require', 'register']

import builtins
import os
import os.path
import sys
import types
from importlib import import_module
from typing import Any, Callable, Dict, Optional, List

from .config import config

# If environment variable MY is set, add "$MY/code/main/python/submodules" to sys.path
if _MY := os.environ.get("MY"):
    submodules_path = os.path.join(_MY, "code", "main", "python", "submodules")
    if os.path.isdir(submodules_path) and submodules_path not in sys.path:
        sys.path.insert(0, submodules_path)

# In-memory registry for explicitly registered callables
_REGISTRY: Dict[str, Callable[..., Any]] = {}


def register(name: Optional[str] = None, *, override: bool = False):
    """
    Decorator to register a callable so it can be retrieved with require().

    Behavior:
      - Keys are matched exactly after hyphens are normalized to underscores.
      - If override is False and the key is in use by a different callable, raises ValueError.
      - Registry lookups do not apply toplevel module prefix mapping.
    """
    def decorator(fn: Callable[..., Any]) -> Callable[..., Any]:
        key = (name or fn.__name__).replace('-', '_')
        if not key:
            raise ValueError("register: empty key is not allowed")
        existing = _REGISTRY.get(key)
        if existing is not None and existing is not fn and not override:
            raise ValueError(f"register: key already in use: {key!r}")
        _REGISTRY[key] = fn
        return fn
    return decorator


def _resolve_alias(name: str) -> str:
    """
    Resolve aliases from config('inceptum.registry'), following string-to-string mappings.
    - Hyphens are normalized to underscores at each hop.
    - Cycles are detected and stop resolution.
    """
    mapping = config('inceptum.registry', default=None)
    if not isinstance(mapping, dict):
        return name

    seen = set()
    current = name
    for _ in range(32):
        if current in seen:
            break
        seen.add(current)
        target = mapping.get(current)
        if not isinstance(target, str):
            break
        current = target.replace('-', '_')
    return current


def _get_prefixes() -> List[str]:
    """
    Read default prefixes from config('inceptum.prefixes'), expected to be a list[str]
    without trailing dots. Returns [] if missing or invalid.
    """
    prefixes = config('inceptum.prefixes', default=None)
    if not isinstance(prefixes, list):
        return []
    out: list[str] = []
    for p in prefixes:
        if isinstance(p, str) and p:
            out.append(p[:-1] if p.endswith('.') else p)
    return out


def toplevel(name):
    """
    Map a toplevel module name using inceptum.module. The legacy inceptum.prefix
    is removed in favor of inceptum.prefixes and is not applied here.
    """
    if cfg := config('inceptum'):
        m = cfg.get('module')
        if m and name in m:
            return m[name]
    return name


def _resolve_single(target_in: Any, *, cli: bool = False):
    """
    Attempt to resolve a single target (no prefix probing).
    - No aliasing here - aliasing is handled in the caller when probing.
    - Registry lookups are checked for exact key matches only.
    - When cli=True, implicit '<name>.cli.main' probing is applied for short names.
    """
    target = target_in

    # Normalize hyphens early
    if isinstance(target, str):
        target = target.replace('-', '_')

        # Registered callable - direct hit
        if target in _REGISTRY:
            return _REGISTRY[target]

    # CLI mode - try resolving with implicit ".cli.main" when appropriate
    if cli:
        if isinstance(target, str):
            path = [p.replace('-', '_') for p in target.split('.')]
        else:
            path = [str(target)]

        # Apply implicit cli.main if:
        #  - single segment, or
        #  - two segments where the first is a configured prefix
        if len(path) == 1 or (len(path) == 2 and path[0] in _get_prefixes()):
            path.extend(('cli', 'main'))

        path[0] = toplevel(path[0])
        try:
            last = path.pop()
            module = import_module('.'.join(path))
            fn = getattr(module, last)
            if hasattr(fn, 'main'):
                fn = getattr(fn, 'main')
        except (ModuleNotFoundError, AttributeError):
            path.append(last)
            module = import_module('.'.join(path))
            try:
                fn = getattr(module, 'main')
            except AttributeError:
                fn = getattr(module, last)
        return fn

    # Non-CLI mode
    local_target = target
    if isinstance(local_target, str) and '.' in local_target:
        head, tail = local_target.split('.', 1)
        mapped_head = toplevel(head)
        attrs = tail.split('.')

        # Try to import head module if possible
        head_mod = None
        try:
            head_mod = import_module(mapped_head)
        except ModuleNotFoundError:
            head_mod = None  # mark that head import failed

        # Prefer attribute resolution on the head module first
        if head_mod is not None:
            obj = head_mod
            missing_attr = False
            for attr in attrs:
                if hasattr(obj, attr):
                    obj = getattr(obj, attr)
                else:
                    missing_attr = True
                    break
            if not missing_attr:
                return obj

        # Try parent module attribute with the last segment name (supports re-exports)
        parent_mod = None
        last_attr = attrs[-1] if attrs else None
        parent_name = '.'.join([mapped_head] + attrs[:-1]) if len(attrs) > 1 else mapped_head
        if attrs:
            try:
                parent_mod = import_module(parent_name)
            except ModuleNotFoundError:
                parent_mod = sys.modules.get(parent_name)

        if parent_mod is not None and last_attr and hasattr(parent_mod, last_attr):
            return getattr(parent_mod, last_attr)

        # Fallback: try importing the full dotted module path
        modname = '.'.join([mapped_head] + attrs)
        try:
            full_mod = import_module(modname)

            # Try attribute on the leaf module with the same name as the last segment
            if last_attr and hasattr(full_mod, last_attr):
                return getattr(full_mod, last_attr)

            # Otherwise return the module itself
            return full_mod
        except ModuleNotFoundError:
            # As a fallback, check if the module already exists in sys.modules
            full_mod = sys.modules.get(modname)
            if full_mod is not None:
                if last_attr and hasattr(full_mod, last_attr):
                    return getattr(full_mod, last_attr)
                return full_mod

            # If head module existed but the attribute chain was missing,
            # re-attempt attribute lookup to raise AttributeError consistently.
            if head_mod is not None:
                obj = head_mod
                for attr in attrs:
                    obj = getattr(obj, attr)  # will raise AttributeError at the missing hop
            # Otherwise propagate the module import failure
            raise

    # No dot - import module directly
    d = import_module(toplevel(local_target if isinstance(local_target, str) else str(local_target)))
    return d


def _is_missing_candidate_module(exc: ModuleNotFoundError, candidate: str) -> bool:
    """
    Return True if the ModuleNotFoundError clearly refers to the candidate path
    itself (top-level or submodule), which means the candidate doesn't exist
    and we can keep probing. Otherwise, it likely refers to a missing dependency
    inside an existing module, and we should fail fast.
    """
    name = getattr(exc, "name", None)
    if not isinstance(name, str):
        return False
    # Examples that should be considered "candidate missing":
    #  - candidate == "pkg.mod" and name == "pkg.mod" (missing submodule)
    #  - candidate == "pkg.mod.attr" (internally we import modules) and name in {"pkg", "pkg.mod"}
    return candidate == name or candidate.startswith(name + ".")


def require(name, *args, _probe_prefixes: bool = True, cli: bool = False):
    """
    Resolve a module, attribute, or registered callable by name.

    - Only one keyword is supported: cli (bool). When True, apply implicit ".cli.main"
      probing for short names.
    - Additional positional string arguments are allowed and will be joined with dots,
      so require('a', 'b', 'c') is equivalent to require('a.b.c').
    """
    # Allow multiple string segments to form a dotted name
    if args:
        if isinstance(name, str) and all(isinstance(a, str) for a in args):
            name = '.'.join([name] + list(args))
        else:
            raise TypeError("require: all positional arguments must be strings when providing multiple segments")

    # Optionally special-case for config
    if (
        name == 'config'
        and isinstance(name, str)
        and config('inceptum.require.special_config', default=False)
    ):
        return config

    # Without probing - apply aliasing once, no prefixes
    if not _probe_prefixes:
        if isinstance(name, str):
            normalized = name.replace('-', '_')
            normalized = _resolve_alias(normalized)
            return _resolve_single(normalized, cli=cli)
        return _resolve_single(name, cli=cli)

    # Build candidate list with alias-resolved seed first (unprefixed only), then original
    if isinstance(name, str):
        prefixes = _get_prefixes()
        normalized = name.replace('-', '_')
        aliased = _resolve_alias(normalized)

        seeds: List[str] = []
        # Put aliased first, then original if different
        if aliased:
            seeds.append(aliased)
        if normalized and normalized != aliased:
            seeds.append(normalized)

        candidates: List[str] = []
        for idx, seed in enumerate(seeds):
            # Always try the unprefixed seed itself
            candidates.append(seed)

            # For the original seed only (not the aliased one), try prefixed variants
            if idx == 1 or (idx == 0 and seed == normalized):
                for p in prefixes:
                    # Do not add a prefix if the seed already starts with one of the prefixes
                    if seed.startswith(p + '.'):
                        continue
                    candidates.append(f"{p}.{seed}")

        last_exc: Optional[BaseException] = None
        fallback_module: Optional[types.ModuleType] = None
        seen: set[str] = set()
        for cand in candidates:
            if cand in seen:
                continue
            seen.add(cand)
            try:
                obj = _resolve_single(cand, cli=cli)
                if isinstance(obj, types.ModuleType):
                    if fallback_module is None:
                        fallback_module = obj
                    continue
                return obj
            except SyntaxError:
                # Fail fast on syntax errors
                raise
            except ModuleNotFoundError as exc:
                # Continue probing only if the missing module is the candidate itself
                # (or its parent in the dotted path). Otherwise, it's a missing
                # dependency inside an existing module -> fail fast.
                if _is_missing_candidate_module(exc, cand):
                    last_exc = exc
                    continue
                raise
            except ImportError:
                # Non-ModuleNotFoundError ImportError indicates candidate exists
                # but failed to import correctly -> fail fast.
                raise
            except (AttributeError, KeyError) as exc:
                last_exc = exc
                continue

        if fallback_module is not None:
            return fallback_module
        if last_exc is not None:
            raise ModuleNotFoundError(f"require: could not resolve {name!r}") from last_exc
        raise ModuleNotFoundError(f"require: could not resolve {name!r}")

    # Non-string target - resolve directly
    return _resolve_single(name, cli=cli)


builtins.require = require

# DEPRECATED
builtins.I = require
builtins.leptonix = require
