#!/usr/bin/env python3
# Title: Teams Activity Tool
# Author: Jeremiah Bess
# Description: Captures local Teams application logs and parses to show activity

# Imports
import argparse
import os
import glob
import datetime
import re
import appdirs

# Globals
version = '1.2'
default_log_dir = ''
startup = 'StatusIndicatorStateService: initialized'
shutdown_app = 'session-end fired'
app_killed = '"exitCode":1073807364'
locked = 'Machine is locked'
unlocked = 'Machine is unlocked'
idle = 'Machine has been idle for'

# Functions
def get_default_dir():
    if os.name == 'nt':
        #if true == Windows 
        log_dir = os.getenv('appdata')
        default_log_dir = os.path.join(log_dir,'Microsoft','Teams')
    elif os.name == 'posix':
        log = os.path.join(appdirs.user_config_dir(),'Microsoft','Teams','logs.txt')
        if os.path.exists(log):
            #if true == Mac OS
            default_log_dir = os.path.dirname(log)
        else:
            #else Linux 
            default_log_dir = os.path.join(appdirs.user_config_dir(),'Microsoft','Microsoft Teams')
    return default_log_dir

def get_args():
    global version
    global default_log_dir
    
    parser = argparse.ArgumentParser(description=f'Teams Activity Tool v{version}\nCaptures events in Teams logs to indicate activity. Outputs data in various formats.', formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument('-e', '--events', action='store_true', help='Outputs event log')
    parser.add_argument('-a', '--activity', action='store_true', help='Outputs activity log')
    parser.add_argument('-d', '--daily', action='store_true', help='Outputs daily hour totals')
    parser.add_argument('-t', '--timeout', default=30, type=int, help='Timeout setting in minutes for computer before auto-lock. Default is 30.')
    parser.add_argument('-l', '--logs', default=get_default_dir(), required=False, action='store', help=f'Path of logs to parse. Typical location is {default_log_dir} which includes logs.txt and old_logs_*.txt.')
    
    args = parser.parse_args()
    

    # Validate path exists
    if not os.path.isdir(args.logs):
        print(f'\nInvalid directory name {args.logs}\n')
        exit(1)
    else:
        return args

def get_files(log_path):
    log_files = []

    # Add old_logs_<DATESTAMP>.txt
    old_log_pattern = os.path.join(log_path,'old_logs_*.txt')
    for file in glob.glob(old_log_pattern):
        log_files.append(file)

    # Add logs.txt
    log_pattern = os.path.join(log_path,'logs.txt')
    for file in glob.glob(log_pattern):
        log_files.append(file)

    return log_files

def get_events(log_files, timeout):
    global startup
    global shutdown_app
    global app_killed
    global locked
    global unlocked
    global idle

    events = {} # {dt:{'type': type, 'event': event}}
    
    for file in log_files:
        # Read file contents
        with open(file) as log:
            entries = log.readlines()

        # Populate daily_activity dictionary
        previous_entry = '' # Used to compare timeout locks vs manual locks
        for entry in entries:     
            # Determine action type and event
            if startup in entry:
                action = {'type': 'start', 'event': 'Teams startup'}
            elif shutdown_app in entry:
                action = {'type': 'stop', 'event': 'Teams shutdown'}
            elif app_killed in entry:
                action = {'type': 'stop', 'event': 'Teams killed'}
            elif locked in entry:
                if idle in previous_entry:
                    action = {'type': 'stop', 'event': 'Computer locked by timeout'}
                else:
                    action = {'type': 'stop', 'event': 'Computer locked by user'}
            elif unlocked in entry:
                action = {'type': 'start', 'event': 'Computer unlocked'}
            else:
                previous_entry = entry
                continue

            # Get datetime objects
            date = ' '.join(entry.split(' ')[0:6]) # Fri Jan 22 2021 12:30:18 GMT-0700
            try:
                dt = datetime.datetime.strptime(date, '%a %b %d %Y %H:%M:%S %Z%z')
            except ValueError:
                continue # Ignore partial lines without datetime stamp, usually at beginning of logs
            if action['event'] == 'Computer locked by timeout': # Subtract timeout amount to get actual activity stop time
                dt = dt + timeout
            events[dt] = action # Add to dictionary

    return events

def get_activity(events):
    activities = [] # ['start_time --> stop_time: hours',...]
    ordered_dt = list(events.keys())
    ordered_dt.sort()

    # Find start/stop events
    start_event = ''
    stop_event = ''
    for dt in ordered_dt:
        if not start_event and events[dt]['type'] == 'start': # Get next start event
            start_event = dt
        elif not start_event: # Skip until a start event
            continue
        elif not stop_event and events[dt]['type'] == 'stop': # Get next stop event
            stop_event = dt
            # Calc time difference
            diff = stop_event - start_event
            hours = round(diff.total_seconds()/3600, 2) # Convert to hours
            # Log pair and hours
            activities.append(f'{start_event.isoformat()} --> {stop_event.isoformat()}: {hours} hours')       
            # Clear start/stop events
            start_event = ''
            stop_event = ''
        else: # Skip until a stop event
            continue
        
    return activities

def get_daily(activities):
    dailies = {} # {date: hours,...}

    # Calculate daily hours
    for activity in activities:
        start = datetime.datetime.fromisoformat(activity[0:19])
        start_date = start.date()
        stop = datetime.datetime.fromisoformat(activity[30:49])
        stop_date = stop.date()
        # Figure if time spans dates
        if start_date == stop_date:
            hours = float(activity[57:61])
            if not start_date in dailies:
                dailies[start_date] = hours
            else:
                dailies[start_date] += hours
        else:
            eod = datetime.datetime.fromisoformat(f'{start_date}T23:59:59') # End of day
            bod = datetime.datetime.fromisoformat(f'{stop_date}T00:00:00') # Beginning of day
            # Find time differences
            start_time = eod - start
            stop_time = stop - bod
            # Convert to hours
            start_hours = round(start_time.total_seconds()/3600, 2)
            stop_hours = round(stop_time.total_seconds()/3600, 2)
            # Add proper time to appropriate date
            if not start_date in dailies:
                dailies[start_date] = start_hours
            else:
                dailies[start_date] += start_hours
            if not stop_date in dailies:
                dailies[stop_date] = stop_hours
            else:
                dailies[stop_date] += stop_hours

    return dailies    
 
def main(): 
    # Get arguments
    args = get_args()

    # Get log files
    log_files = get_files(args.logs)

    # Get events
    timeout = datetime.timedelta(minutes=-args.timeout) # Subtract minutes from end time to get when activity likely stopped
    events = get_events(log_files, timeout) # Unordered dictionary

    # Get activities
    activities = get_activity(events) # Ordered list

    # Get dailies
    dailies = get_daily(activities) # Unordered dictionary
    
    # Print events
    if args.events:
        ordered_events = list(events.keys())
        ordered_events.sort()
        print('\nEvent log:')
        for dt in ordered_events:
            print(f'{dt.isoformat()}: {events[dt]["event"]}')

    # Print activities
    if args.activity:
        print('\nActivity log:')
        for activity in activities:
            print(activity)        

    # Print dailies
    if args.daily:
        ordered_days = list(dailies.keys())
        ordered_days.sort()
        print('\nDaily log:')
        for date in ordered_days:
            print(f'{date}: {round(dailies[date], 2)}')
            
    print('\r')

# Main
if __name__ == '__main__':
    main()
