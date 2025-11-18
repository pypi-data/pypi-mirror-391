#!/usr/bin/env python3
# tests/test_cst_utils.py

import unittest
from pathlib import Path

import libcst as cst
import libcst.metadata as md
from import_surgeon.modules.cst_utils import (
    DottedReplacer,
    ImportReplacer,
    _attr_to_dotted,
    _import_alias_name,
    _module_to_str,
    _str_to_expr,
)


class TestCstUtils(unittest.TestCase):
    # Test CST helpers
    def test_attr_to_dotted_name(self):
        node = cst.Name("foo")
        self.assertEqual(_attr_to_dotted(node), "foo")

    def test_attr_to_dotted_attribute(self):
        node = cst.Attribute(value=cst.Name("mod"), attr=cst.Name("sub"))
        self.assertEqual(_attr_to_dotted(node), "mod.sub")

    def test_attr_to_dotted_complex(self):
        node = cst.Attribute(
            value=cst.Attribute(value=cst.Name("a"), attr=cst.Name("b")),
            attr=cst.Name("c"),
        )
        self.assertEqual(_attr_to_dotted(node), "a.b.c")

    def test_attr_to_dotted_none(self):
        node = cst.SimpleString('"foo"')
        self.assertIsNone(_attr_to_dotted(node))

    def test_module_to_str(self):
        node = cst.Name("mod")
        self.assertEqual(_module_to_str(node), "mod")

    def test_module_to_str_relative(self):
        self.assertEqual(_module_to_str(None, 2), "..")

    def test_module_to_str_attribute(self):
        node = cst.Attribute(value=cst.Name("pkg"), attr=cst.Name("mod"))
        self.assertEqual(_module_to_str(node), "pkg.mod")

    def test_import_alias_name(self):
        alias = cst.ImportAlias(name=cst.Name("Symbol"))
        self.assertEqual(_import_alias_name(alias), "Symbol")

    def test_import_alias_name_dotted(self):
        alias = cst.ImportAlias(
            name=cst.Attribute(value=cst.Name("mod"), attr=cst.Name("Symbol"))
        )
        self.assertEqual(_import_alias_name(alias), "mod.Symbol")

    def test_str_to_expr(self):
        expr = _str_to_expr("pkg.mod")
        self.assertEqual(_attr_to_dotted(expr), "pkg.mod")

    # Test ImportReplacer
    def test_import_replacer_simple(self):
        code = "from old.mod import Symbol"
        wrapper = md.MetadataWrapper(cst.parse_module(code))
        replacer = ImportReplacer("old.mod", "new.mod", ["Symbol"])
        new_code = wrapper.visit(replacer).code
        self.assertEqual(new_code.strip(), "from new.mod import Symbol")

    def test_import_replacer_alias(self):
        code = "from old.mod import Symbol as Alias"
        wrapper = md.MetadataWrapper(cst.parse_module(code))
        replacer = ImportReplacer("old.mod", "new.mod", ["Symbol"])
        new_code = wrapper.visit(replacer).code
        self.assertEqual(new_code.strip(), "from new.mod import Symbol as Alias")

    def test_import_replacer_star(self):
        code = "from old.mod import *"
        wrapper = md.MetadataWrapper(cst.parse_module(code))
        replacer = ImportReplacer("old.mod", "new.mod", ["Symbol"])
        new_code = wrapper.visit(replacer).code
        self.assertIn("from new.mod import Symbol", new_code)
        self.assertIn("from old.mod import *", new_code)

    def test_import_replacer_multi(self):
        code = "from old.mod import A, Symbol, B"
        wrapper = md.MetadataWrapper(cst.parse_module(code))
        replacer = ImportReplacer("old.mod", "new.mod", ["Symbol"])
        new_code = wrapper.visit(replacer).code
        self.assertIn("from old.mod import A, B", new_code)
        self.assertIn("from new.mod import Symbol", new_code)

    def test_import_replacer_no_change(self):
        code = "from new.mod import Symbol"
        wrapper = md.MetadataWrapper(cst.parse_module(code))
        replacer = ImportReplacer("old.mod", "new.mod", ["Symbol"])
        new_code = wrapper.visit(replacer).code
        self.assertEqual(new_code.strip(), code)

    def test_import_replacer_relative_skip(self):
        code = "from .old_sub import Symbol"
        wrapper = md.MetadataWrapper(cst.parse_module(code))
        replacer = ImportReplacer("old_sub", "new_sub", ["Symbol"])
        new_code = wrapper.visit(replacer).code
        self.assertEqual(new_code.strip(), code)

    def test_import_replacer_relative_force(self):
        code = "from .old.mod import Symbol"
        wrapper = md.MetadataWrapper(cst.parse_module(code))
        replacer = ImportReplacer("old.mod", "new.mod", ["Symbol"], force_relative=True)
        new_code = wrapper.visit(replacer).code
        self.assertEqual(new_code.strip(), "from new.mod import Symbol")

    def test_import_replacer_resolve_relative(self):
        code = "from ..old.mod import Symbol"
        file_path = Path("/fake/pkg/sub/file.py")
        replacer = ImportReplacer(
            "pkg.old.mod",
            "pkg.new.mod",
            ["Symbol"],
            force_relative=True,
            base_package="pkg",
            file_path=file_path,
        )
        wrapper = md.MetadataWrapper(cst.parse_module(code))
        new_code = wrapper.visit(replacer).code
        self.assertEqual(new_code.strip(), "from pkg.new.mod import Symbol")

    def test_import_replacer_duplicate_avoid(self):
        code = "from new.mod import Symbol\nfrom old.mod import Symbol"
        wrapper = md.MetadataWrapper(cst.parse_module(code))
        replacer = ImportReplacer("old.mod", "new.mod", ["Symbol"])
        new_code = wrapper.visit(replacer).code
        self.assertEqual(new_code.strip(), "from new.mod import Symbol")

    def test_import_replacer_empty_removal(self):
        code = "from old.mod import Symbol"
        wrapper = md.MetadataWrapper(cst.parse_module(code))
        replacer = ImportReplacer("old.mod", "new.mod", ["Symbol"])
        new_code = wrapper.visit(replacer).code
        self.assertEqual(new_code.strip(), "from new.mod import Symbol")

    def test_import_replacer_no_change_dotted(self):
        code = "import old.mod\nold.mod.Symbol"
        wrapper = md.MetadataWrapper(cst.parse_module(code))
        replacer = ImportReplacer("old.mod", "new.mod", ["Symbol"])
        new_code = wrapper.visit(replacer).code
        self.assertEqual(new_code.strip(), code)

    def test_import_replacer_insert_position(self):
        code = '''"""Docstring"""
from __future__ import annotations
import os
from old.mod import Symbol'''
        wrapper = md.MetadataWrapper(cst.parse_module(code))
        replacer = ImportReplacer("old.mod", "new.mod", ["Symbol"])
        new_code = wrapper.visit(replacer).code
        lines = new_code.splitlines()
        self.assertIn("from new.mod import Symbol", lines)
        self.assertEqual(
            lines.index("from new.mod import Symbol"), 3
        )  # After future and before os

    def test_import_replacer_multi_level_relative(self):
        code = "from ...old.mod import Symbol"
        file_path = Path("/fake/pkg/sub/dir/file.py")
        replacer = ImportReplacer(
            "pkg.old.mod",
            "pkg.new.mod",
            ["Symbol"],
            force_relative=True,
            base_package="pkg",
            file_path=file_path,
        )
        wrapper = md.MetadataWrapper(cst.parse_module(code))
        new_code = wrapper.visit(replacer).code
        self.assertEqual(new_code.strip(), "from pkg.new.mod import Symbol")

    def test_import_replacer_with_comments(self):
        code = "# Comment above\nfrom old.mod import Symbol  # inline comment"
        wrapper = md.MetadataWrapper(cst.parse_module(code))
        replacer = ImportReplacer("old.mod", "new.mod", ["Symbol"])
        new_code = wrapper.visit(replacer).code
        self.assertIn("from new.mod import Symbol", new_code)
        self.assertIn("# Comment above", new_code)

    def test_import_replacer_multi_line(self):
        code = "from old.mod import (\n    A,\n    Symbol,\n    B,\n)"
        wrapper = md.MetadataWrapper(cst.parse_module(code))
        replacer = ImportReplacer("old.mod", "new.mod", ["Symbol"])
        new_code = wrapper.visit(replacer).code
        self.assertIn("from old.mod import (\n    A, B)", new_code)
        self.assertIn("from new.mod import Symbol", new_code)

    def test_import_replacer_no_body(self):
        code = ""
        wrapper = md.MetadataWrapper(cst.parse_module(code))
        replacer = ImportReplacer("old.mod", "new.mod", ["Symbol"])
        new_code = wrapper.visit(replacer).code
        self.assertEqual(new_code, "")

    def test_import_replacer_star_new_with_alias_old(self):
        code = """from new.mod import *
from old.mod import Symbol as Alias"""
        expected = """from new.mod import *
from new.mod import Symbol as Alias"""
        wrapper = md.MetadataWrapper(cst.parse_module(code))
        replacer = ImportReplacer("old.mod", "new.mod", ["Symbol"])
        new_code = wrapper.visit(replacer).code
        self.assertEqual(new_code.strip(), expected.strip())

    def test_import_replacer_existing_alias_in_new(self):
        code = """from new.mod import Symbol as Alias
from old.mod import Symbol as Alias"""
        expected = """from new.mod import Symbol as Alias"""
        wrapper = md.MetadataWrapper(cst.parse_module(code))
        replacer = ImportReplacer("old.mod", "new.mod", ["Symbol"])
        new_code = wrapper.visit(replacer).code
        self.assertEqual(new_code.strip(), expected.strip())

    def test_import_replacer_relative_too_deep(self):
        code = "from ....old.mod import Symbol"
        file_path = Path("/fake/pkg/sub/file.py")
        replacer = ImportReplacer(
            "pkg.old.mod",
            "pkg.new.mod",
            ["Symbol"],
            force_relative=True,
            base_package="pkg",
            file_path=file_path,
        )
        wrapper = md.MetadataWrapper(cst.parse_module(code))
        new_code = wrapper.visit(replacer).code
        self.assertEqual(new_code.strip(), code)

    def test_import_replacer_nested_in_function(self):
        code = """def f():
    from old.mod import Symbol"""
        expected = """from new.mod import Symbol
def f():
    pass"""
        wrapper = md.MetadataWrapper(cst.parse_module(code))
        replacer = ImportReplacer("old.mod", "new.mod", ["Symbol"])
        new_code = wrapper.visit(replacer).code
        self.assertEqual(new_code.strip(), expected.strip())

    def test_import_replacer_conditional_import(self):
        code = """if cond:
    from old.mod import Symbol"""
        expected = """from new.mod import Symbol
if cond:
    pass"""
        wrapper = md.MetadataWrapper(cst.parse_module(code))
        replacer = ImportReplacer("old.mod", "new.mod", ["Symbol"])
        new_code = wrapper.visit(replacer).code
        self.assertEqual(new_code.strip(), expected.strip())

    def test_import_replacer_in_try_except(self):
        code = """try:
    from old.mod import Symbol
except ImportError:
    pass"""
        expected = """from new.mod import Symbol
try:
    pass
except ImportError:
    pass"""
        wrapper = md.MetadataWrapper(cst.parse_module(code))
        replacer = ImportReplacer("old.mod", "new.mod", ["Symbol"])
        new_code = wrapper.visit(replacer).code
        self.assertEqual(new_code.strip(), expected.strip())

    def test_import_replacer_relative_force_no_base_no_match(self):
        code = "from ..old.mod import Symbol"
        expected = code
        file_path = Path("/fake/pkg/sub/file.py")
        replacer = ImportReplacer(
            "pkg.old.mod",
            "pkg.new.mod",
            ["Symbol"],
            force_relative=True,
            base_package=None,
            file_path=file_path,
        )
        wrapper = md.MetadataWrapper(cst.parse_module(code))
        new_code = wrapper.visit(replacer).code
        self.assertEqual(new_code.strip(), expected)

    def test_import_replacer_multiple_symbols(self):
        code = "from old.mod import Sym1, Sym2"
        wrapper = md.MetadataWrapper(cst.parse_module(code))
        replacer = ImportReplacer("old.mod", "new.mod", ["Sym1", "Sym2"])
        new_code = wrapper.visit(replacer).code
        self.assertEqual(new_code.strip(), "from new.mod import Sym1, Sym2")

    def test_import_replacer_multiple_symbols_mixed(self):
        code = "from old.mod import Sym1, Other, Sym2"
        wrapper = md.MetadataWrapper(cst.parse_module(code))
        replacer = ImportReplacer("old.mod", "new.mod", ["Sym1", "Sym2"])
        new_code = wrapper.visit(replacer).code
        self.assertIn("from old.mod import Other", new_code)
        self.assertIn("from new.mod import Sym1, Sym2", new_code)

    def test_import_replacer_multiple_symbols_aliases(self):
        code = "from old.mod import Sym1 as A, Sym2 as B"
        wrapper = md.MetadataWrapper(cst.parse_module(code))
        replacer = ImportReplacer("old.mod", "new.mod", ["Sym1", "Sym2"])
        new_code = wrapper.visit(replacer).code
        self.assertIn("from new.mod import Sym1 as A, Sym2 as B", new_code)

    def test_import_replacer_star_multiple_symbols(self):
        code = "from old.mod import *"
        wrapper = md.MetadataWrapper(cst.parse_module(code))
        replacer = ImportReplacer("old.mod", "new.mod", ["Sym1", "Sym2"])
        new_code = wrapper.visit(replacer).code
        self.assertIn("from old.mod import *", new_code)
        self.assertIn("from new.mod import Sym1, Sym2", new_code)

    # Test DottedReplacer
    def test_dotted_replacer_simple(self):
        code = "a = old.mod.Symbol"
        wrapper = md.MetadataWrapper(cst.parse_module(code))
        replacer = DottedReplacer("old.mod", "new.mod", ["Symbol"])
        new_code = wrapper.visit(replacer).code
        self.assertEqual(new_code.strip(), "a = new.mod.Symbol")

    def test_dotted_replacer_multiple(self):
        code = "a = old.mod.Sym1\nb = old.mod.Sym2"
        wrapper = md.MetadataWrapper(cst.parse_module(code))
        replacer = DottedReplacer("old.mod", "new.mod", ["Sym1", "Sym2"])
        new_code = wrapper.visit(replacer).code
        self.assertEqual(new_code.strip(), "a = new.mod.Sym1\nb = new.mod.Sym2")

    def test_dotted_replacer_no_match(self):
        code = "a = other.mod.Symbol"
        wrapper = md.MetadataWrapper(cst.parse_module(code))
        replacer = DottedReplacer("old.mod", "new.mod", ["Symbol"])
        new_code = wrapper.visit(replacer).code
        self.assertEqual(new_code.strip(), code)

    def test_dotted_replacer_relative(self):
        code = "a = old.mod.Symbol"
        file_path = Path("/fake/pkg/sub/file.py")
        replacer = DottedReplacer(
            "pkg.old.mod",
            "pkg.new.mod",
            ["Symbol"],
            force_relative=True,
            base_package="pkg",
            file_path=file_path,
        )
        wrapper = md.MetadataWrapper(cst.parse_module(code))
        new_code = wrapper.visit(replacer).code
        self.assertEqual(new_code.strip(), "a = pkg.new.mod.Symbol")


if __name__ == "__main__":
    unittest.main()
