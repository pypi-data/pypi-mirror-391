"""
Tests for pattern detection in decompilation.
"""

from pollywog.patterns import (
    PATTERNS,
    AveragePattern,
    ProductPattern,
    SumPattern,
    WeightedAveragePattern,
    detect_pattern,
)


class TestWeightedAveragePattern:
    def test_simple_weighted_average(self):
        """Test detection of simple weighted average."""
        pattern = WeightedAveragePattern()
        expr = "([Au_oxide] * [prop_oxide] + [Au_sulfide] * [prop_sulfide]) / ([prop_oxide] + [prop_sulfide])"

        match = pattern.match(expr)

        assert match is not None
        assert match.pattern_name == "WeightedAverage"
        assert match.confidence >= 0.9
        assert set(match.variables) == {"Au_oxide", "Au_sulfide"}
        assert set(match.parameters["weights"]) == {"prop_oxide", "prop_sulfide"}
        assert "WeightedAverage" in match.helper_code
        assert "variables=" in match.helper_code
        assert "weights=" in match.helper_code

    def test_three_term_weighted_average(self):
        """Test weighted average with three terms."""
        pattern = WeightedAveragePattern()
        expr = "([a] * [w1] + [b] * [w2] + [c] * [w3]) / ([w1] + [w2] + [w3])"

        match = pattern.match(expr)

        assert match is not None
        assert len(match.variables) == 3
        assert len(match.parameters["weights"]) == 3

    def test_not_weighted_average_simple_division(self):
        """Test that simple division is not detected as weighted average."""
        pattern = WeightedAveragePattern()
        expr = "[Au] / [tonnage]"

        match = pattern.match(expr)

        assert match is None

    def test_not_weighted_average_missing_weights(self):
        """Test that expression missing weights in denominator is not matched."""
        pattern = WeightedAveragePattern()
        expr = "([Au_oxide] * [prop_oxide] + [Au_sulfide] * [prop_sulfide]) / 2"

        match = pattern.match(expr)

        assert match is None


class TestSumPattern:
    def test_simple_sum(self):
        """Test detection of simple sum."""
        pattern = SumPattern()
        expr = "[Au] + [Ag] + [Cu]"

        match = pattern.match(expr)

        assert match is not None
        assert match.pattern_name == "Sum"
        assert match.confidence >= 0.9
        assert set(match.variables) == {"Au", "Ag", "Cu"}
        assert "Sum" in match.helper_code

    def test_two_term_sum(self):
        """Test sum with two terms."""
        pattern = SumPattern()
        expr = "[a] + [b]"

        match = pattern.match(expr)

        assert match is not None
        assert len(match.variables) == 2

    def test_not_sum_with_multiplication(self):
        """Test that expression with multiplication is not matched as sum."""
        pattern = SumPattern()
        expr = "[Au] * [Ag] + [Cu]"

        match = pattern.match(expr)

        assert match is None

    def test_not_sum_single_variable(self):
        """Test that single variable is not matched as sum."""
        pattern = SumPattern()
        expr = "[Au]"

        match = pattern.match(expr)

        assert match is None


class TestProductPattern:
    def test_simple_product(self):
        """Test detection of simple product."""
        pattern = ProductPattern()
        expr = "[length] * [width] * [height]"

        match = pattern.match(expr)

        assert match is not None
        assert match.pattern_name == "Product"
        assert match.confidence >= 0.9
        assert set(match.variables) == {"length", "width", "height"}
        assert "Product" in match.helper_code

    def test_two_term_product(self):
        """Test product with two terms."""
        pattern = ProductPattern()
        expr = "[a] * [b]"

        match = pattern.match(expr)

        assert match is not None
        assert len(match.variables) == 2

    def test_not_product_with_addition(self):
        """Test that expression with addition is not matched as product."""
        pattern = ProductPattern()
        expr = "[Au] * [Ag] + [Cu]"

        match = pattern.match(expr)

        assert match is None


class TestAveragePattern:
    def test_simple_average(self):
        """Test detection of simple average."""
        pattern = AveragePattern()
        expr = "([Au1] + [Au2] + [Au3]) / 3"

        match = pattern.match(expr)

        assert match is not None
        assert match.pattern_name == "Average"
        assert match.confidence >= 0.9
        assert set(match.variables) == {"Au1", "Au2", "Au3"}
        assert match.parameters["count"] == 3
        assert "Average" in match.helper_code

    def test_average_count_mismatch(self):
        """Test average with count not matching variable count (lower confidence)."""
        pattern = AveragePattern()
        expr = "([Au1] + [Au2]) / 3"

        match = pattern.match(expr)

        assert match is not None
        assert match.confidence < 0.9  # Lower confidence due to mismatch

    def test_not_average_division_by_variable(self):
        """Test that division by variable is not matched as average."""
        pattern = AveragePattern()
        expr = "([Au1] + [Au2]) / [count]"

        match = pattern.match(expr)

        assert match is None


class TestPatternDetection:
    def test_detect_weighted_average(self):
        """Test detect_pattern function with weighted average."""
        expr = "([Au_oxide] * [prop_oxide] + [Au_sulfide] * [prop_sulfide]) / ([prop_oxide] + [prop_sulfide])"

        match = detect_pattern(expr)

        assert match is not None
        assert match.pattern_name == "WeightedAverage"

    def test_detect_sum(self):
        """Test detect_pattern function with sum."""
        expr = "[Au] + [Ag] + [Cu]"

        match = detect_pattern(expr)

        assert match is not None
        assert match.pattern_name == "Sum"

    def test_detect_product(self):
        """Test detect_pattern function with product."""
        expr = "[length] * [width] * [height]"

        match = detect_pattern(expr)

        assert match is not None
        assert match.pattern_name == "Product"

    def test_detect_average(self):
        """Test detect_pattern function with average."""
        expr = "([Au1] + [Au2] + [Au3]) / 3"

        match = detect_pattern(expr)

        assert match is not None
        assert match.pattern_name == "Average"

    def test_detect_no_pattern(self):
        """Test detect_pattern with expression that doesn't match any pattern."""
        expr = "[Au] * 0.95 + [Ag] * 0.85"

        match = detect_pattern(expr)

        assert match is None

    def test_detect_min_confidence(self):
        """Test detect_pattern respects minimum confidence threshold."""
        expr = "([Au1] + [Au2]) / 3"  # Count mismatch -> lower confidence

        # With default min_confidence (0.9)
        match = detect_pattern(expr)
        assert match is None

        # With lower threshold
        match = detect_pattern(expr, min_confidence=0.5)
        assert match is not None
        assert match.pattern_name == "Average"

    def test_patterns_registry(self):
        """Test that all patterns are registered."""
        pattern_names = {p.name for p in PATTERNS}

        assert "WeightedAverage" in pattern_names
        assert "Sum" in pattern_names
        assert "Product" in pattern_names
        assert "Average" in pattern_names
