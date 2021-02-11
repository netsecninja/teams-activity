# Teams Activity Tool
Captures Microsoft Teams application logs and parses to show activity

# Usage
```
usage: teams_activity.py [-h] [-e] [-a] [-d] logs

Teams Activity Tool v1.1
Captures events in Teams logs to indicate activity. Outputs data in various formats.

positional arguments:
  logs            Path of logs to parse. Typical location is C:\Users\<PROFILE>\AppData\Roaming\Microsoft\Teams which includes logs.txt and old_logs_*.txt.

optional arguments:
  -h, --help      show this help message and exit
  -e, --events    Outputs event log
  -a, --activity  Outputs activity log
  -d, --daily     Outputs daily hour totals
  ```
# Screenshots
Events output example:

![Event output](/screenshots/Event.png)

Activity output example:

![Activity output](/screenshots/Activity.png)

Daily output example:

![Daily output](/screenshots/Daily.png)
