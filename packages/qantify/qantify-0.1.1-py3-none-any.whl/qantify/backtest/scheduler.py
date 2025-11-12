"""Advanced calendar and event scheduling system for market events."""

from __future__ import annotations

import asyncio
import json
import logging
from dataclasses import dataclass, field
from datetime import datetime, time, timedelta
from typing import Any, Callable, Dict, List, Optional, Set, Tuple, Union
from enum import Enum
from pathlib import Path
import calendar as cal

import pandas as pd
import numpy as np
from dateutil import parser as date_parser
from dateutil.relativedelta import relativedelta

from qantify.backtest.orchestration import EventInjection, EventInjector

logger = logging.getLogger(__name__)


class EventType(Enum):
    """Types of market events that can be scheduled."""

    EARNINGS = "earnings"
    ECONOMIC_DATA = "economic_data"
    FED_MEETING = "fed_meeting"
    DIVIDEND = "dividend"
    SPLIT = "split"
    MERGER = "merger"
    IPO = "ipo"
    DELISTING = "delisting"
    HOLIDAY = "holiday"
    CUSTOM = "custom"


class EventPriority(Enum):
    """Priority levels for event processing."""

    LOW = 1
    MEDIUM = 2
    HIGH = 3
    CRITICAL = 4


@dataclass(slots=True)
class ScheduledEvent:
    """A scheduled market event."""

    event_id: str
    event_type: EventType
    timestamp: datetime
    symbol: Optional[str] = None
    title: str = ""
    description: str = ""
    data: Dict[str, Any] = field(default_factory=dict)
    priority: EventPriority = EventPriority.MEDIUM
    recurrence: Optional[str] = None  # Cron-like expression or custom recurrence
    affected_assets: Set[str] = field(default_factory=set)
    market_impact: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)

    def to_injection(self) -> EventInjection:
        """Convert to EventInjection for use in orchestration."""
        return EventInjection(
            timestamp=self.timestamp,
            event_type=self.event_type.value,
            data=self.data,
            affected_assets=self.affected_assets if self.affected_assets else {self.symbol} if self.symbol else set(),
            description=f"{self.title}: {self.description}"
        )


@dataclass(slots=True)
class CalendarConfig:
    """Configuration for the event calendar."""

    timezone: str = "America/New_York"  # Default to NYSE timezone
    market_hours: Dict[str, Tuple[time, time]] = field(default_factory=lambda: {
        "weekdays": (time(9, 30), time(16, 0)),
        "weekends": None
    })
    holidays: Set[datetime] = field(default_factory=set)
    enable_market_hours_filter: bool = True
    auto_adjust_to_market_hours: bool = True


class RecurrenceParser:
    """Parse recurrence patterns for scheduled events."""

    @staticmethod
    def parse_recurrence(recurrence: str) -> Callable[[datetime], datetime]:
        """Parse a recurrence string into a function that returns the next occurrence."""
        # Simple implementations for common patterns
        if recurrence == "daily":
            return lambda dt: dt + timedelta(days=1)
        elif recurrence == "weekly":
            return lambda dt: dt + timedelta(weeks=1)
        elif recurrence == "monthly":
            return lambda dt: dt + relativedelta(months=1)
        elif recurrence == "quarterly":
            return lambda dt: dt + relativedelta(months=3)
        elif recurrence == "annually" or recurrence == "yearly":
            return lambda dt: dt + relativedelta(years=1)
        else:
            # Try to parse as cron-like (simplified)
            return RecurrenceParser._parse_cron_like(recurrence)

    @staticmethod
    def _parse_cron_like(pattern: str) -> Callable[[datetime], datetime]:
        """Parse a simple cron-like pattern (minute hour day month day_of_week)."""
        parts = pattern.split()
        if len(parts) != 5:
            raise ValueError(f"Invalid cron pattern: {pattern}")

        minute, hour, day, month, dow = parts

        def next_occurrence(dt: datetime) -> datetime:
            # Simplified implementation - increment by day and check conditions
            candidate = dt + timedelta(days=1)
            while True:
                if (RecurrenceParser._matches_field(minute, candidate.minute) and
                    RecurrenceParser._matches_field(hour, candidate.hour) and
                    RecurrenceParser._matches_field(day, candidate.day) and
                    RecurrenceParser._matches_field(month, candidate.month) and
                    RecurrenceParser._matches_field(dow, candidate.weekday())):
                    return candidate
                candidate += timedelta(days=1)

        return next_occurrence

    @staticmethod
    def _matches_field(pattern: str, value: int) -> bool:
        """Check if a value matches a cron field pattern."""
        if pattern == "*":
            return True
        if "," in pattern:
            return any(RecurrenceParser._matches_field(p.strip(), value) for p in pattern.split(","))
        if "-" in pattern:
            start, end = map(int, pattern.split("-"))
            return start <= value <= end
        if "/" in pattern:
            base, step = pattern.split("/")
            base = base if base != "*" else "0"
            return (value - int(base)) % int(step) == 0
        return int(pattern) == value


class EarningsCalendar:
    """Specialized calendar for earnings events."""

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key
        self.cache: Dict[str, List[ScheduledEvent]] = {}

    async def fetch_earnings_calendar(
        self,
        symbols: List[str],
        start_date: datetime,
        end_date: datetime
    ) -> List[ScheduledEvent]:
        """Fetch earnings calendar from external sources."""
        events = []

        # In a real implementation, this would call financial APIs
        # For now, we'll create mock events based on typical earnings patterns
        for symbol in symbols:
            quarterly_events = self._generate_quarterly_earnings(symbol, start_date, end_date)
            events.extend(quarterly_events)

        return events

    def _generate_quarterly_earnings(
        self,
        symbol: str,
        start_date: datetime,
        end_date: datetime
    ) -> List[ScheduledEvent]:
        """Generate quarterly earnings events for a symbol."""
        events = []

        # Typical earnings months: Jan, Apr, Jul, Oct
        earnings_months = [1, 4, 7, 10]
        current_date = start_date.replace(day=1)

        while current_date <= end_date:
            if current_date.month in earnings_months:
                # Schedule earnings for 4th Thursday of the month (typical pattern)
                earnings_date = self._get_nth_weekday(current_date.year, current_date.month, 3, 3)  # 4th Thursday

                if start_date <= earnings_date <= end_date:
                    # After-hours release (typically 4:00 PM ET)
                    earnings_time = earnings_date.replace(hour=16, minute=0, second=0, microsecond=0)

                    event = ScheduledEvent(
                        event_id=f"earnings_{symbol}_{earnings_date.strftime('%Y%m%d')}",
                        event_type=EventType.EARNINGS,
                        timestamp=earnings_time,
                        symbol=symbol,
                        title=f"{symbol} Q{((earnings_date.month - 1) // 3) + 1} Earnings",
                        description=f"Quarterly earnings report for {symbol}",
                        data={
                            "quarter": ((earnings_date.month - 1) // 3) + 1,
                            "year": earnings_date.year,
                            "expected_impact": "high"
                        },
                        priority=EventPriority.HIGH,
                        recurrence="quarterly",
                        affected_assets={symbol}
                    )
                    events.append(event)

            current_date = current_date.replace(day=1) + relativedelta(months=1)

        return events

    def _get_nth_weekday(self, year: int, month: int, n: int, weekday: int) -> datetime:
        """Get the nth weekday of a month (0=Monday, 6=Sunday)."""
        first_of_month = datetime(year, month, 1)
        first_weekday = first_of_month.weekday()

        # Find first occurrence of the desired weekday
        days_to_add = (weekday - first_weekday) % 7
        first_occurrence = first_of_month + timedelta(days=days_to_add)

        # Add weeks to get nth occurrence
        target_date = first_occurrence + timedelta(weeks=n-1)

        # Make sure it's still in the same month
        if target_date.month != month:
            target_date = target_date - timedelta(weeks=1)

        return target_date


class EconomicCalendar:
    """Calendar for economic data releases."""

    def __init__(self):
        self.events = self._load_economic_events()

    def _load_economic_events(self) -> Dict[str, Dict[str, Any]]:
        """Load predefined economic events."""
        return {
            "non_farm_payrolls": {
                "name": "Non-Farm Payrolls",
                "release_day": "first_friday",
                "release_time": "08:30",
                "impact": "high",
                "description": "Monthly employment data"
            },
            "cpi": {
                "name": "Consumer Price Index",
                "release_day": "mid_month",
                "release_time": "08:30",
                "impact": "high",
                "description": "Monthly inflation data"
            },
            "fed_funds_rate": {
                "name": "Federal Funds Rate Decision",
                "release_day": "fomc_meeting",
                "release_time": "14:00",
                "impact": "critical",
                "description": "FOMC interest rate decision"
            },
            "gdp": {
                "name": "GDP Report",
                "release_day": "quarterly_first",
                "release_time": "08:30",
                "impact": "high",
                "description": "Quarterly GDP growth"
            }
        }

    async def generate_economic_events(
        self,
        start_date: datetime,
        end_date: datetime
    ) -> List[ScheduledEvent]:
        """Generate economic data release events."""
        events = []

        current_date = start_date
        while current_date <= end_date:
            for event_key, event_info in self.events.items():
                event_dates = self._get_event_dates(current_date.year, current_date.month, event_key)

                for event_date in event_dates:
                    if start_date <= event_date <= end_date:
                        event_time = datetime.combine(event_date, self._parse_time(event_info["release_time"]))

                        priority = EventPriority.CRITICAL if event_info["impact"] == "critical" else \
                                 EventPriority.HIGH if event_info["impact"] == "high" else EventPriority.MEDIUM

                        event = ScheduledEvent(
                            event_id=f"economic_{event_key}_{event_date.strftime('%Y%m%d')}",
                            event_type=EventType.ECONOMIC_DATA,
                            timestamp=event_time,
                            title=event_info["name"],
                            description=event_info["description"],
                            data={
                                "indicator": event_key,
                                "impact_level": event_info["impact"],
                                "expected_volatility": True
                            },
                            priority=priority,
                            affected_assets=set(),  # Affects all assets
                            market_impact={
                                "volatility_spike": True,
                                "volume_multiplier": 2.0 if event_info["impact"] == "high" else 1.5
                            }
                        )
                        events.append(event)

            current_date = current_date.replace(day=1) + relativedelta(months=1)

        return events

    def _get_event_dates(self, year: int, month: int, event_key: str) -> List[datetime]:
        """Get event dates for a specific economic indicator."""
        event_info = self.events[event_key]

        if event_info["release_day"] == "first_friday":
            return [self._get_nth_weekday(year, month, 1, 4)]  # First Friday
        elif event_info["release_day"] == "mid_month":
            return [datetime(year, month, 15)]  # Mid-month
        elif event_info["release_day"] == "fomc_meeting":
            return self._get_fomc_dates(year)
        elif event_info["release_day"] == "quarterly_first":
            if month in [1, 4, 7, 10]:
                return [datetime(year, month, 1)]
            return []
        else:
            return []

    def _get_fomc_dates(self, year: int) -> List[datetime]:
        """Get FOMC meeting dates for a year."""
        # Simplified FOMC schedule (typically 8 meetings per year)
        fomc_months = [1, 3, 4, 6, 7, 9, 10, 12]
        dates = []

        for month in fomc_months:
            # Third Wednesday of the month (typical FOMC pattern)
            third_wednesday = self._get_nth_weekday(year, month, 3, 2)  # Wednesday = 2
            dates.append(third_wednesday)

        return dates

    def _get_nth_weekday(self, year: int, month: int, n: int, weekday: int) -> datetime:
        """Get the nth weekday of a month."""
        first_of_month = datetime(year, month, 1)
        first_weekday = first_of_month.weekday()

        days_to_add = (weekday - first_weekday) % 7
        first_occurrence = first_of_month + timedelta(days=days_to_add)

        target_date = first_occurrence + timedelta(weeks=n-1)

        if target_date.month != month:
            target_date = target_date - timedelta(weeks=1)

        return target_date

    def _parse_time(self, time_str: str) -> time:
        """Parse time string to time object."""
        hour, minute = map(int, time_str.split(":"))
        return time(hour, minute)


class EventScheduler:
    """Main event scheduling and management system."""

    def __init__(self, calendar_config: Optional[CalendarConfig] = None):
        self.config = calendar_config or CalendarConfig()
        self.events: Dict[str, ScheduledEvent] = {}
        self.earnings_calendar = EarningsCalendar()
        self.economic_calendar = EconomicCalendar()
        self.event_queue: List[ScheduledEvent] = []

    async def schedule_event(self, event: ScheduledEvent) -> str:
        """Schedule a new event."""
        # Adjust timing if needed
        if self.config.auto_adjust_to_market_hours:
            event.timestamp = self._adjust_to_market_hours(event.timestamp)

        self.events[event.event_id] = event
        logger.info(f"Scheduled event: {event.title} at {event.timestamp}")
        return event.event_id

    async def schedule_earnings_calendar(
        self,
        symbols: List[str],
        start_date: datetime,
        end_date: datetime
    ) -> List[str]:
        """Schedule earnings events for multiple symbols."""
        events = await self.earnings_calendar.fetch_earnings_calendar(symbols, start_date, end_date)
        event_ids = []

        for event in events:
            event_id = await self.schedule_event(event)
            event_ids.append(event_id)

        logger.info(f"Scheduled {len(event_ids)} earnings events")
        return event_ids

    async def schedule_economic_calendar(
        self,
        start_date: datetime,
        end_date: datetime
    ) -> List[str]:
        """Schedule economic data release events."""
        events = await self.economic_calendar.generate_economic_events(start_date, end_date)
        event_ids = []

        for event in events:
            event_id = await self.schedule_event(event)
            event_ids.append(event_id)

        logger.info(f"Scheduled {len(event_ids)} economic events")
        return event_ids

    async def get_upcoming_events(
        self,
        start_time: datetime,
        end_time: Optional[datetime] = None,
        event_types: Optional[List[EventType]] = None,
        symbols: Optional[List[str]] = None
    ) -> List[ScheduledEvent]:
        """Get upcoming events within a time range."""
        if end_time is None:
            end_time = start_time + timedelta(days=30)

        upcoming = []

        for event in self.events.values():
            if start_time <= event.timestamp <= end_time:
                if event_types and event.event_type not in event_types:
                    continue
                if symbols and event.symbol and event.symbol not in symbols:
                    continue
                upcoming.append(event)

        return sorted(upcoming, key=lambda x: x.timestamp)

    async def get_events_for_date(self, date: datetime) -> List[ScheduledEvent]:
        """Get all events for a specific date."""
        start_of_day = date.replace(hour=0, minute=0, second=0, microsecond=0)
        end_of_day = start_of_day + timedelta(days=1)

        return await self.get_upcoming_events(start_of_day, end_of_day)

    def create_event_injection(self, event: ScheduledEvent) -> EventInjection:
        """Convert a scheduled event to an event injection."""
        return event.to_injection()

    async def build_injection_schedule(
        self,
        start_date: datetime,
        end_date: datetime,
        symbols: Optional[List[str]] = None
    ) -> List[EventInjection]:
        """Build a complete schedule of event injections."""
        upcoming_events = await self.get_upcoming_events(
            start_date, end_date,
            symbols=symbols
        )

        injections = [self.create_event_injection(event) for event in upcoming_events]
        logger.info(f"Built injection schedule with {len(injections)} events")

        return injections

    def _adjust_to_market_hours(self, timestamp: datetime) -> datetime:
        """Adjust timestamp to fall within market hours if necessary."""
        if not self.config.enable_market_hours_filter:
            return timestamp

        # Convert to config timezone
        ts_local = timestamp
        if timestamp.tzinfo is None:
            ts_local = timestamp.replace(tzinfo=pd.Timestamp(timestamp).tz_localize(self.config.timezone).tz)
        else:
            ts_local = timestamp.astimezone(pd.Timestamp(timestamp).tz_convert(self.config.timezone).tz)

        weekday = ts_local.weekday()
        market_hours = self.config.market_hours.get("weekdays" if weekday < 5 else "weekends")

        if market_hours is None:  # No market hours for this day type
            return timestamp

        open_time, close_time = market_hours
        current_time = ts_local.time()

        if current_time < open_time:
            # Before market open - move to open
            adjusted = ts_local.replace(hour=open_time.hour, minute=open_time.minute, second=0, microsecond=0)
        elif current_time > close_time:
            # After market close - move to next day open
            next_day = ts_local + timedelta(days=1)
            adjusted = next_day.replace(hour=open_time.hour, minute=open_time.minute, second=0, microsecond=0)
        else:
            # Within market hours - keep as is
            adjusted = ts_local

        # Convert back to original timezone if needed
        return adjusted

    async def export_schedule(self, filepath: Union[str, Path]) -> None:
        """Export the current schedule to a JSON file."""
        schedule_data = {
            "config": {
                "timezone": self.config.timezone,
                "market_hours": {
                    k: [t.isoformat() for t in v] if v else None
                    for k, v in self.config.market_hours.items()
                },
                "enable_market_hours_filter": self.config.enable_market_hours_filter,
                "auto_adjust_to_market_hours": self.config.auto_adjust_to_market_hours
            },
            "events": [
                {
                    "event_id": event.event_id,
                    "event_type": event.event_type.value,
                    "timestamp": event.timestamp.isoformat(),
                    "symbol": event.symbol,
                    "title": event.title,
                    "description": event.description,
                    "data": event.data,
                    "priority": event.priority.value,
                    "recurrence": event.recurrence,
                    "affected_assets": list(event.affected_assets),
                    "market_impact": event.market_impact,
                    "created_at": event.created_at.isoformat(),
                    "updated_at": event.updated_at.isoformat()
                }
                for event in self.events.values()
            ]
        }

        filepath = Path(filepath)
        with open(filepath, 'w') as f:
            json.dump(schedule_data, f, indent=2, default=str)

        logger.info(f"Exported schedule to {filepath}")

    async def import_schedule(self, filepath: Union[str, Path]) -> None:
        """Import a schedule from a JSON file."""
        filepath = Path(filepath)
        with open(filepath, 'r') as f:
            schedule_data = json.load(f)

        # Restore config
        config_data = schedule_data["config"]
        self.config = CalendarConfig(
            timezone=config_data["timezone"],
            market_hours={
                k: tuple(time.fromisoformat(t) for t in v) if v else None
                for k, v in config_data["market_hours"].items()
            },
            enable_market_hours_filter=config_data["enable_market_hours_filter"],
            auto_adjust_to_market_hours=config_data["auto_adjust_to_market_hours"]
        )

        # Restore events
        for event_data in schedule_data["events"]:
            event = ScheduledEvent(
                event_id=event_data["event_id"],
                event_type=EventType(event_data["event_type"]),
                timestamp=datetime.fromisoformat(event_data["timestamp"]),
                symbol=event_data["symbol"],
                title=event_data["title"],
                description=event_data["description"],
                data=event_data["data"],
                priority=EventPriority(event_data["priority"]),
                recurrence=event_data["recurrence"],
                affected_assets=set(event_data["affected_assets"]),
                market_impact=event_data["market_impact"],
                created_at=datetime.fromisoformat(event_data["created_at"]),
                updated_at=datetime.fromisoformat(event_data["updated_at"])
            )
            self.events[event.event_id] = event

        logger.info(f"Imported schedule with {len(self.events)} events from {filepath}")


# Convenience functions
async def create_earnings_injection(
    symbol: str,
    timestamp: datetime,
    surprise_pct: float,
    volatility_multiplier: float = 2.0
) -> EventInjection:
    """Create an earnings event injection."""
    return EventInjector.create_earnings_event(symbol, timestamp, surprise_pct, volatility_multiplier)


async def schedule_market_events(
    symbols: List[str],
    start_date: datetime,
    end_date: datetime,
    include_earnings: bool = True,
    include_economic: bool = True
) -> List[EventInjection]:
    """Convenience function to schedule common market events."""
    scheduler = EventScheduler()

    if include_earnings:
        await scheduler.schedule_earnings_calendar(symbols, start_date, end_date)

    if include_economic:
        await scheduler.schedule_economic_calendar(start_date, end_date)

    return await scheduler.build_injection_schedule(start_date, end_date, symbols)


__all__ = [
    "EventScheduler",
    "CalendarConfig",
    "ScheduledEvent",
    "EventType",
    "EventPriority",
    "EarningsCalendar",
    "EconomicCalendar",
    "RecurrenceParser",
    "create_earnings_injection",
    "schedule_market_events",
]
