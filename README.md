# nyurban-schedule-scraper
Scrape calendar events from NYUrban website and publish to Google calendar

# Usage
urban_schedule_script.py -u <username> -p <password> [-c <calendarName>] -t... <teamId>
        -u --username
                Login name for nyurban website
        -p --password
                Login password for nyurban website
        -c --calendar   Default: primary
                Name (or 'summary') of Google Calendar
        -t --team
                List of team IDs to get data for from NYUrban website
        -h --help
                Print this message
