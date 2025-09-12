"""
Unit tests for DateRange value object - DDD Hexagonal Architecture
"""
import unittest
from datetime import date, timedelta
from src.domain.value_objects.date_range import DateRange


class TestDateRange(unittest.TestCase):
    """Tests for DateRange value object"""

    def test_creation_with_dates(self):
        """Test creation with explicit dates"""
        start = date(2025, 9, 1)
        end = date(2025, 9, 8)

        date_range = DateRange(start_date=start, end_date=end)

        self.assertEqual(date_range.start_date, start)
        self.assertEqual(date_range.end_date, end)

    def test_from_days_back_zero(self):
        """Test creation with 0 days (today only)"""
        today = date.today()
        date_range = DateRange.from_days_back(0)

        self.assertEqual(date_range.start_date, today)
        self.assertEqual(date_range.end_date, today)

    def test_from_days_back_seven(self):
        """Test creation with 7 days back"""
        today = date.today()
        expected_start = today - timedelta(days=7)

        date_range = DateRange.from_days_back(7)

        self.assertEqual(date_range.start_date, expected_start)
        self.assertEqual(date_range.end_date, today)

    def test_from_days_back_thirty(self):
        """Test creation with 30 days back"""
        today = date.today()
        expected_start = today - timedelta(days=30)

        date_range = DateRange.from_days_back(30)

        self.assertEqual(date_range.start_date, expected_start)
        self.assertEqual(date_range.end_date, today)

    def test_contains_date_in_range(self):
        """Test if a date is within the range"""
        date_range = DateRange(
            start_date=date(2025, 9, 1),
            end_date=date(2025, 9, 10)
        )

        test_date = date(2025, 9, 5)
        self.assertTrue(date_range.contains(test_date))

    def test_contains_date_start_boundary(self):
        """Test start boundary date"""
        date_range = DateRange(
            start_date=date(2025, 9, 1),
            end_date=date(2025, 9, 10)
        )

        self.assertTrue(date_range.contains(date(2025, 9, 1)))

    def test_contains_date_end_boundary(self):
        """Test end boundary date"""
        date_range = DateRange(
            start_date=date(2025, 9, 1),
            end_date=date(2025, 9, 10)
        )

        self.assertTrue(date_range.contains(date(2025, 9, 10)))

    def test_contains_date_before_range(self):
        """Test date before the range"""
        date_range = DateRange(
            start_date=date(2025, 9, 1),
            end_date=date(2025, 9, 10)
        )

        test_date = date(2025, 8, 31)
        self.assertFalse(date_range.contains(test_date))

    def test_contains_date_after_range(self):
        """Test date after the range"""
        date_range = DateRange(
            start_date=date(2025, 9, 1),
            end_date=date(2025, 9, 10)
        )

        test_date = date(2025, 9, 11)
        self.assertFalse(date_range.contains(test_date))

    def test_str_representation(self):
        """Test string representation"""
        date_range = DateRange(
            start_date=date(2025, 9, 1),
            end_date=date(2025, 9, 10)
        )

        result = str(date_range)
        expected = "2025-09-01  2025-09-10"
        self.assertEqual(result, expected)


if __name__ == '__main__':
    unittest.main()
