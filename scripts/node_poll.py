# Created for SC2
# Add a line in boot.sh saying:
# nc.traditional -ul -p 441 localhost -e /root/radio-api/node_poll.py &
# Relies on nc.traditional being installed

import sys
import time

def get_tap_stats(tap_name):
  '''
  Function which reads /proc/net/dev and expects a line
  with statistics for tap. Returns two numbers: Bytes received and transmitted
  from tap by parsing based on a special predefined linux format.
  '''
  with open('/proc/net/dev', 'r') as inFile:
    lines = inFile.readlines()

  colLine = lines[1]
  _, receiveCols, transmitCols = colLine.split('|')
  receiveCols = map(lambda a: "recv_"+a, receiveCols.split())
  transmitCols = map(lambda a: "trans_"+a, transmitCols.split())

  cols = receiveCols + transmitCols

  faces = {}
  for line in lines[2:]:
    if line.find(':') < 0: continue
    face, data = line.split(':')
    faceData = dict(zip(cols, data.split()))
    faces[face.lstrip().rstrip()] = faceData

  tap = faces[tap_name]
  return tap['recv_bytes'], tap['trans_bytes']

def check_and_respond(count, tap_name):
  '''
  Checks if the system has received the query character. If so, reads tap
  statistics and writes those to stdout in the format of:

  received_bytes transmitted_bytes
  '''
  line = sys.stdin.readline()
  if line and line.rstrip() == "?":
    count += 1
    #received, transmitted = get_tap_stats(tap_name)
    #sys.stdout.write(received + ' ' + transmitted + '\n')
    sys.stdout.write(str(count) + '\n')
    sys.stdout.flush()

  return count

def main():
  '''
  Periodically checks, and responds as necessary.
  '''
  count = 0
  tap_name = 'tr0'
  while True:
    count = check_and_respond(count, tap_name)
    time.sleep(0.5)

if __name__ == '__main__':
  main()

