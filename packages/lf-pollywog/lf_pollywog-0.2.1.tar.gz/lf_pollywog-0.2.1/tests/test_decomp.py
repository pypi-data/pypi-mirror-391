"""
Tests for the decomp module (decompilation of .lfcalc to Python code).
"""

import tempfile
from pathlib import Path

from pollywog.core import CalcSet, Category, Filter, If, Number, Variable
from pollywog.decomp import decompile, decompile_to_string


def test_decompile_simple_number():
    """Test decompiling a simple Number calculation."""
    calcset = CalcSet(
        [
            Number(
                "Au_clean", "clamp([Au], 0)", comment_equation="Remove negative values"
            ),
        ]
    )

    code = decompile_to_string(calcset)

    # Check that code contains expected elements
    assert "from pollywog.core import" in code
    assert "CalcSet" in code
    assert "Number" in code
    assert '"Au_clean"' in code
    assert '"clamp([Au], 0)"' in code
    assert "Remove negative values" in code


def test_decompile_multiple_items():
    """Test decompiling multiple items of different types."""
    calcset = CalcSet(
        [
            Variable("Au", comment_item="Gold grade from database"),
            Number("Au_clean", "clamp([Au], 0)"),
            Number("Au_log", "log([Au_clean] + 1e-6)"),
            Category("ore_class", "'low_grade'"),
            Filter("is_ore", "[Au_clean] > 0.5"),
        ]
    )

    code = decompile_to_string(calcset)

    # Check all item types are imported
    assert "Variable" in code
    assert "Number" in code
    assert "Category" in code
    assert "Filter" in code

    # Check all items are created
    assert '"Au"' in code
    assert '"Au_clean"' in code
    assert '"Au_log"' in code
    assert '"ore_class"' in code
    assert '"is_ore"' in code


def test_decompile_with_if_statement():
    """Test decompiling calculations with If statements."""
    calcset = CalcSet(
        [
            Number(
                "grade_adjusted",
                [
                    If(
                        [
                            ("[Au] > 2.0", "[Au] * 0.95"),
                            ("[Au] > 1.0", "[Au] * 0.98"),
                        ],
                        otherwise=["[Au]"],
                    )
                ],
            ),
        ]
    )

    code = decompile_to_string(calcset)

    # Check If structure is present
    assert "If([" in code
    assert "[Au] > 2.0" in code
    assert "[Au] * 0.95" in code
    assert "otherwise=" in code


def test_decompile_roundtrip():
    """Test that decompiled code can be executed to recreate the same calcset."""
    original = CalcSet(
        [
            Number("Au_clean", "clamp([Au], 0)", comment_equation="Remove negatives"),
            Number("Au_log", "log([Au_clean] + 1e-6)"),
            Category("ore_type", "'oxide'"),
        ]
    )

    # Generate code
    code = decompile_to_string(original)

    # Execute the generated code to create a new calcset
    namespace = {}
    exec(code, namespace)
    recreated = namespace["calcset"]

    # Verify the recreated calcset matches the original
    assert len(recreated.items) == len(original.items)

    for orig_item, rec_item in zip(original.items, recreated.items):
        assert type(orig_item) == type(rec_item)
        assert orig_item.name == rec_item.name
        assert orig_item.expression == rec_item.expression
        assert orig_item.comment_item == rec_item.comment_item
        assert orig_item.comment_equation == rec_item.comment_equation


def test_decompile_file_io():
    """Test decompiling to/from files."""
    calcset = CalcSet(
        [
            Number("Au_clean", "clamp([Au], 0)"),
            Number("Au_log", "log([Au_clean] + 1e-6)"),
        ]
    )

    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)

        # Save as .lfcalc
        lfcalc_path = tmpdir / "test.lfcalc"
        calcset.to_lfcalc(lfcalc_path)

        # Decompile to Python
        py_path = tmpdir / "test_decompiled.py"
        code = decompile(lfcalc_path, py_path)

        # Verify file was created
        assert py_path.exists()
        assert py_path.read_text() == code

        # Verify the code is valid Python
        namespace = {}
        exec(code, namespace)
        assert "calcset" in namespace


def test_decompile_escaping():
    """Test that special characters in strings are properly escaped."""
    calcset = CalcSet(
        [
            Number(
                "test", 'some"quoted"text', comment_equation='Comment with "quotes"'
            ),
        ]
    )

    code = decompile_to_string(calcset)

    # The generated code should be valid Python
    namespace = {}
    exec(code, namespace)
    recreated = namespace["calcset"]

    assert recreated.items[0].expression[0] == 'some"quoted"text'
    assert recreated.items[0].comment_equation == 'Comment with "quotes"'


def test_decompile_complex_if():
    """Test decompiling complex If structures with multiple conditions."""
    calcset = CalcSet(
        [
            Category(
                "domain",
                [
                    If(
                        [
                            ("[depth] < 100", "'oxide'"),
                            ("[depth] < 200", "'transition'"),
                            ("[depth] < 500", "'sulfide'"),
                        ],
                        otherwise=["'deep_sulfide'"],
                    )
                ],
            ),
        ]
    )

    code = decompile_to_string(calcset)

    # Execute and verify
    namespace = {}
    exec(code, namespace)
    recreated = namespace["calcset"]

    # Verify If structure is preserved
    assert len(recreated.items) == 1
    assert isinstance(recreated.items[0].expression[0], If)
    assert len(recreated.items[0].expression[0].rows) == 3
    assert recreated.items[0].expression[0].otherwise == ["'deep_sulfide'"]


def test_decompile_with_weighted_average_pattern():
    """Test that weighted average pattern is detected and converted to helper."""
    from pollywog.helpers import WeightedAverage

    calcset = CalcSet(
        [
            # Create using helper
            WeightedAverage(
                variables=["Au_oxide", "Au_sulfide"],
                weights=["prop_oxide", "prop_sulfide"],
                name="Au_composite",
                comment="Domain-weighted gold grade",
            ),
        ]
    )

    code = decompile_to_string(calcset)

    # Should detect pattern and use WeightedAverage helper
    assert "WeightedAverage" in code
    assert 'variables=["Au_oxide", "Au_sulfide"]' in code
    assert 'weights=["prop_oxide", "prop_sulfide"]' in code
    assert "Domain-weighted gold grade" in code

    # Should not have manual formula
    assert "([Au_oxide] * [prop_oxide]" not in code


def test_decompile_with_sum_pattern():
    """Test that sum pattern is detected and converted to helper."""
    calcset = CalcSet(
        [
            Number("total_grade", "[Au] + [Ag] + [Cu]"),
        ]
    )

    code = decompile_to_string(calcset)

    # Should detect pattern and use Sum helper
    assert "Sum" in code
    assert '["Au", "Ag", "Cu"]' in code

    # Should not have manual formula
    assert "[Au] + [Ag] + [Cu]" not in code


def test_decompile_with_product_pattern():
    """Test that product pattern is detected and converted to helper."""
    calcset = CalcSet(
        [
            Number("volume", "[length] * [width] * [height]"),
        ]
    )

    code = decompile_to_string(calcset)

    # Should detect pattern and use Product helper
    assert "Product" in code
    assert '["length", "width", "height"]' in code


def test_decompile_with_average_pattern():
    """Test that average pattern is detected and converted to helper."""
    calcset = CalcSet(
        [
            Number("avg_grade", "([Au1] + [Au2] + [Au3]) / 3"),
        ]
    )

    code = decompile_to_string(calcset)

    # Should detect pattern and use Average helper
    assert "Average" in code
    assert '["Au1", "Au2", "Au3"]' in code


def test_decompile_no_pattern_fallback():
    """Test that expressions without patterns fall back to direct code."""
    calcset = CalcSet(
        [
            Number(
                "custom", "[Au] * 0.95 + [Ag] * 0.85", comment_equation="Custom formula"
            ),
        ]
    )

    code = decompile_to_string(calcset)

    # Should NOT use any helper in the item definition (helpers are in imports, that's OK)
    # Check that the item is created with Number(), not a helper
    assert 'Number("custom"' in code

    # Should have direct formula
    assert "[Au] * 0.95 + [Ag] * 0.85" in code
    assert "Custom formula" in code


def test_decompile_pattern_roundtrip():
    """Test that decompiled code with patterns can recreate the same calcset."""
    from pollywog.helpers import WeightedAverage

    original = CalcSet(
        [
            WeightedAverage(
                variables=["Au_oxide", "Au_sulfide"],
                weights=["prop_oxide", "prop_sulfide"],
                name="Au_composite",
                comment="Domain-weighted gold",
            ),
            Number("total", "[Au] + [Ag] + [Cu]"),
        ]
    )

    # Decompile
    code = decompile_to_string(original)

    # Execute to recreate
    namespace = {}
    exec(code, namespace)
    recreated = namespace["calcset"]

    # Verify items match
    assert len(recreated.items) == len(original.items)

    for orig_item, rec_item in zip(original.items, recreated.items):
        assert orig_item.name == rec_item.name
        # Expressions should be semantically equivalent
        # (Helpers may add parentheses, so normalize by removing them)
        orig_expr = str(orig_item.expression).replace("(", "").replace(")", "")
        rec_expr = str(rec_item.expression).replace("(", "").replace(")", "")
        assert orig_expr == rec_expr


def test_decompile_imports_helpers():
    """Test that decompiled code imports helper functions."""
    calcset = CalcSet(
        [
            Number("test", "[a] + [b]"),
        ]
    )

    code = decompile_to_string(calcset)

    # Should import helpers
    assert "from pollywog.helpers import" in code
    assert "Average" in code
    assert "Product" in code
    assert "Sum" in code
    assert "WeightedAverage" in code
