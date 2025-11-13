import os
import json
import sys
import types
from pathlib import Path

import pytest

from inceptum import config
from inceptum.require import require


def write_json(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data), encoding="utf-8")


def make_package_chain(fullname: str):
    """
    Ensure all parents exist as packages in sys.modules with __path__ set,
    and return the leaf module name that can be used for import.
    """
    parts = fullname.split('.')
    for i in range(1, len(parts)):
        pkg_name = '.'.join(parts[:i])
        if pkg_name not in sys.modules:
            pkg = types.ModuleType(pkg_name)
            pkg.__path__ = []  # mark as package
            sys.modules[pkg_name] = pkg


def create_module(fullname: str, **attrs):
    """
    Create a module (and its parents as packages) in sys.modules.
    """
    make_package_chain(fullname)
    mod = types.ModuleType(fullname)
    for k, v in attrs.items():
        setattr(mod, k, v)
    sys.modules[fullname] = mod
    return mod


def cleanup_modules(names):
    for n in names:
        sys.modules.pop(n, None)


def test_require_uses_prefixes_when_base_missing(monkeypatch, tmp_path):
    base = tmp_path / "cfg"
    monkeypatch.setenv("INCEPTUM", str(base))
    # Configure prefixes
    write_json(base / "any" / "inceptum.json", {"prefixes": ["pfx"]})

    created = []
    try:
        create_module("pfx")
        created.append("pfx")
        m = create_module("pfx.xmod", token="OK")
        created.append("pfx.xmod")

        resolved = require("xmod")
        assert resolved is m
        assert getattr(resolved, "token") == "OK"
    finally:
        cleanup_modules(created)


def test_require_prefers_unprefixed_if_present(monkeypatch, tmp_path):
    base = tmp_path / "cfg2"
    monkeypatch.setenv("INCEPTUM", str(base))
    write_json(base / "any" / "inceptum.json", {"prefixes": ["pfx"]})

    created = []
    try:
        # Both unprefixed and prefixed exist - unprefixed should win
        m0 = create_module("zmod", tag="base")
        created.append("zmod")
        create_module("pfx")
        created.append("pfx")
        m1 = create_module("pfx.zmod", tag="prefixed")
        created.append("pfx.zmod")

        resolved = require("zmod")
        assert resolved is m0
        assert getattr(resolved, "tag") == "base"
    finally:
        cleanup_modules(created)


def test_toplevel_module_mapping_still_applies(monkeypatch, tmp_path):
    base = tmp_path / "cfg3"
    monkeypatch.setenv("INCEPTUM", str(base))
    write_json(base / "any" / "inceptum.json", {"module": {"wps": "leptonix_wps"}})

    created = []
    try:
        m = create_module("leptonix_wps", sentinel=1)
        created.append("leptonix_wps")

        resolved = require("wps")
        assert resolved is m
        assert getattr(resolved, "sentinel") == 1
    finally:
        cleanup_modules(created)


def test_alias_mapping_resolves_to_module(monkeypatch, tmp_path):
    base = tmp_path / "cfg4"
    monkeypatch.setenv("INCEPTUM", str(base))
    write_json(base / "any" / "inceptum.json", {"registry": {"alias": "pkg.bar"}})

    created = []
    try:
        create_module("pkg")
        created.append("pkg")
        m = create_module("pkg.bar", value=42)
        created.append("pkg.bar")

        resolved = require("alias")
        assert resolved is m
        assert getattr(resolved, "value") == 42
    finally:
        cleanup_modules(created)


def test_function_mode_with_prefixes(monkeypatch, tmp_path):
    base = tmp_path / "cfg5"
    monkeypatch.setenv("INCEPTUM", str(base))
    write_json(base / "any" / "inceptum.json", {"prefixes": ["pfx"]})

    created = []
    try:
        # pfx.tool.cli.main should be discovered when require('tool', cli=True)
        create_module("pfx")
        created.append("pfx")
        create_module("pfx.tool")
        created.append("pfx.tool")
        create_module("pfx.tool.cli")
        created.append("pfx.tool.cli")

        def main():
            return 123

        m = create_module("pfx.tool.cli.main")
        setattr(m, "main", main)
        created.append("pfx.tool.cli.main")

        fn = require("tool", cli=True)
        assert callable(fn)
        assert fn() == 123
    finally:
        cleanup_modules(created)


def test_require_prefers_attribute_over_submodule(monkeypatch, tmp_path):
    base = tmp_path / "cfg_attr"
    monkeypatch.setenv("INCEPTUM", str(base))

    created = []
    try:
        # util has an attribute 'isiterator' and there is also a submodule util.isiterator.
        # The attribute should be preferred.
        def isiterator_fn():
            return "ATTR"

        util_mod = create_module("util", isiterator=isiterator_fn)
        created.append("util")
        sub_mod = create_module("util.isiterator", marker="SUBMODULE")
        created.append("util.isiterator")

        resolved = require("util.isiterator")
        assert resolved is isiterator_fn
        assert resolved() == "ATTR"
    finally:
        cleanup_modules(created)


def test_require_dotted_import_when_attribute_missing(monkeypatch, tmp_path):
    base = tmp_path / "cfg_attr_missing"
    monkeypatch.setenv("INCEPTUM", str(base))

    created = []
    try:
        # util exists but does not expose 'isiterator' attribute, only the submodule exists.
        create_module("util")
        created.append("util")
        sub_mod = create_module("util.isiterator", marker="SUBMODULE")
        created.append("util.isiterator")

        resolved = require("util.isiterator")
        assert resolved is sub_mod
        assert getattr(resolved, "marker") == "SUBMODULE"
    finally:
        cleanup_modules(created)


def test_alias_and_dotted_function_resolution_no_prefixed_alias(monkeypatch, tmp_path):
    base = tmp_path / "cfg_mark"
    monkeypatch.setenv("INCEPTUM", str(base))
    # Aliased seed will NOT be re-prefixed, so we must include the prefix in the alias value
    write_json(
        base / "any" / "inceptum.json",
        {
            "prefixes": ["my"],
            "module": {"wps": "leptonix_wps"},
            "registry": {"markdown": "my.markdown.from_html"},
        },
    )

    created = []
    try:
        # Create packages and modules
        create_module("my")
        created.append("my")

        def from_html(x=1):
            return ("OK", x)

        # Parent module re-exports the function
        create_module("my.markdown", from_html=from_html)
        created.append("my.markdown")

        # Leaf module also defines the function
        create_module("my.markdown.from_html", from_html=from_html)
        created.append("my.markdown.from_html")

        # Direct dotted resolution should return the function via prefix probing
        fn1 = require("markdown.from_html")
        assert callable(fn1)
        assert fn1 is from_html
        assert fn1(2) == ("OK", 2)

        # Alias resolution should also return the same function - no added prefixing
        fn2 = require("markdown")
        assert callable(fn2)
        assert fn2 is from_html
    finally:
        cleanup_modules(created)


def test_dotted_prefers_callable_from_prefixed_over_plain_module(monkeypatch, tmp_path):
    base = tmp_path / "cfg_epub"
    monkeypatch.setenv("INCEPTUM", str(base))
    write_json(base / "any" / "inceptum.json", {"prefixes": ["my"]})

    created = []
    try:
        # Unprefixed package 'epub' with a submodule 'content' but no callable named 'content'
        create_module("epub")
        created.append("epub")
        create_module("epub.content", marker="UNPREF_SUBMODULE")
        created.append("epub.content")

        # Prefixed package with a real function and a re-export at package level
        create_module("my")
        created.append("my")

        def content():
            return "FUNCTION"

        create_module("my.epub", content=content)  # re-export at package level
        created.append("my.epub")
        create_module("my.epub.content", content=content)
        created.append("my.epub.content")

        # For dotted name, prefer the callable from the prefixed candidate over the plain module
        resolved = require("epub.content")
        assert callable(resolved)
        assert resolved is content
        assert resolved() == "FUNCTION"

        # For simple un-dotted name, still prefer the unprefixed module as before
        resolved_pkg = require("epub")
        assert resolved_pkg is sys.modules["epub"]
    finally:
        cleanup_modules(created)


def test_special_case_config_toggle(monkeypatch, tmp_path):
    base = tmp_path / "cfg_toggle"
    monkeypatch.setenv("INCEPTUM", str(base))
    # By default, special case is off
    write_json(base / "any" / "inceptum.json", {})

    created = []
    try:
        # Provide a dummy 'config' module that would be found if special-casing is off
        m = create_module("config", marker="MOD")
        created.append("config")

        # With special_config off, require('config') returns the module
        obj = require("config")
        assert obj is m
        assert getattr(obj, "marker") == "MOD"

        # Turn special-casing on
        write_json(base / "any" / "inceptum.json", {"require": {"special_config": True}})

        # Cache in config() is per base/env/host/name - switching file is OK in tests
        from inceptum.config import _CACHE  # type: ignore
        _CACHE.clear()

        obj2 = require("config")
        # Expect the function 'config' from inceptum.config
        from inceptum import config as config_fn
        assert obj2 is config_fn
    finally:
        cleanup_modules(created)


def test_alias_cycle_does_not_loop_and_raises(monkeypatch, tmp_path):
    base = tmp_path / "cfg_cycle"
    monkeypatch.setenv("INCEPTUM", str(base))
    write_json(base / "any" / "inceptum.json", {"registry": {"a": "b", "b": "a"}})

    with pytest.raises(ModuleNotFoundError):
        require("a")


def test_variadic_segments_equivalent_to_dotted(monkeypatch, tmp_path):
    base = tmp_path / "cfg_varargs"
    monkeypatch.setenv("INCEPTUM", str(base))
    write_json(base / "any" / "inceptum.json", {})

    created = []
    try:
        # Create database.abc module exposing a callable "SQL"
        create_module("database")
        created.append("database")

        def SQL():
            return "OK"

        create_module("database.abc", SQL=SQL)
        created.append("database.abc")

        # Dotted form
        fn1 = require("database.abc.SQL")
        assert callable(fn1)
        assert fn1() == "OK"

        # Variadic segments form
        fn2 = require("database", "abc", "SQL")
        assert callable(fn2)
        assert fn2() == "OK"
        assert fn1 is fn2
    finally:
        cleanup_modules(created)


def test_require_stops_on_syntax_error(monkeypatch, tmp_path):
    base = tmp_path / "cfg_syntax"
    monkeypatch.setenv("INCEPTUM", str(base))
    # Prefix to simulate a fallback that should NOT be used
    write_json(base / "any" / "inceptum.json", {"prefixes": ["pfx"]})

    # Put a real file on disk with a syntax error
    srcdir = tmp_path / "src_syntax"
    srcdir.mkdir()
    (srcdir / "badmod.py").write_text("def broken(:\n    pass\n", encoding="utf-8")
    monkeypatch.syspath_prepend(str(srcdir))

    created = []
    try:
        # Create a working prefixed fallback that must NOT be used
        create_module("pfx")
        created.append("pfx")
        create_module("pfx.badmod", marker="PREF_OK")
        created.append("pfx.badmod")

        with pytest.raises(SyntaxError):
            require("badmod")
    finally:
        cleanup_modules(created)
        sys.modules.pop("badmod", None)


def test_require_stops_on_internal_missing_dependency(monkeypatch, tmp_path):
    base = tmp_path / "cfg_missing_dep"
    monkeypatch.setenv("INCEPTUM", str(base))
    # Prefix to simulate a fallback that should NOT be used
    write_json(base / "any" / "inceptum.json", {"prefixes": ["pfx"]})

    # Put a real file on disk that imports a non-existent module
    srcdir = tmp_path / "src_missing_dep"
    srcdir.mkdir()
    (srcdir / "baddep.py").write_text("import __this_module_does_not_exist__\nX = 1\n", encoding="utf-8")
    monkeypatch.syspath_prepend(str(srcdir))

    created = []
    try:
        # Create a working prefixed fallback that must NOT be used
        create_module("pfx")
        created.append("pfx")
        create_module("pfx.baddep", marker="PREF_OK")
        created.append("pfx.baddep")

        # ModuleNotFoundError is raised for the missing dependency; we should fail fast
        with pytest.raises(ModuleNotFoundError):
            require("baddep")
    finally:
        cleanup_modules(created)
        sys.modules.pop("baddep", None)
