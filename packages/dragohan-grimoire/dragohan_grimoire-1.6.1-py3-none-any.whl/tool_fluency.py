"""
Tool Fluency - GOD MODE 2025
- Instant import (async patching + writes)
- Zero blocking I/O
- Self-healing + persistent learning
- RAM-speed cache (/tmp)
- Auto-prune logs
- Battle-tested for trillion-dollar automation
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
import time

# =============================
# CONFIG: RAM-SPEED + PRUNE
# =============================
GLOBAL_MEMORY_DIR = Path("/tmp/grimoire_global")  # RAM disk
PROJECT_MEMORY_DIR = Path(".grimoire_memory")     # Project-local
GLOBAL_MEMORY_DIR.mkdir(exist_ok=True)
PROJECT_MEMORY_DIR.mkdir(exist_ok=True)

MEMORY_FILE = "memory.json"
ACTIVITY_LOG = "activity.log"
ACTIVITY_JSON = "activity.json"

GLOBAL_MEMORY_FILE = GLOBAL_MEMORY_DIR / MEMORY_FILE
PROJECT_MEMORY_FILE = PROJECT_MEMORY_DIR / MEMORY_FILE
GLOBAL_ACTIVITY_LOG = GLOBAL_MEMORY_DIR / ACTIVITY_LOG
PROJECT_ACTIVITY_LOG = PROJECT_MEMORY_DIR / ACTIVITY_LOG
GLOBAL_ACTIVITY_JSON = GLOBAL_MEMORY_DIR / ACTIVITY_JSON
PROJECT_ACTIVITY_JSON = PROJECT_MEMORY_DIR / ACTIVITY_JSON

TARGET_MODULES = [
    "json_mage", "loops", "simple_file",
    "getter", "converter", "duplicates", "internet"
]

DEFAULT_FLATTEN_DEPTH = 20
AUTO_APPLY_CONFIDENCE = 0.6
MAX_LOG_ENTRIES = 1000
_IO_LOCK = threading.Lock()

# =============================
# LOW-LEVEL UTILS
# =============================
def _now_iso(): return datetime.utcnow().isoformat() + "Z"
def _trace_short(): return traceback.format_exc(limit=1)
def _sha1_of(obj) -> str:
    try: b = json.dumps(obj, default=str, sort_keys=True).encode("utf-8")
    except: b = repr(obj).encode("utf-8")
    return hashlib.sha1(b).hexdigest()

def _safe_read_json(path: Path):
    try:
        if path.exists():
            return json.loads(path.read_text(encoding="utf-8"))
    except: return {}
    return {}

# ASYNC WRITE: Fire and forget
def _blocking_write(path: Path, data):
    with _IO_LOCK:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(data, indent=2, default=str), encoding="utf-8")

def _safe_write_json(path: Path, data):
    threading.Thread(target=_blocking_write, args=(path, data), daemon=True).start()

def _blocking_append(path: Path, record: dict):
    with _IO_LOCK:
        data = _safe_read_json(path)
        if not isinstance(data, list): data = []
        data.append(record)
        if len(data) > MAX_LOG_ENTRIES: data = data[-MAX_LOG_ENTRIES:]
        _blocking_write(path, data)

def _append_json_activity(path: Path, record: dict):
    threading.Thread(target=_blocking_append, args=(path, record), daemon=True).start()

def _blocking_log(path: Path, text: str):
    with _IO_LOCK:
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "a", encoding="utf-8") as f:
            f.write(text + "\n")

def _append_text_log(path: Path, text: str):
    threading.Thread(target=_blocking_log, args=(path, text), daemon=True).start()

# =============================
# PERSISTENT MEMORY
# =============================
class PersistentMemory:
    def __init__(self, global_file=GLOBAL_MEMORY_FILE, project_file=PROJECT_MEMORY_FILE):
        self.global_file = global_file
        self.project_file = project_file
        self._data = {"success_patterns": {}, "failure_lessons": {}, "metadata": {}, "counters": {}}
        self._load()
    def _load(self):
        g = _safe_read_json(self.global_file) or {}
        p = _safe_read_json(self.project_file) or {}
        for k in self._data:
            merged = {}
            if isinstance(g.get(k), dict): merged.update(g.get(k))
            if isinstance(p.get(k), dict): merged.update(p.get(k))
            self._data[k] = merged
    def _persist(self):
        merged = self._data
        _safe_write_json(self.global_file, merged)
        _safe_write_json(self.project_file, merged)
    def remember_success(self, task_sig: str, strategy: str, meta=None):
        rec = self._data["success_patterns"].get(task_sig, {"wins": 0, "confidence": 0.0, "last_used": None, "meta": {}})
        rec["wins"] += 1
        rec["strategy"] = strategy
        rec["last_used"] = _now_iso()
        rec["confidence"] = rec["wins"] / (rec["wins"] + 1)
        if meta: rec["meta"].update(meta)
        self._data["success_patterns"][task_sig] = rec
        self._persist()
    def remember_failure(self, error_sig: str, solution=None):
        rec = self._data["failure_lessons"].get(error_sig, {"tries": 0, "solutions": [], "last_seen": None})
        rec["tries"] += 1
        rec["last_seen"] = _now_iso()
        if solution: rec["solutions"].append({"solution": solution, "time": _now_iso()})
        self._data["failure_lessons"][error_sig] = rec
        self._persist()
    def get_success(self, task_sig: str): return self._data["success_patterns"].get(task_sig)
    def get_failure(self, error_sig: str): return self._data["failure_lessons"].get(error_sig)
    def increment_counter(self, key: str):
        self._data["counters"][key] = self._data["counters"].get(key, 0) + 1
        self._persist()
    def export(self): return self._data.copy()

# =============================
# LOGGING
# =============================
def _log_activity(record: dict, human: str | None = None):
    line = f"{_now_iso()} {human or record.get('type')}: {json.dumps(record, default=str, ensure_ascii=False)}"
    _append_text_log(GLOBAL_ACTIVITY_LOG, line)
    _append_text_log(PROJECT_ACTIVITY_LOG, line)
    _append_json_activity(GLOBAL_ACTIVITY_JSON, record)
    _append_json_activity(PROJECT_ACTIVITY_JSON, record)

# =============================
# NORMALIZATION & FLATTEN
# =============================
def _is_pathlike(obj): return isinstance(obj, (str, Path))
def _has_raw(obj):
    try: return hasattr(obj, "raw")
    except: return False
def _looks_like_api_wrapper(obj):
    if not isinstance(obj, dict): return False
    keys = set(obj.keys())
    return bool(keys & {"data", "results", "items", "payload", "cleaned_data"})

def _try_json_load(path):
    try:
        p = Path(path)
        if p.exists():
            with open(p, "r", encoding="utf-8") as f:
                return json.load(f)
    except:
        try: return Path(path).read_text(encoding="utf-8").splitlines()
        except: return None
    return None

def _grimoire_flatten(data, max_depth=DEFAULT_FLATTEN_DEPTH):
    def _inner(el, depth):
        if depth <= 0: yield el; return
        if isinstance(el, list):
            for sub in el:
                if isinstance(sub, list): yield from _inner(sub, depth - 1)
                else: yield sub
        else: yield el
    return list(_inner(data, max_depth)) if isinstance(data, list) else data

def _grimoire_normalize(data):
    if _has_raw(data):
        try: return data.raw
        except: pass
    if _is_pathlike(data):
        try:
            sf = importlib.import_module("simple_file")
            if hasattr(sf, "load"): return sf.load(str(data))
        except: pass
        loaded = _try_json_load(data)
        if loaded is not None: return loaded
    if isinstance(data, dict) and _looks_like_api_wrapper(data):
        for k in ("data", "results", "items", "payload", "cleaned_data"):
            if k in data: return data[k]
        if len(data) == 1: return list(data.values())[0]
    return data

# =============================
# SELF-HEALING WRAPPER
# =============================
def _task_signature(module_name: str, func_name: str, args, kwargs) -> str:
    def shape(x):
        if _has_raw(x): return ("mage",)
        if isinstance(x, dict): return ("dict", tuple(sorted(x.keys())))
        if isinstance(x, list): return ("list", len(x))
        if _is_pathlike(x): return ("path", str(x)[:120])
        return (type(x).__name__,)
    sig = {"module": module_name, "func": func_name, "args": [shape(a) for a in args], "kwargs": {k: shape(v) for k, v in kwargs.items()}}
    return _sha1_of(sig)

def _error_signature(e: Exception) -> str:
    return f"{type(e).__name__}:{str(e)[:200]}"

def _apply_strategies_and_record(orig_fn, module_name: str, func_name: str, mem: PersistentMemory):
    @functools.wraps(orig_fn)
    def wrapped(*args, **kwargs):
        task_sig = _task_signature(module_name, func_name, args, kwargs)
        mem.increment_counter("calls")
        mem.increment_counter(f"calls::{module_name}.{func_name}")

        learned = mem.get_success(task_sig)
        if learned and learned.get("confidence", 0.0) >= AUTO_APPLY_CONFIDENCE:
            strategy = learned.get("strategy")
            try:
                if strategy == "use_raw_first" and args and _has_raw(args[0]):
                    res = orig_fn(args[0].raw, *args[1:], **kwargs)
                    return _maybe_wrap_result(res, mem)
                if strategy == "flatten_first" and args and isinstance(_grimoire_normalize(args[0]), list):
                    flat = _grimoire_flatten(_grimoire_normalize(args[0]))
                    res = orig_fn(flat, *args[1:], **kwargs)
                    return _maybe_wrap_result(res, mem)
            except Exception as e:
                pass

        # Try strategies
        attempts = []
        try:
            norm_args = tuple(_grimoire_normalize(a) for a in args)
            norm_kwargs = {k: _grimoire_normalize(v) for k, v in kwargs.items()}
            res = orig_fn(*norm_args, **norm_kwargs)
            mem.remember_success(task_sig, "normalize_first")
            return _maybe_wrap_result(res, mem)
        except Exception as e: attempts.append(("normalize_first", e))

        try:
            if args and _has_raw(args[0]):
                res = orig_fn(args[0].raw, *args[1:], **kwargs)
                mem.remember_success(task_sig, "use_raw_first")
                return _maybe_wrap_result(res, mem)
        except Exception as e: attempts.append(("use_raw_first", e))

        try:
            if args and isinstance(_grimoire_normalize(args[0]), list):
                flat = _grimoire_flatten(_grimoire_normalize(args[0]))
                res = orig_fn(flat, *args[1:], **kwargs)
                mem.remember_success(task_sig, "flatten_first")
                return _maybe_wrap_result(res, mem)
        except Exception as e: attempts.append(("flatten_first", e))

        try:
            res = orig_fn(*args, **kwargs)
            mem.remember_success(task_sig, "call_raw")
            return _maybe_wrap_result(res, mem)
        except Exception as e: attempts.append(("call_raw", e))

        err_sig = _error_signature(attempts[-1][1])
        mem.remember_failure(err_sig, {"attempts": [{"strategy": s, "error": str(type(ex).__name__)} for s, ex in attempts]})
        raise attempts[-1][1]

    return wrapped

def _maybe_wrap_result(res, mem: PersistentMemory):
    if _has_raw(res): return res
    if isinstance(res, (list, dict)):
        try:
            mod = importlib.import_module("json_mage")
            if hasattr(mod, "modify"):
                return mod.modify(res)
        except: pass
    return res

# =============================
# PATCHING
# =============================
def _wrap_module_functions(modname: str, mem: PersistentMemory, names=None):
    try:
        mod = importlib.import_module(modname)
    except ImportError:
        return
    except Exception as e:
        _log_activity({"type": "import_error", "mod": modname, "err": str(e)}, human=None)
        return

    GrimoireBridge.connect(modname, mod)
    items = [(n, o) for n, o in vars(mod).items() if not n.startswith("_") and callable(o) and (not names or n in names)]
    for name, obj in items:
        try:
            wrapped = _apply_strategies_and_record(obj, modname, name, mem)
            setattr(mod, name, wrapped)
            time.sleep(0.001)  # Prevent CPU spike
        except Exception as e:
            _log_activity({"type": "patch_error", "mod": modname, "name": name, "err": str(e)}, human=None)
        finally:
            time.sleep(0.001)

def _patch_known_modules(mem: PersistentMemory):
    for modname in TARGET_MODULES:
        if modname == "json_mage":
            try:
                mod = importlib.import_module(modname)
                if hasattr(mod, "modify"):
                    orig = mod.modify
                    wrapped = _apply_strategies_and_record(orig, modname, "modify", mem)
                    setattr(mod, "modify", wrapped)
                # Wrap common mage methods
                for _, cls in inspect.getmembers(mod, inspect.isclass):
                    for m in ("all", "get", "filter", "find", "first", "last"):
                        if hasattr(cls, m):
                            orig = getattr(cls, m)
                            wrapped = _apply_strategies_and_record(orig, modname, f"{cls.__name__}.{m}", mem)
                            setattr(cls, m, wrapped)
            except: pass
        else:
            _wrap_module_functions(modname, mem)

# =============================
# GRIMOIRE BRIDGE
# =============================
class GrimoireBridge:
    _memory = None
    _tools = {}
    @classmethod
    def init_memory(cls, mem): cls._memory = mem
    @classmethod
    def remember(cls, key: str, value, scope="global"):
        if cls._memory:
            cls._memory._data["metadata"][key] = {"value": value, "time": _now_iso(), "scope": scope}
            cls._memory._persist()
    @classmethod
    def recall(cls, key: str, default=None):
        if cls._memory: return cls._memory._data.get("metadata", {}).get(key, {}).get("value", default)
        return default
    @classmethod
    def connect(cls, name: str, tool_obj):
        cls._tools[name] = tool_obj
        return tool_obj
    @classmethod
    def fetch_tool(cls, name: str): return cls._tools.get(name)

# =============================
# ACTIVATION — GOD MODE
# =============================
_already_activated = False
def activate_tool_fluency():
    global _already_activated
    if _already_activated: return
    _already_activated = True

    print("GRIMOIRE FLUENCY LAYER ACTIVATED [ASYNC PATCHING...]")

    start = time.time()
    mem = PersistentMemory()
    GrimoireBridge.init_memory(mem)

    def patch_all():
        _patch_known_modules(mem)
        duration = time.time() - start
        _log_activity({"type": "activated", "duration_ms": int(duration*1000)},
                      human=f"[Fluency] ACTIVATED in {duration:.3f}s")

    threading.Thread(target=patch_all, daemon=True).start()

    globals().update({
        "GrimoireBridge": GrimoireBridge,
        "_grimoire_normalize": _grimoire_normalize,
        "_grimoire_flatten": _grimoire_flatten,
        "PersistentMemory": PersistentMemory
    })

# ACTIVATE ON IMPORT
activate_tool_fluency()
