"""
Example: Decompiling .lfcalc files to Python code

This example demonstrates how to use pollywog's decompilation feature to convert
existing .lfcalc files into version-controlled Python code.

Use cases:
- Migrate legacy calculations to git-based workflows
- Learn how to write complex calculations in pollywog
- Get a starting point for refactoring manual calculations
"""

from pollywog.core import CalcSet, Category, If, Number
from pollywog.decomp import decompile, decompile_to_string
from pollywog.helpers import WeightedAverage

# ============================================================================
# Example 1: Decompile an existing .lfcalc file
# ============================================================================

print("=" * 70)
print("Example 1: Decompiling an existing .lfcalc file")
print("=" * 70)

# Pick one of the example .lfcalc files
input_file = "complete_workflow.lfcalc"

# Decompile to Python code
print(f"\nDecompiling {input_file}...\n")
code = decompile(input_file)

print("Generated Python code:")
print("-" * 70)
print(code)
print("-" * 70)

# You can also save to a file
# decompile(input_file, "complete_workflow_decompiled.py")

# ============================================================================
# Example 2: Decompile a CalcSet directly (without file I/O)
# ============================================================================

print("\n" + "=" * 70)
print("Example 2: Decompiling a CalcSet directly")
print("=" * 70)

# Create a sample calcset
calcset = CalcSet(
    [
        Number("Au_clean", "clamp([Au], 0)", comment_equation="Remove negative values"),
        Number("Au_capped", "min([Au_clean], 10)", comment_equation="Cap at 10 g/t"),
        # Using helper
        WeightedAverage(
            variables=["Au_oxide", "Au_sulfide"],
            weights=["prop_oxide", "prop_sulfide"],
            name="Au_composite",
            comment="Domain-weighted gold grade",
        ),
        # Conditional logic
        Category(
            "ore_class",
            [
                If(
                    [
                        ("[Au_composite] > 2.0", "'high_grade'"),
                        ("[Au_composite] > 0.5", "'low_grade'"),
                    ],
                    otherwise=["'waste'"],
                )
            ],
        ),
    ]
)

# Decompile to string
code = decompile_to_string(calcset)

print("\nGenerated Python code:")
print("-" * 70)
print(code)
print("-" * 70)

# ============================================================================
# Example 3: Roundtrip verification
# ============================================================================

print("\n" + "=" * 70)
print("Example 3: Roundtrip verification (CalcSet -> Code -> CalcSet)")
print("=" * 70)

# Generate Python code
code = decompile_to_string(calcset)

# Execute the generated code to recreate the calcset
namespace = {}
exec(code, namespace)
recreated = namespace["calcset"]

# Verify it matches
print(f"\nOriginal items: {len(calcset.items)}")
print(f"Recreated items: {len(recreated.items)}")
print(
    f"Names match: {all(o.name == r.name for o, r in zip(calcset.items, recreated.items))}"
)
print(
    f"Expressions match: {all(o.expression == r.expression for o, r in zip(calcset.items, recreated.items))}"
)

print("\nSuccess! The decompiled code recreates the exact same CalcSet.")

# ============================================================================
# Tips for using decompilation
# ============================================================================

print("\n" + "=" * 70)
print("Tips for using decompilation:")
print("=" * 70)
print(
    """
1. **Migration workflow**:
   - Decompile your .lfcalc files to Python
   - Commit the Python code to git
   - Future changes are version-controlled and reviewable

2. **Learning tool**:
   - Not sure how to write a complex If statement?
   - Build it manually in Leapfrog, export to .lfcalc
   - Decompile to see the pollywog syntax

3. **Refactoring**:
   - Decompile gives you valid Python code
   - Look for patterns (repeated structures)
   - Manually refactor using helpers or loops
   - Commit the improved version

4. **Phase 1 limitations**:
   - No automatic pattern detection (yet!)
   - WeightedAverage becomes manual formula
   - Loops are unrolled into individual items
   - You'll need to manually identify optimization opportunities

5. **Future phases**:
   - Phase 2: Auto-detect WeightedAverage, Sum, etc.
   - Phase 3: Detect variable families and generate loops
   - Phase 4: Suggest refactoring opportunities
"""
)
