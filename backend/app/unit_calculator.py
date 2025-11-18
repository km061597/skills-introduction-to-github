"""
Unit Price Extraction and Calculation Module

This module handles:
1. Extracting quantity and unit from product titles
2. Normalizing units to common standards
3. Calculating unit prices ($/oz, $/count, etc.)
4. Comparing bulk sizes
"""
import re
from typing import Optional, Tuple
from decimal import Decimal


class UnitCalculator:
    """
    Handles unit price extraction and calculation
    """

    # Unit conversion factors to ounces
    WEIGHT_CONVERSIONS = {
        'oz': 1.0,
        'ounce': 1.0,
        'ounces': 1.0,
        'lb': 16.0,
        'lbs': 16.0,
        'pound': 16.0,
        'pounds': 16.0,
        'g': 0.0353,
        'gram': 0.0353,
        'grams': 0.0353,
        'kg': 35.274,
        'kilogram': 35.274,
        'kilograms': 35.274,
    }

    # Volume conversion factors to fluid ounces
    VOLUME_CONVERSIONS = {
        'fl oz': 1.0,
        'fl. oz': 1.0,
        'fluid ounce': 1.0,
        'fluid ounces': 1.0,
        'ml': 0.0338,
        'milliliter': 0.0338,
        'milliliters': 0.0338,
        'l': 33.814,
        'liter': 33.814,
        'liters': 33.814,
        'gal': 128.0,
        'gallon': 128.0,
        'gallons': 128.0,
        'qt': 32.0,
        'quart': 32.0,
        'quarts': 32.0,
        'pt': 16.0,
        'pint': 16.0,
        'pints': 16.0,
    }

    # Regex patterns for extracting units from titles
    PATTERNS = [
        # Weight patterns
        r'(\d+(?:\.\d+)?)\s*[-]?\s*(oz|ounce|ounces)\b',
        r'(\d+(?:\.\d+)?)\s*[-]?\s*(lb|lbs|pound|pounds)\b',
        r'(\d+(?:\.\d+)?)\s*[-]?\s*(g|gram|grams)\b',
        r'(\d+(?:\.\d+)?)\s*[-]?\s*(kg|kilogram|kilograms)\b',

        # Volume patterns
        r'(\d+(?:\.\d+)?)\s*[-]?\s*(fl\.?\s*oz|fluid\s+ounce|fluid\s+ounces)\b',
        r'(\d+(?:\.\d+)?)\s*[-]?\s*(ml|milliliter|milliliters)\b',
        r'(\d+(?:\.\d+)?)\s*[-]?\s*(l|liter|liters)\b',
        r'(\d+(?:\.\d+)?)\s*[-]?\s*(gal|gallon|gallons)\b',

        # Count patterns
        r'(\d+(?:\.\d+)?)\s*[-]?\s*pack\b',
        r'(\d+(?:\.\d+)?)\s*[-]?\s*count\b',
        r'(\d+(?:\.\d+)?)\s*[-]?\s*ct\b',
        r'(\d+(?:\.\d+)?)\s*[-]?\s*piece|pieces\b',

        # Combined patterns (e.g., "12 x 16 oz")
        r'(\d+)\s*[x×]\s*(\d+(?:\.\d+)?)\s*(oz|lb|g|ml|fl\.?\s*oz)',
    ]

    @staticmethod
    def extract_unit_from_title(title: str) -> Tuple[Optional[float], Optional[str]]:
        """
        Extract quantity and unit from product title

        Args:
            title: Product title string

        Returns:
            Tuple of (quantity, unit) or (None, None) if not found
        """
        if not title:
            return None, None

        title_lower = title.lower()

        # Try each pattern
        for pattern in UnitCalculator.PATTERNS:
            match = re.search(pattern, title_lower, re.IGNORECASE)
            if match:
                groups = match.groups()

                # Handle combined patterns (e.g., "12 x 16 oz")
                if len(groups) == 3 and groups[0].isdigit():
                    count = float(groups[0])
                    quantity = float(groups[1])
                    unit = groups[2].strip()
                    total_quantity = count * quantity
                    return total_quantity, unit

                # Standard patterns
                elif len(groups) >= 2:
                    quantity = float(groups[0])
                    unit = groups[1].strip()
                    return quantity, unit

        return None, None

    @staticmethod
    def normalize_to_standard_unit(quantity: float, unit: str) -> Tuple[Optional[float], Optional[str]]:
        """
        Normalize quantity to standard unit (oz for weight, fl oz for volume, count for items)

        Args:
            quantity: Original quantity
            unit: Original unit

        Returns:
            Tuple of (normalized_quantity, standard_unit)
        """
        if not quantity or not unit:
            return None, None

        unit_lower = unit.lower().strip()

        # Check weight conversions
        if unit_lower in UnitCalculator.WEIGHT_CONVERSIONS:
            conversion_factor = UnitCalculator.WEIGHT_CONVERSIONS[unit_lower]
            normalized = quantity * conversion_factor
            return normalized, 'oz'

        # Check volume conversions
        if unit_lower in UnitCalculator.VOLUME_CONVERSIONS:
            conversion_factor = UnitCalculator.VOLUME_CONVERSIONS[unit_lower]
            normalized = quantity * conversion_factor
            return normalized, 'fl oz'

        # Count-based (pack, count, ct)
        if unit_lower in ['pack', 'count', 'ct', 'piece', 'pieces']:
            return quantity, 'count'

        return None, None

    @staticmethod
    def calculate_unit_price(price: Decimal, quantity: float, unit: str) -> Optional[Decimal]:
        """
        Calculate unit price ($/oz, $/count, etc.)

        Args:
            price: Product price
            quantity: Quantity from title
            unit: Unit from title

        Returns:
            Unit price as Decimal or None if cannot calculate
        """
        if not price or not quantity or not unit or quantity == 0:
            return None

        try:
            # Normalize to standard unit
            normalized_qty, standard_unit = UnitCalculator.normalize_to_standard_unit(quantity, unit)

            if not normalized_qty or normalized_qty == 0:
                return None

            # Calculate unit price
            unit_price = price / Decimal(str(normalized_qty))
            return round(unit_price, 4)  # Round to 4 decimal places

        except (ValueError, ZeroDivisionError, Exception):
            return None

    @staticmethod
    def get_unit_type(unit: str) -> Optional[str]:
        """
        Get standardized unit type from original unit

        Args:
            unit: Original unit string

        Returns:
            Standardized unit type ('oz', 'fl oz', 'count')
        """
        if not unit:
            return None

        unit_lower = unit.lower().strip()

        if unit_lower in UnitCalculator.WEIGHT_CONVERSIONS:
            return 'oz'
        elif unit_lower in UnitCalculator.VOLUME_CONVERSIONS:
            return 'fl oz'
        elif unit_lower in ['pack', 'count', 'ct', 'piece', 'pieces']:
            return 'count'

        return None

    @staticmethod
    def calculate_bulk_savings(sizes: list) -> list:
        """
        Analyze bulk sizes to find best value

        Args:
            sizes: List of tuples [(size_label, quantity, unit, price), ...]

        Returns:
            List of dicts with analysis
        """
        analysis = []

        for size_label, quantity, unit, price in sizes:
            unit_price = UnitCalculator.calculate_unit_price(
                Decimal(str(price)),
                quantity,
                unit
            )

            if unit_price:
                analysis.append({
                    'size': size_label,
                    'price': price,
                    'quantity': quantity,
                    'unit': unit,
                    'unit_price': float(unit_price)
                })

        # Sort by unit price
        analysis.sort(key=lambda x: x['unit_price'])

        if analysis:
            best_unit_price = analysis[0]['unit_price']

            # Calculate savings vs best
            for item in analysis:
                if best_unit_price > 0:
                    savings_pct = ((item['unit_price'] - best_unit_price) / best_unit_price) * 100
                    item['savings_vs_best'] = round(savings_pct, 2)
                    item['is_best'] = (item['unit_price'] == best_unit_price)

        return analysis

    @staticmethod
    def calculate_subscribe_save_value(
        current_price: Decimal,
        quantity: float,
        unit: str,
        discount_pct: float
    ) -> dict:
        """
        Calculate true value with Subscribe & Save discount

        Args:
            current_price: Current product price
            quantity: Product quantity
            unit: Product unit
            discount_pct: Subscribe & Save discount percentage

        Returns:
            Dict with original and discounted prices
        """
        original_unit_price = UnitCalculator.calculate_unit_price(current_price, quantity, unit)

        if not original_unit_price or not discount_pct:
            return {
                'original_price': float(current_price),
                'original_unit_price': float(original_unit_price) if original_unit_price else None,
                'discounted_price': None,
                'discounted_unit_price': None,
                'savings': None
            }

        discounted_price = current_price * Decimal(1 - discount_pct / 100)
        discounted_unit_price = UnitCalculator.calculate_unit_price(discounted_price, quantity, unit)
        savings = current_price - discounted_price

        return {
            'original_price': float(current_price),
            'original_unit_price': float(original_unit_price),
            'discounted_price': float(discounted_price),
            'discounted_unit_price': float(discounted_unit_price) if discounted_unit_price else None,
            'savings': float(savings),
            'discount_pct': discount_pct
        }


# Helper function for easy import
def extract_and_calculate_unit_price(title: str, price: Decimal) -> Tuple[Optional[Decimal], Optional[str], Optional[float]]:
    """
    Convenience function to extract unit info and calculate unit price in one call

    Args:
        title: Product title
        price: Product price

    Returns:
        Tuple of (unit_price, unit_type, quantity)
    """
    quantity, unit = UnitCalculator.extract_unit_from_title(title)

    if not quantity or not unit:
        return None, None, None

    unit_price = UnitCalculator.calculate_unit_price(price, quantity, unit)
    unit_type = UnitCalculator.get_unit_type(unit)

    return unit_price, unit_type, quantity


# UnitType enum for backward compatibility with tests
from enum import Enum


class UnitType(str, Enum):
    """Unit type enumeration"""
    WEIGHT = "weight"
    VOLUME = "volume"
    COUNT = "count"
    UNKNOWN = "unknown"


# Backward compatibility wrapper
class UnitPriceCalculator(UnitCalculator):
    """Wrapper class for backward compatibility with tests"""

    @staticmethod
    def extract_unit_info(title: str) -> dict:
        """
        Extract unit information from title (compatibility method)

        Args:
            title: Product title

        Returns:
            Dictionary with quantity, unit, and unit_type
        """
        quantity, unit = UnitCalculator.extract_unit_from_title(title)

        # Determine unit type
        unit_type = None
        if unit:
            type_str = UnitCalculator.get_unit_type(unit)
            if type_str == "weight":
                unit_type = UnitType.WEIGHT
            elif type_str == "volume":
                unit_type = UnitType.VOLUME
            elif type_str == "count":
                unit_type = UnitType.COUNT
            else:
                unit_type = UnitType.UNKNOWN

        return {
            'quantity': Decimal(str(quantity)) if quantity is not None else None,
            'unit': unit,
            'unit_type': unit_type if unit_type is not None else UnitType.UNKNOWN
        }

    @staticmethod
    def convert_to_standard_unit(quantity: Decimal, unit: str, unit_type: 'UnitType') -> Decimal:
        """
        Convert to standard unit (compatibility method)

        Args:
            quantity: Quantity to convert
            unit: Unit to convert from
            unit_type: Type of unit

        Returns:
            Converted quantity in standard units
        """
        normalized_qty, normalized_unit = UnitCalculator.normalize_to_standard_unit(
            float(quantity), unit
        )
        return Decimal(str(normalized_qty)) if normalized_qty is not None else quantity

    @staticmethod
    def calculate_unit_price(price: Decimal, quantity: Decimal, unit: str) -> Optional[Decimal]:
        """
        Calculate unit price (compatibility method)

        Args:
            price: Product price
            quantity: Product quantity
            unit: Unit type

        Returns:
            Price per unit or None
        """
        if price < 0:
            return None
        return UnitCalculator.calculate_unit_price(price, float(quantity), unit)

    @staticmethod
    def calculate_from_title(title: str, price: Decimal) -> dict:
        """
        Complete unit price calculation from title (compatibility method)

        Args:
            title: Product title
            price: Product price

        Returns:
            Dictionary with all calculation results
        """
        # Extract unit info
        quantity, unit = UnitCalculator.extract_unit_from_title(title)

        if not quantity or not unit:
            return {
                'unit_price': None,
                'quantity': None,
                'unit': None,
                'unit_type': None
            }

        # Normalize to standard units
        normalized_qty, normalized_unit = UnitCalculator.normalize_to_standard_unit(quantity, unit)

        # Determine unit type
        type_str = UnitCalculator.get_unit_type(normalized_unit or unit)
        unit_type = UnitType.UNKNOWN
        if type_str == "weight":
            unit_type = UnitType.WEIGHT
        elif type_str == "volume":
            unit_type = UnitType.VOLUME
        elif type_str == "count":
            unit_type = UnitType.COUNT

        # Calculate unit price
        unit_price = UnitCalculator.calculate_unit_price(
            price,
            normalized_qty if normalized_qty is not None else quantity,
            normalized_unit if normalized_unit is not None else unit
        )

        return {
            'unit_price': unit_price,
            'quantity': Decimal(str(normalized_qty)) if normalized_qty is not None else Decimal(str(quantity)),
            'unit': normalized_unit if normalized_unit is not None else unit,
            'unit_type': unit_type
        }
