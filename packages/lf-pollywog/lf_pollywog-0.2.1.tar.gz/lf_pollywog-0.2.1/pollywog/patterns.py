"""
Pattern detection for decompilation.

This module provides pattern matching capabilities to detect common calculation
patterns in expressions and convert them to helper function calls.

Phase 2: String-based pattern matching for common cases.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Optional


@dataclass
class PatternMatch:
    """
    Result of attempting to match a pattern in an expression.

    Attributes:
        pattern_name: Name of the matched pattern (e.g., "WeightedAverage")
        confidence: Confidence score (0.0 to 1.0)
        helper_code: Generated helper function call (if matched)
        variables: List of variable names extracted
        parameters: Dict of additional parameters (weights, thresholds, etc.)
    """

    pattern_name: str
    confidence: float
    helper_code: str
    variables: list[str]
    parameters: dict


class Pattern:
    """Base class for pattern matchers."""

    name: str = "Pattern"

    def match(self, expression: str) -> Optional[PatternMatch]:
        """
        Attempt to match this pattern against an expression.

        Args:
            expression: Expression string to match against

        Returns:
            PatternMatch if matched with confidence > 0, None otherwise
        """
        raise NotImplementedError


class WeightedAveragePattern(Pattern):
    """
    Detects weighted average pattern: (a*w1 + b*w2 + ...) / (w1 + w2 + ...)

    Examples:
        ([Au_oxide] * [prop_oxide] + [Au_sulfide] * [prop_sulfide]) / ([prop_oxide] + [prop_sulfide])
    """

    name = "WeightedAverage"

    def match(self, expression: str) -> Optional[PatternMatch]:
        # Normalize whitespace
        expr = expression.replace(" ", "")

        # Pattern: (term1 + term2 + ...) / (weight1 + weight2 + ...)
        # where each term is: [var] * [weight]
        division_pattern = r"^\(([^)]+)\)/\(([^)]+)\)$"
        match = re.match(division_pattern, expr)

        if not match:
            return None

        numerator = match.group(1)
        denominator = match.group(2)

        # Extract terms from numerator (should be [var]*[weight])
        term_pattern = r"\[([^\]]+)\]\*\[([^\]]+)\]"
        terms = re.findall(term_pattern, numerator)

        if not terms:
            return None

        # Extract weights from denominator
        weight_pattern = r"\[([^\]]+)\]"
        denominator_weights = re.findall(weight_pattern, denominator)

        if not denominator_weights:
            return None

        # Extract variables and weights from terms
        variables = [var for var, weight in terms]
        numerator_weights = [weight for var, weight in terms]

        # Check that all weights match between numerator and denominator
        if set(numerator_weights) != set(denominator_weights):
            return None

        if len(numerator_weights) != len(denominator_weights):
            return None

        # High confidence if:
        # 1. Weights match exactly
        # 2. At least 2 terms
        # 3. All terms follow the pattern
        confidence = 0.95 if len(variables) >= 2 else 0.8

        # Generate helper code
        variables_str = ", ".join(f'"{v}"' for v in variables)
        weights_str = ", ".join(f'"{w}"' for w in numerator_weights)

        helper_code = (
            f"WeightedAverage(variables=[{variables_str}], weights=[{weights_str}])"
        )

        return PatternMatch(
            pattern_name=self.name,
            confidence=confidence,
            helper_code=helper_code,
            variables=variables,
            parameters={"weights": numerator_weights},
        )


class SumPattern(Pattern):
    """
    Detects simple sum pattern: a + b + c + ...

    Examples:
        [Au] + [Ag] + [Cu]
    """

    name = "Sum"

    def match(self, expression: str) -> Optional[PatternMatch]:
        # Normalize whitespace
        expr = expression.replace(" ", "")

        # Pattern: [var1]+[var2]+[var3]+...
        # Must have at least 2 terms
        pattern = r"^\[([^\]]+)\](?:\+\[([^\]]+)\])+$"

        if not re.match(pattern, expr):
            return None

        # Extract all variables
        var_pattern = r"\[([^\]]+)\]"
        variables = re.findall(var_pattern, expr)

        if len(variables) < 2:
            return None

        # Check that there are no other operators (multiplication, division, etc.)
        # Remove all [var] patterns and check what's left
        cleaned = re.sub(r"\[([^\]]+)\]", "", expr)
        if cleaned.replace("+", "") != "":
            return None

        # High confidence for simple addition
        confidence = 0.95

        # Generate helper code
        variables_str = ", ".join(f'"{v}"' for v in variables)
        helper_code = f"Sum([{variables_str}])"

        return PatternMatch(
            pattern_name=self.name,
            confidence=confidence,
            helper_code=helper_code,
            variables=variables,
            parameters={},
        )


class ProductPattern(Pattern):
    """
    Detects simple product pattern: a * b * c * ...

    Examples:
        [length] * [width] * [height]
    """

    name = "Product"

    def match(self, expression: str) -> Optional[PatternMatch]:
        # Normalize whitespace
        expr = expression.replace(" ", "")

        # Pattern: [var1]*[var2]*[var3]*...
        # Must have at least 2 terms
        pattern = r"^\[([^\]]+)\](?:\*\[([^\]]+)\])+$"

        if not re.match(pattern, expr):
            return None

        # Extract all variables
        var_pattern = r"\[([^\]]+)\]"
        variables = re.findall(var_pattern, expr)

        if len(variables) < 2:
            return None

        # Check that there are no other operators
        cleaned = re.sub(r"\[([^\]]+)\]", "", expr)
        if cleaned.replace("*", "") != "":
            return None

        # High confidence for simple multiplication
        confidence = 0.95

        # Generate helper code
        variables_str = ", ".join(f'"{v}"' for v in variables)
        helper_code = f"Product([{variables_str}])"

        return PatternMatch(
            pattern_name=self.name,
            confidence=confidence,
            helper_code=helper_code,
            variables=variables,
            parameters={},
        )


class AveragePattern(Pattern):
    """
    Detects average pattern: (a + b + c + ...) / N

    Examples:
        ([Au1] + [Au2] + [Au3]) / 3
    """

    name = "Average"

    def match(self, expression: str) -> Optional[PatternMatch]:
        # Normalize whitespace
        expr = expression.replace(" ", "")

        # Pattern: ([var1]+[var2]+...)/N
        pattern = r"^\(([^)]+)\)/(\d+)$"
        match = re.match(pattern, expr)

        if not match:
            return None

        numerator = match.group(1)
        denominator = int(match.group(2))

        # Extract variables from numerator
        var_pattern = r"\[([^\]]+)\]"
        variables = re.findall(var_pattern, numerator)

        if not variables:
            return None

        # Check that denominator matches the number of variables
        if len(variables) != denominator:
            # Could still be average, just with lower confidence
            confidence = 0.7
        else:
            confidence = 0.95

        # Check that numerator is simple addition
        cleaned = re.sub(r"\[([^\]]+)\]", "", numerator)
        if cleaned.replace("+", "") != "":
            return None

        # Generate helper code
        variables_str = ", ".join(f'"{v}"' for v in variables)
        helper_code = f"Average([{variables_str}])"

        return PatternMatch(
            pattern_name=self.name,
            confidence=confidence,
            helper_code=helper_code,
            variables=variables,
            parameters={"count": denominator},
        )


# Registry of all available patterns
PATTERNS = [
    WeightedAveragePattern(),
    SumPattern(),
    ProductPattern(),
    AveragePattern(),
]


def detect_pattern(
    expression: str, min_confidence: float = 0.9
) -> Optional[PatternMatch]:
    """
    Attempt to detect a pattern in the given expression.

    Tries all registered patterns and returns the best match above the
    minimum confidence threshold.

    Args:
        expression: Expression string to analyze
        min_confidence: Minimum confidence threshold (0.0 to 1.0)

    Returns:
        PatternMatch if a pattern is detected with sufficient confidence,
        None otherwise
    """
    best_match = None
    best_confidence = 0.0

    for pattern in PATTERNS:
        match = pattern.match(expression)
        if match and match.confidence > best_confidence:
            best_match = match
            best_confidence = match.confidence

    if best_match and best_confidence >= min_confidence:
        return best_match

    return None
