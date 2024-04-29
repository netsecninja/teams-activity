# Teams Activity Tool
Captures Microsoft Teams application logs and parses to show activity

# Usage
```
usage: teams_activity.py [-h] [-e] [-a] [-d] [-t TIMEOUT] [-l LOGS]

Teams Activity Tool v1.2
Captures events in Teams logs to indicate activity. Outputs data in various formats.

options:
  -h, --help            show this help message and exit
  -e, --events          Outputs event log
  -a, --activity        Outputs activity log
  -d, --daily           Outputs daily hour totals
  -t TIMEOUT, --timeout TIMEOUT
                        Timeout setting in minutes for computer before auto-lock. Default is 30.
  -l LOGS, --logs LOGS  Path of logs to parse. Typical location is  which includes logs.txt and old_logs_*.txt.
```
# Screenshots
Events output example:

![Event output](/screenshots/Event.png)

Activity output example:

![Activity output](/screenshots/Activity.png)

Daily output example:

![Daily output](/screenshots/Daily.png)
