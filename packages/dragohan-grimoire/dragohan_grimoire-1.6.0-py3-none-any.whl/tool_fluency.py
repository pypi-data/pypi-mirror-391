# tool_fluency.py
"""
Tool Fluency - single import activates Grimoire fluency across your local grimoire modules.

Usage:
    from tool_fluency import *

Behavior:
    - Auto-patches json_mage.modify, loops.loopon, simple_file.save/load, getter/converter/duplicates/internet public callables
    - Smart normalization & flattening (only when beneficial)
    - Persistent learning across runs (global + project-local)
    - Human-readable and JSON logging
    - Self-healing: tries alternate strategies on failures and records / reuses winning patterns
    - Exposes GrimoireBridge, _grimoire_normalize, _grimoire_flatten
"""

from __future__ import annotations
import json
import os
import traceback
import importlib
import inspect
import functools
from pathlib import Path
from datetime import datetime
import hashlib
import threading

# -----------------------------
# Configuration (tune as needed)
# -----------------------------
GLOBAL_MEMORY_DIR = Path.home() / ".grimoire_memory"
PROJECT_MEMORY_DIR = Path(".") / ".grimoire_memory"
GLOBAL_MEMORY_DIR.mkdir(exist_ok=True)
PROJECT_MEMORY_DIR.mkdir(exist_ok=True)

# Memory filenames
MEMORY_FILE = "memory.json"
ACTIVITY_LOG = "activity.log"
ACTIVITY_JSON = "activity.json"

# Full paths
GLOBAL_MEMORY_FILE = GLOBAL_MEMORY_DIR / MEMORY_FILE
PROJECT_MEMORY_FILE = PROJECT_MEMORY_DIR / MEMORY_FILE
GLOBAL_ACTIVITY_LOG = GLOBAL_MEMORY_DIR / ACTIVITY_LOG
PROJECT_ACTIVITY_LOG = PROJECT_MEMORY_DIR / ACTIVITY_LOG
GLOBAL_ACTIVITY_JSON = GLOBAL_MEMORY_DIR / ACTIVITY_JSON
PROJECT_ACTIVITY_JSON = PROJECT_MEMORY_DIR / ACTIVITY_JSON

# Modules to attempt to patch
TARGET_MODULES = [
    "json_mage",
    "loops",
    "simple_file",
    "getter",
    "converter",
    "duplicates",
    "internet"
]

# Max flatten depth when attempting auto-flattening
DEFAULT_FLATTEN_DEPTH = 20

# Confidence threshold before auto-applying a learned transformation without verbose notice
AUTO_APPLY_CONFIDENCE = 0.6

# Thread lock for safe writes
_IO_LOCK = threading.Lock()

# -----------------------------
# Low-level utilities
# -----------------------------


def _now_iso():
    return datetime.utcnow().isoformat() + "Z"


def _trace_short():
    return traceback.format_exc(limit=1)


def _sha1_of(obj) -> str:
    try:
        b = json.dumps(obj, default=str, sort_keys=True).encode("utf-8")
    except Exception:
        b = repr(obj).encode("utf-8")
    return hashlib.sha1(b).hexdigest()


def _safe_read_json(path: Path):
    try:
        if path.exists():
            return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        # corrupt or unreadable → return {}
        return {}
    return {}


def _safe_write_json(path: Path, data):
    with _IO_LOCK:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(data, indent=2, default=str), encoding="utf-8")


def _append_text_log(path: Path, text: str):
    with _IO_LOCK:
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "a", encoding="utf-8") as f:
            f.write(text + "\n")


def _append_json_activity(path: Path, record: dict):
    with _IO_LOCK:
        path.parent.mkdir(parents=True, exist_ok=True)
        data = _safe_read_json(path)
        if not isinstance(data, list):
            data = []
        data.append(record)
        _safe_write_json(path, data)


# -----------------------------
# Memory: persistent learning
# -----------------------------


class PersistentMemory:
    """
    Dual-layer memory: project-local + global merged on load.
    Stores:
      - success_patterns: mapping task_signature -> {strategy, wins, last_used, confidence}
      - failure_lessons: mapping error_signature -> {solution, tries, last_seen}
      - metadata: user preferences, counters
    """

    def __init__(self, global_file: Path = GLOBAL_MEMORY_FILE, project_file: Path = PROJECT_MEMORY_FILE):
        self.global_file = global_file
        self.project_file = project_file
        self._data = {
            "success_patterns": {},
            "failure_lessons": {},
            "metadata": {},
            "counters": {}
        }
        self._load()

    def _load(self):
        # Load global then project and merge (project overrides)
        g = _safe_read_json(self.global_file) or {}
        p = _safe_read_json(self.project_file) or {}
        # merge keys
        for k in self._data.keys():
            merged = {}
            if isinstance(g.get(k), dict):
                merged.update(g.get(k))
            if isinstance(p.get(k), dict):
                merged.update(p.get(k))
            self._data[k] = merged

    def _persist(self):
        # Write both global and project layers (project stores exact project-local; global stores global)
        # For simplicity, write merged view to both locations (keeps them in sync).
        merged = self._data
        _safe_write_json(self.global_file, merged)
        _safe_write_json(self.project_file, merged)

    def remember_success(self, task_sig: str, strategy: str, meta: dict | None = None):
        rec = self._data["success_patterns"].get(task_sig, {"wins": 0, "strategy": None, "confidence": 0.0, "last_used": None, "meta": {}})
        rec["wins"] = rec.get("wins", 0) + 1
        rec["strategy"] = strategy
        rec["last_used"] = _now_iso()
        # simple confidence: wins / (wins + 1)
        rec["confidence"] = rec["wins"] / (rec["wins"] + 1)
        if meta:
            rec_meta = rec.get("meta", {})
            rec_meta.update(meta)
            rec["meta"] = rec_meta
        self._data["success_patterns"][task_sig] = rec
        self._persist()
        _log_activity({
            "type": "success_pattern",
            "task_sig": task_sig,
            "strategy": strategy,
            "meta": meta or {},
            "time": _now_iso()
        }, human=f"[Fluency] success pattern recorded: {task_sig} -> {strategy}")

    def remember_failure(self, error_sig: str, solution: dict | None = None):
        rec = self._data["failure_lessons"].get(error_sig, {"tries": 0, "solutions": [], "last_seen": None})
        rec["tries"] = rec.get("tries", 0) + 1
        rec["last_seen"] = _now_iso()
        if solution:
            rec["solutions"].append({"solution": solution, "time": _now_iso()})
        self._data["failure_lessons"][error_sig] = rec
        self._persist()
        _log_activity({
            "type": "failure_lesson",
            "error_sig": error_sig,
            "solution": solution or {},
            "time": _now_iso()
        }, human=f"[Fluency] failure recorded: {error_sig} -> {solution}")

    def get_success(self, task_sig: str):
        return self._data["success_patterns"].get(task_sig)

    def get_failure(self, error_sig: str):
        return self._data["failure_lessons"].get(error_sig)

    def increment_counter(self, key: str):
        self._data["counters"][key] = self._data["counters"].get(key, 0) + 1
        self._persist()

    def export(self):
        return self._data.copy()


# -----------------------------
# Activity logging helpers
# -----------------------------


def _log_activity(record: dict, human: str | None = None):
    """
    Writes both a human log and a JSON activity record to both global and project locations.
    """
    # Human-readable line
    line = f"{_now_iso()} {human or record.get('type')}: {json.dumps(record, default=str, ensure_ascii=False)}"
    try:
        _append_text_log(GLOBAL_ACTIVITY_LOG, line)
        _append_text_log(PROJECT_ACTIVITY_LOG, line)
    except Exception:
        pass

    # JSON structured
    try:
        _append_json_activity(GLOBAL_ACTIVITY_JSON, record)
        _append_json_activity(PROJECT_ACTIVITY_JSON, record)
    except Exception:
        pass


# -----------------------------
# Core Perception & Conversion
# -----------------------------


def _is_pathlike(obj):
    return isinstance(obj, (str, Path))


def _has_raw(obj):
    try:
        return hasattr(obj, "raw")
    except Exception:
        return False


def _looks_like_api_wrapper(obj):
    if not isinstance(obj, dict):
        return False
    keys = set(obj.keys())
    return bool(keys & {"data", "results", "items", "payload", "cleaned_data"})


def _try_json_load(path):
    try:
        p = Path(path)
        if p.exists():
            with open(p, "r", encoding="utf-8") as f:
                return json.load(f)
    except Exception:
        try:
            return Path(path).read_text(encoding="utf-8").splitlines()
        except Exception:
            return None
    return None


def _grimoire_flatten(data, max_depth: int = DEFAULT_FLATTEN_DEPTH):
    """Conservative flatten: flattens nested lists up to max_depth; leaves non-lists untouched."""
    def _inner(el, depth):
        if depth <= 0:
            yield el
            return
        if isinstance(el, list):
            for sub in el:
                if isinstance(sub, list):
                    yield from _inner(sub, depth - 1)
                else:
                    yield sub
        else:
            yield el

    if isinstance(data, list):
        return list(_inner(data, max_depth))
    return data


def _grimoire_normalize(data):
    """
    Smart normalization:
      - If Mage-like (has .raw) -> return .raw
      - If path-like -> try simple_file.load if available, else json load
      - If API wrapper dict -> extract 'data' or 'results' intelligently
      - Else return data unchanged
    Conservative: only changes what is clearly a wrapper to avoid breaking intentional raw inputs.
    """
    # 1) unwrap .raw
    try:
        if _has_raw(data):
            return data.raw
    except Exception:
        pass

    # 2) path-like
    if _is_pathlike(data):
        try:
            # prefer simple_file.load if available
            sf = importlib.import_module("simple_file")
            if hasattr(sf, "load"):
                try:
                    out = sf.load(str(data))
                    return out
                except Exception:
                    pass
        except Exception:
            pass
        # fallback to json load
        loaded = _try_json_load(data)
        if loaded is not None:
            return loaded

    # 3) API wrapper dict
    if isinstance(data, dict) and _looks_like_api_wrapper(data):
        for candidate in ("data", "results", "items", "payload", "cleaned_data"):
            if candidate in data:
                return data[candidate]
        if len(data) == 1:
            try:
                return list(data.values())[0]
            except Exception:
                pass

    # 4) leave unchanged
    return data


# -----------------------------
# Strategy runner & self-healing
# -----------------------------


def _task_signature(module_name: str, func_name: str, args, kwargs) -> str:
    """
    Create a conservative signature for the task: module.func + hash of types & keys of inputs.
    Used to index learned patterns.
    """
    try:
        # use shapes instead of values to avoid huge keys
        def shape(x):
            if _has_raw(x):
                return ("mage",)
            if isinstance(x, dict):
                return ("dict", tuple(sorted(x.keys())))
            if isinstance(x, list):
                return ("list", len(x))
            if _is_pathlike(x):
                return ("path", str(x)[:120])
            return (type(x).__name__,)
        signature = {
            "module": module_name,
            "func": func_name,
            "args": [shape(a) for a in args],
            "kwargs": {k: shape(v) for k, v in kwargs.items()}
        }
        return _sha1_of(signature)
    except Exception:
        return _sha1_of(repr((module_name, func_name)))


def _error_signature(e: Exception) -> str:
    # Short signature for error type + message summary
    try:
        return f"{type(e).__name__}:{str(e)[:200]}"
    except Exception:
        return f"Exception:{_sha1_of(repr(e))}"


def _apply_strategies_and_record(orig_fn, module_name: str, func_name: str, mem: PersistentMemory):
    """
    Returns a wrapped function which:
      - Normalizes inputs when helpful
      - Attempts the original function
      - On failure, tries alternate strategies (unwrap .raw, flatten first arg, pass .raw explicitly)
      - Records successes/failures in memory and logs activity
    """
    @functools.wraps(orig_fn)
    def wrapped(*args, **kwargs):
        task_sig = _task_signature(module_name, func_name, args, kwargs)
        mem.increment_counter("calls")
        mem.increment_counter(f"calls::{module_name}.{func_name}")

        # Step 0: check memory for successful strategy
        learned = mem.get_success(task_sig)
        if learned and learned.get("confidence", 0.0) >= AUTO_APPLY_CONFIDENCE:
            strategy = learned.get("strategy")
            # apply strategy silently, but log
            _log_activity({
                "type": "auto_apply",
                "task_sig": task_sig,
                "strategy": strategy,
                "meta": learned.get("meta", {}),
                "time": _now_iso()
            }, human=f"[Fluency] auto-applying learned strategy for {module_name}.{func_name}: {strategy}")

            # try applying known strategy variants (if strategy encodes 'flatten' or 'use_raw')
            try:
                if strategy == "use_raw_first":
                    new_args = tuple((a.raw if _has_raw(a) else a) for a in args)
                    res = orig_fn(*new_args, **kwargs)
                    if _has_raw(res) is False:
                        mem.remember_success(task_sig, strategy)
                    return _maybe_wrap_result(res, mem)
                if strategy == "flatten_first":
                    if args:
                        new_args = ( _grimoire_flatten(_grimoire_normalize(args[0])), ) + args[1:]
                    else:
                        new_args = args
                    res = orig_fn(*new_args, **kwargs)
                    mem.remember_success(task_sig, strategy)
                    return _maybe_wrap_result(res, mem)
                # unknown strategy -> fallthrough to default attempt
            except Exception as e:
                # learned strategy failed; fall back to exploration
                _log_activity({
                    "type": "auto_apply_failed",
                    "task_sig": task_sig,
                    "strategy": strategy,
                    "error": _error_signature(e),
                    "trace": _trace_short(),
                    "time": _now_iso()
                }, human=f"[Fluency] learned strategy failed for {module_name}.{func_name}: {strategy} -> {e}")

        # Strategy exploration stack
        attempts = []
        # Candidate 0: direct call with normalized args (conservative)
        try:
            norm_args = tuple(_grimoire_normalize(a) for a in args)
            norm_kwargs = {k: _grimoire_normalize(v) for k, v in kwargs.items()}
            res = orig_fn(*norm_args, **norm_kwargs)
            # record success with strategy 'normalize_first'
            mem.remember_success(task_sig, "normalize_first", meta={"args_shape": str([type(a).__name__ for a in norm_args])})
            return _maybe_wrap_result(res, mem)
        except Exception as e0:
            attempts.append(("normalize_first", e0))

        # Candidate 1: try unwrapping .raw from first arg (if present)
        try:
            if args and _has_raw(args[0]):
                new_args = (args[0].raw, ) + args[1:]
                new_args = tuple(_grimoire_normalize(a) for a in new_args)
                res = orig_fn(*new_args, **kwargs)
                mem.remember_success(task_sig, "use_raw_first", meta={"note": "unwrapped first arg"})
                return _maybe_wrap_result(res, mem)
        except Exception as e1:
            attempts.append(("use_raw_first", e1))

        # Candidate 2: try flattening first arg (if list-like)
        try:
            if args and isinstance(_grimoire_normalize(args[0]), list):
                flat = _grimoire_flatten(_grimoire_normalize(args[0]))
                new_args = (flat, ) + tuple(_grimoire_normalize(a) for a in args[1:])
                res = orig_fn(*new_args, **kwargs)
                mem.remember_success(task_sig, "flatten_first", meta={"flatten_depth": DEFAULT_FLATTEN_DEPTH})
                return _maybe_wrap_result(res, mem)
        except Exception as e2:
            attempts.append(("flatten_first", e2))

        # Candidate 3: try calling with fully raw args (no normalization)
        try:
            res = orig_fn(*args, **kwargs)
            mem.remember_success(task_sig, "call_raw", meta={"note": "raw_call_succeeded"})
            return _maybe_wrap_result(res, mem)
        except Exception as e3:
            attempts.append(("call_raw", e3))

        # Candidate 4: last resort - try each arg unwrapped if possible
        try:
            new_args = []
            for a in args:
                if _has_raw(a):
                    new_args.append(a.raw)
                else:
                    new_args.append(_grimo_normalize_try(a))
            res = orig_fn(*tuple(new_args), **kwargs)
            mem.remember_success(task_sig, "mixed_unwrap", meta={"note": "mixed_unwrap_last_resort"})
            return _maybe_wrap_result(res, mem)
        except Exception as e4:
            attempts.append(("mixed_unwrap", e4))

        # If we reach here, everything failed. Record failure with traces and suggestions.
        err_sig = _error_signature(attempts[-1][1] if attempts else Exception("unknown"))
        mem.remember_failure(err_sig, solution={"attempts": [ {"strategy": s, "error": str(type(ex).__name__) + ':' + str(ex)[:200]} for s, ex in attempts ]})
        _log_activity({
            "type": "call_failure",
            "task_sig": task_sig,
            "module": module_name,
            "function": func_name,
            "attempts": [ {"strategy": s, "error": str(type(ex).__name__) + ':' + str(ex)[:200]} for s, ex in attempts ],
            "time": _now_iso()
        }, human=f"[Fluency] ERROR {module_name}.{func_name} failed after strategies: {[s for s, _ in attempts]}. See activity.json for details.")

        # Raise last exception to keep behavior consistent with original API (but after logging)
        raise attempts[-1][1]

    return wrapped


def _maybe_wrap_result(res, mem: PersistentMemory):
    """
    If result is not Mage-like and is list/dict, attempt to wrap using json_mage.modify (if available),
    else return as-is. Also record what was returned.
    """
    try:
        # If result has raw already, return
        if _has_raw(res):
            mem.increment_counter("returns_mage_like")
            return res
    except Exception:
        pass

    # If result is list/dict -> try to wrap with json_mage.modify
    if isinstance(res, (list, dict)):
        try:
            mod = importlib.import_module("json_mage")
            if hasattr(mod, "modify"):
                wrapped = mod.modify(res)
                mem.increment_counter("returns_wrapped_by_modify")
                return wrapped
        except Exception:
            pass
    # else return as-is
    mem.increment_counter("returns_raw_python")
    return res


def _grimo_normalize_try(x):
    """A best-effort normalize for mixed-unwrapping strategy."""
    try:
        return _grimoire_normalize(x)
    except Exception:
        try:
            if _has_raw(x):
                return x.raw
        except Exception:
            pass
    return x

# -----------------------------
# Module patching utilities
# -----------------------------


def _wrap_module_functions(modname: str, mem: PersistentMemory, names: list | None = None):
    """
    Attempt to import module and wrap public callables.
    If `names` provided, only wrap those names.
    """
    try:
        mod = importlib.import_module(modname)
    except Exception:
        _log_activity({"type": "module_missing", "module": modname, "time": _now_iso()},
                      human=f"[Fluency] {modname} not found - skipping patch.")
        return

    GrimoireBridge.connect(modname, mod)
    # Determine items to patch
    items = []
    for name, obj in list(vars(mod).items()):
        if names and name not in names:
            continue
        if name.startswith("_"):
            continue
        if callable(obj):
            items.append((name, obj))

    # If module exposes a class with __call__ (e.g., LoopOn instances), try to wrap its methods too
    for name, cls in inspect.getmembers(mod, inspect.isclass):
        # skip internal classes
        if name.startswith("_"):
            continue
        # wrap callables on class if common names
        try:
            for m in ("__call__", "all", "get", "filter"):
                if hasattr(cls, m):
                    orig = getattr(cls, m)
                    wrapped = _apply_strategies_and_record(orig, modname, f"{name}.{m}", mem)
                    try:
                        setattr(cls, m, wrapped)
                    except Exception:
                        pass
        except Exception:
            pass

    # Wrap top-level functions we found
    for name, obj in items:
        try:
            wrapped = _apply_strategies_and_record(obj, modname, name, mem)
            setattr(mod, name, wrapped)
            _log_activity({"type": "patched", "module": modname, "name": name, "time": _now_iso()},
                          human=f"[Fluency] patched {modname}.{name}")
        except Exception:
            _log_activity({"type": "patch_error", "module": modname, "name": name, "time": _now_iso(), "trace": _trace_short()},
                          human=f"[Fluency] failed to patch {modname}.{name}")


def _patch_known_modules(mem: PersistentMemory):
    # Specific names to patch for known modules
    # json_mage.modify, loops.loopon, simple_file.save/load are prioritized
    for modname in TARGET_MODULES:
        # For json_mage, patch 'modify' and class methods 'all','get','filter','find'
        if modname == "json_mage":
            try:
                mod = importlib.import_module(modname)
            except Exception:
                _log_activity({"type": "module_missing", "module": modname, "time": _now_iso()},
                              human=f"[Fluency] {modname} not present.")
                continue
            GrimoireBridge.connect(modname, mod)
            if hasattr(mod, "modify"):
                orig_modify = getattr(mod, "modify")
                # Wrap modify
                wrapped_modify = _apply_strategies_and_record(orig_modify, modname, "modify", mem)
                try:
                    setattr(mod, "modify", wrapped_modify)
                    _log_activity({"type": "patched", "module": modname, "name": "modify", "time": _now_iso()},
                                  human=f"[Fluency] patched {modname}.modify")
                except Exception:
                    pass
            # Try to wrap common class methods if any class exists
            common_methods = ["all", "get", "filter", "find", "first", "last"]
            for _, cls in inspect.getmembers(mod, inspect.isclass):
                try:
                    for m in common_methods:
                        if hasattr(cls, m):
                            orig = getattr(cls, m)
                            wrapped = _apply_strategies_and_record(orig, modname, f"{cls.__name__}.{m}", mem)
                            try:
                                setattr(cls, m, wrapped)
                            except Exception:
                                pass
                except Exception:
                    pass
        else:
            # default wrap of public functions
            _wrap_module_functions(modname, mem)

# -----------------------------
# Grimoire Bridge & Public API
# -----------------------------


class GrimoireBridge:
    """
    Shared consciousness for tools. Holds in-memory copy of memory and quick helper apis.
    Use GrimoireBridge.remember / recall to interact with memory directly.
    """
    _memory = None  # PersistentMemory instance
    _tools = {}

    @classmethod
    def init_memory(cls, mem: PersistentMemory):
        cls._memory = mem

    @classmethod
    def remember(cls, key: str, value, scope: str = "global"):
        if cls._memory is None:
            return None
        cls._memory._data["metadata"][key] = {"value": value, "time": _now_iso(), "scope": scope}
        cls._memory._persist()
        _log_activity({"type": "bridge_remember", "key": key, "scope": scope, "time": _now_iso()},
                      human=f"[GrimoireBridge] remembered {key} in {scope}")

    @classmethod
    def recall(cls, key: str, default=None):
        if cls._memory is None:
            return default
        return cls._memory._data.get("metadata", {}).get(key, {}).get("value", default)

    @classmethod
    def connect(cls, name: str, tool_obj):
        cls._tools[name] = tool_obj
        _log_activity({"type": "bridge_connect", "tool": name, "time": _now_iso()}, human=f"[GrimoireBridge] connected {name}")
        return tool_obj

    @classmethod
    def fetch_tool(cls, name: str):
        return cls._tools.get(name)

    @classmethod
    def execute_flow(cls, data, *operations):
        """
        Lightweight orchestrator helper (convenience).
        operations can be callables or strings with simple routes:
          - 'json.all:stats' -> call modify(data).all('stats')
          - 'loopon:base_stat'
          - 'simple_file:save::name'
        This helper will normalize inputs when helpful and apply learned strategies if present.
        """
        current = _grimoire_normalize(data)
        mem = cls._memory
        for op in operations:
            if callable(op):
                current = op(current)
            elif isinstance(op, str):
                # simple parser
                if op.startswith("json."):
                    # support json.all("stats") format or json.all:stats
                    try:
                        part = op.split(".", 1)[1]
                        if "(" in part and part.endswith(")"):
                            fn = part.split("(")[0]
                            arg = part.split("(", 1)[1].rstrip(")").strip('\'"')
                        else:
                            fn, _, arg = part.partition(":")
                            arg = arg or None
                        mod = importlib.import_module("json_mage")
                        mage = getattr(mod, "modify")(current)
                        if arg:
                            current = getattr(mage, fn)(arg)
                        else:
                            current = getattr(mage, fn)()
                    except Exception as e:
                        _log_activity({"type": "execute_flow_error", "op": op, "error": str(e), "time": _now_iso()},
                                      human=f"[Fluency] execute_flow json.{op} failed: {e}")
                elif op.startswith("loopon."):
                    try:
                        key = op.split(".", 1)[1]
                        mod = importlib.import_module("loops")
                        fn = getattr(mod, "loopon")
                        current = fn(current, key)
                    except Exception as e:
                        _log_activity({"type": "execute_flow_error", "op": op, "error": str(e), "time": _now_iso()},
                                      human=f"[Fluency] execute_flow loopon.{op} failed: {e}")
                elif op.startswith("simple_file.save"):
                    try:
                        parts = op.split("::")
                        name = parts[1] if len(parts) > 1 else "auto"
                        mod = importlib.import_module("simple_file")
                        save_fn = getattr(mod, "save")
                        save_fn(name, current)
                    except Exception as e:
                        _log_activity({"type": "execute_flow_error", "op": op, "error": str(e), "time": _now_iso()},
                                      human=f"[Fluency] execute_flow simple_file.save failed: {e}")
                else:
                    # unknown string op - ignore
                    pass
            # normalize between steps
            current = _grimoire_normalize(current)
        return current


# -----------------------------
# Activation
# -----------------------------


_already_activated = False


def activate_tool_fluency():
    global _already_activated
    if _already_activated:
        return
    _already_activated = True

    # Initialize persistent memory
    mem = PersistentMemory()
    GrimoireBridge.init_memory(mem)

    # Patch known modules
    try:
        _patch_known_modules(mem)
    except Exception as e:
        _log_activity({"type": "patch_failure", "error": str(e), "time": _now_iso()}, human=f"[Fluency] patching failed: {e}")

    # Expose conveniences in module globals
    globals().update({
        "GrimoireBridge": GrimoireBridge,
        "_grimoire_normalize": _grimoire_normalize,
        "_grimoire_flatten": _grimoire_flatten,
        "PersistentMemory": PersistentMemory
    })

    _log_activity({"type": "activated", "time": _now_iso()}, human="[Fluency] GRIMOIRE FLUENCY LAYER ACTIVATED")
    # Friendly print once on import
    try:
        print("💀 GRIMOIRE FLUENCY LAYER ACTIVATED 💀")
    except Exception:
        pass


# Activate as soon as module is imported
activate_tool_fluency()

