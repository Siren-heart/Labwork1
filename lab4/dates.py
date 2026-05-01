# Practice 4: dates and time

from datetime import datetime, timedelta, timezone

# Create a datetime object for the current moment.
now = datetime.now()
print("Current datetime:", now)

# Create a custom date object.
custom_date = datetime(2026, 4, 28, 14, 30, 0)
print("Custom datetime:", custom_date)

# Format a date as a readable string.
formatted = custom_date.strftime("%d-%m-%Y %H:%M:%S")
print("Formatted datetime:", formatted)

# Calculate time differences with timedelta.
deadline = custom_date + timedelta(days=7)
remaining = deadline - custom_date
print("Deadline:", deadline)
print("Difference in days:", remaining.days)

# Work with timezones using UTC offsets.
utc_time = datetime.now(timezone.utc)
almaty_time = utc_time.astimezone(timezone(timedelta(hours=5)))
print("UTC time:", utc_time.strftime("%Y-%m-%d %H:%M:%S %Z"))
print("UTC+5 time:", almaty_time.strftime("%Y-%m-%d %H:%M:%S %Z"))
