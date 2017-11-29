#!/usr/bin/env python
import sys, os
import time
import subprocess
from subprocess import check_output

def main():
    last_update_time = 0
    update_time_period = 2

    port_num = '441'

    cmd = 'nc.traditional -ul -p {} -e /root/radio_api/node_poll.py'.format(
            port_num)
    p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE)

    while True:
        if time.time() - last_update_time > update_time_period:
            p.kill()
            cmd = 'nc.traditional -ul -p {} -e /root/radio_api/node_poll.py'.format(
                    port_num)
            p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE)
            last_update_time = time.time()

        time.sleep(update_time_period / 2)

if __name__ == '__main__':
    main()
