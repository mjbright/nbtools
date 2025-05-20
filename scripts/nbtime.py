#!/usr/bin/env python3

import os, sys
import time

command=" ".join(sys.argv[1:])

# Run command:
start_ts=time.time()
os.system( command )
end_ts=time.time()

# Difference between two timestamps
delta = end_ts - start_ts

days      = int(delta / (60 * 60 * 24))
rem_secs  = delta - ( days * 60 * 60 * 24 )
hours     = int(rem_secs / (60 * 60))
rem_secs -= hours * 60 * 60
mins      = int(rem_secs / 60)
rem_secs -= mins * 60

if days > 0:
    print(f'Took [{delta:.2f}s]  {days}d {hours}h {mins}m {rem_secs:.2f}s: {command}')
elif hours > 0:
    print(f'Took [{delta:.2f}s]  {hours}h {mins}m {rem_secs:.2f}s: {command}')
elif mins > 0:
    print(f'Took [{delta:.2f}s]  {mins}m {rem_secs:.2f}s: {command}')
else:
    print(f'Took  {rem_secs:.2f}s: {command}')

# test: 5d, 7h, 23m, 46s
#delta = (60 * 60 * 24 * 5) + (60 * 60 * 7) + (60 * 23) + 46.4
#delta = (60 * 60 * 7) + (60 * 23) + 46.4
#delta = (60 * 23) + 46.4
#delta = 46.4
# f'{value:{width}.{precision}}'
#print('Difference is:', delta)

