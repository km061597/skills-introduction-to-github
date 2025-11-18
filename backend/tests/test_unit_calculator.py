"""
Unit tests for unit price calculator
"""
import pytest
from decimal import Decimal

from app.unit_calculator import UnitPriceCalculator, UnitType


class TestUnitPriceExtraction:
    """Test unit extraction from product titles"""

    def test_extract_pounds(self):
        """Test extracting pounds from title"""
        result = UnitPriceCalculator.extract_unit_info("Protein Powder 5 lb")
        assert result['quantity'] == Decimal('5')
        assert result['unit'] == 'lb'
        assert result['unit_type'] == UnitType.WEIGHT

    def test_extract_ounces(self):
        """Test extracting ounces from title"""
        result = UnitPriceCalculator.extract_unit_info("Coffee Beans 12 oz")
        assert result['quantity'] == Decimal('12')
        assert result['unit'] == 'oz'

    def test_extract_count(self):
        """Test extracting count from title"""
        result = UnitPriceCalculator.extract_unit_info("Vitamin C 100 Count")
        assert result['quantity'] == Decimal('100')
        assert result['unit'] == 'count'
        assert result['unit_type'] == UnitType.COUNT

    def test_extract_fluid_ounces(self):
        """Test extracting fluid ounces from title"""
        result = UnitPriceCalculator.extract_unit_info("Shampoo 16 fl oz")
        assert result['quantity'] == Decimal('16')
        assert result['unit'] == 'fl oz'
        assert result['unit_type'] == UnitType.VOLUME

    def test_extract_pack(self):
        """Test extracting pack quantity"""
        result = UnitPriceCalculator.extract_unit_info("Protein Bars 12 Pack")
        assert result['quantity'] == Decimal('12')
        assert result['unit'] in ['pack', 'count']

    def test_no_unit_found(self):
        """Test when no unit is found"""
        result = UnitPriceCalculator.extract_unit_info("Generic Product")
        assert result['quantity'] is None
        assert result['unit'] is None


class TestUnitConversion:
    """Test unit conversion to standard units"""

    def test_pounds_to_ounces(self):
        """Test converting pounds to ounces"""
        oz = UnitPriceCalculator.convert_to_standard_unit(
            quantity=Decimal('5'),
            unit='lb',
            unit_type=UnitType.WEIGHT
        )
        assert oz == Decimal('80')  # 5 * 16

    def test_kilograms_to_ounces(self):
        """Test converting kilograms to ounces"""
        oz = UnitPriceCalculator.convert_to_standard_unit(
            quantity=Decimal('1'),
            unit='kg',
            unit_type=UnitType.WEIGHT
        )
        assert oz == Decimal('35.274')  # 1 kg = 35.274 oz

    def test_liters_to_fluid_ounces(self):
        """Test converting liters to fluid ounces"""
        fl_oz = UnitPriceCalculator.convert_to_standard_unit(
            quantity=Decimal('1'),
            unit='L',
            unit_type=UnitType.VOLUME
        )
        assert fl_oz == Decimal('33.814')  # 1 L = 33.814 fl oz

    def test_count_no_conversion(self):
        """Test that count units don't convert"""
        count = UnitPriceCalculator.convert_to_standard_unit(
            quantity=Decimal('100'),
            unit='count',
            unit_type=UnitType.COUNT
        )
        assert count == Decimal('100')


class TestUnitPriceCalculation:
    """Test unit price calculations"""

    def test_calculate_unit_price_weight(self):
        """Test calculating unit price for weight-based product"""
        unit_price = UnitPriceCalculator.calculate_unit_price(
            price=Decimal('49.99'),
            quantity=Decimal('80'),  # 5 lb = 80 oz
            unit='oz'
        )
        assert unit_price == Decimal('0.6249')  # 49.99 / 80

    def test_calculate_unit_price_count(self):
        """Test calculating unit price for count-based product"""
        unit_price = UnitPriceCalculator.calculate_unit_price(
            price=Decimal('19.99'),
            quantity=Decimal('100'),
            unit='count'
        )
        assert unit_price == Decimal('0.1999')  # 19.99 / 100

    def test_calculate_unit_price_zero_quantity(self):
        """Test that zero quantity returns None"""
        unit_price = UnitPriceCalculator.calculate_unit_price(
            price=Decimal('19.99'),
            quantity=Decimal('0'),
            unit='oz'
        )
        assert unit_price is None

    def test_calculate_unit_price_negative_price(self):
        """Test that negative price returns None"""
        unit_price = UnitPriceCalculator.calculate_unit_price(
            price=Decimal('-19.99'),
            quantity=Decimal('100'),
            unit='count'
        )
        assert unit_price is None


class TestEndToEndCalculation:
    """Test complete unit price calculation flow"""

    def test_full_calculation_protein_powder(self):
        """Test complete calculation for protein powder"""
        title = "Optimum Nutrition Whey Protein 5 lb"
        price = Decimal('54.99')

        result = UnitPriceCalculator.calculate_from_title(title, price)

        assert result['unit_price'] is not None
        assert result['quantity'] == Decimal('80')  # 5 lb = 80 oz
        assert result['unit'] == 'oz'
        assert result['unit_type'] == UnitType.WEIGHT
        assert result['unit_price'] < Decimal('1.0')  # Should be under $1/oz

    def test_full_calculation_vitamins(self):
        """Test complete calculation for vitamins"""
        title = "Vitamin C 1000mg 100 Count"
        price = Decimal('19.99')

        result = UnitPriceCalculator.calculate_from_title(title, price)

        assert result['unit_price'] is not None
        assert result['quantity'] == Decimal('100')
        assert result['unit'] == 'count'
        assert result['unit_type'] == UnitType.COUNT

    def test_full_calculation_no_unit(self):
        """Test calculation when no unit is found"""
        title = "Generic Product"
        price = Decimal('9.99')

        result = UnitPriceCalculator.calculate_from_title(title, price)

        assert result['unit_price'] is None
        assert result['quantity'] is None
        assert result['unit'] is None
