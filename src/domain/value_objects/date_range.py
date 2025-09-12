"""
Value Objects - Business Domain
Hexagonal Architecture DDD
"""
from datetime import date, timedelta
from typing import Optional
from dataclasses import dataclass


@dataclass(frozen=True)
class DateRange:
    """
    Value Object representing a date range for search.

    Immutable and contains business logic related to date ranges.
    """
    start_date: date
    end_date: date

    def __post_init__(self):
        """Date range validation"""
        if self.start_date > self.end_date:
            raise ValueError("Start date must be before or equal to end date")

    @classmethod
    def from_days_back(cls, days_back: int = 0, base_date: Optional[date] = None) -> 'DateRange':
        """Create a date range going back X days from a base date

        Args:
            days_back: Number of days to go back (0 = only today)
            base_date: Base date (today by default)

        Returns:
            DateRange instance
        """
        if base_date is None:
            base_date = date.today()

        if days_back == 0:
            # Only today
            return cls(start_date=base_date, end_date=base_date)
        else:
            # From today back to X days
            start_date = base_date - timedelta(days=days_back)
            return cls(start_date=start_date, end_date=base_date)

    def contains(self, check_date: date) -> bool:
        """Check if a date is within this range"""
        return self.start_date <= check_date <= self.end_date

    def duration_days(self) -> int:
        """Return the duration in days"""
        return (self.end_date - self.start_date).days + 1

    def overlaps_with(self, other: 'DateRange') -> bool:
        """Check if this range overlaps with another"""
        return (self.start_date <= other.end_date and
                self.end_date >= other.start_date)

    def to_dict(self) -> dict:
        """Convert to dictionary for serialization"""
        return {
            'start_date': self.start_date.isoformat(),
            'end_date': self.end_date.isoformat(),
            'duration_days': self.duration_days()
        }

    def __str__(self):
        """
        String representation in the format 'YYYY-MM-DD  YYYY-MM-DD' for tests and display.
        """
        return f"{self.start_date.strftime('%Y-%m-%d')}  {self.end_date.strftime('%Y-%m-%d')}"


@dataclass(frozen=True)
class Source:
    """
    Value Object representing a technology watch source.
    """
    name: str
    url: str
    description: Optional[str] = None

    def __post_init__(self):
        """Source validation"""
        if not self.name or not self.name.strip():
            raise ValueError("Source name cannot be empty")
        if not self.url or not self.url.strip():
            raise ValueError("Source URL cannot be empty")

    def matches_filter(self, filter_name: str) -> bool:
        """Check if the source matches the filter"""
        if not filter_name or filter_name.lower() == "all sources":
            return True
        return self.name.lower() == filter_name.lower()
