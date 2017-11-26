#!/usr/bin/env python
import sys, os
import time
import subprocess
from subprocess import check_output

def get_routing_table():
    '''
    Runs the routing daemon on the host, and gets the routing table. Processes
    the routing table to return a list of dictionaries, each representing
    a row in the routing table.
    '''
    # Get the output of the routing daemon
    routing_output = subprocess.check_output(['route', '-n']).split('\n')

    # Throw away the header
    routing_lines = routing_output[2:]
    routes = []

    for routing_line in routing_lines:
        parts = routing_line.split(' ')
        parts = [part for part in parts if part != '']

        # Get the components based on the fixed format
        destination, gateway, genmask, flags, metric, ref, use, iface = parts[:8]

        current_route = {
          'destination': destination,
          'gateway': gateway,
          'genmask': genmask,
          'flags': flags,
          'metric': metric,
          'ref': ref,
          'use': use,
          'iface': iface
        }

        # Add this to the total routes existing
        routes.append(current_route)

    # A list of dictionaries, each of which represent a reachable route
    return routes

def get_my_internal_ip_address(routes, my_srn_number):
    '''
    Takes in a list of dictionaries from the routing daemon. Searches these till
    receives one which interacts with 'tap0' as well as with its own srn
    number as the destination, and decides that to be the IP address. Returns
    None if an IP is not found which matches these criterion.
    '''

    for route in routes:
        if route['iface'] == 'tap0':
            destination_ip = route['destination']
            last_octet = destination_ip.split('.')[-1]

            # Compare the last octet
            if last_octet == my_srn_number:
                return destination_ip

    return None


def get_my_srn_number():
    '''
    Uses ifconfig and tr0 to discover the srn number of itself (+100). This is
    used for communication using IP addresses.
    '''

    shell_command = "(ifconfig tr0 | grep inet | head -n 1 | awk '{print $2}' | cut -d '.' -f 3)"
    return check_output(shell_command, shell=True).decode().replace('\n', '')

def main():
    last_update_time = 0
    update_time_period = 1
    routing_table = get_routing_table()
    srn_num = get_my_srn_number()
    my_ip = get_my_internal_ip_address(routing_table, srn_num)

    port_num = '441'

    cmd = 'nc.traditional -ul -p {} {} -e /root/radio-api/node_poll.py'.format(
            port_num, my_ip)
    p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE)

    while True:
        if time.time() - last_update_time > update_time_period:
            # Update routing paramters if they changed
            routing_table = get_routing_table()
            srn_num = get_my_srn_number()
            my_ip = get_my_internal_ip_address(routing_table, srn_num)

            p.kill()
            cmd = 'nc.traditional -ul -p {} {} -e /root/radio-api/node_poll.py'.format(
                    port_num, my_ip)
            p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE)
            last_update_time = time.time()

if __name__ == '__main__':
    main()
