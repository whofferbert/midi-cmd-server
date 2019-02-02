#!/usr/bin/python3
# by William Hofferbert
# Midi Shutdown Server
# creates a virtual midi device via amidithru,
# then listens for a control change message
# on that device, running a shutdown command
# via os.system when it gets that command.

import time
import mido
import os
import re

def midi_cmd(cc, val, cmd, uptime = 0):
  global cmds
  global cmd_num
  if cc not in cmds:
    cmds[cc] = {}
  cmds[cc][val] = {}
  cmds[cc][val]["cmd"] = cmd
  cmds[cc][val]["uptime"] = uptime
    
cmds = dict()
cmd_num = 0

#
# Script setup
#

# midi device naming
name = "MidiCmdServer"

# set up midi commands here
# cc, cc_val, command, optional uptime seconds restriction
midi_cmd(64, 127, "echo '64 on' >> /tmp/test", 120)
#midi_cmd(64, 127, "init 0", 120)
midi_cmd(64, 0,   "echo '64 off' >> /tmp/test")
midi_cmd(65, 30,  "echo 'other' >> /tmp/test")

#
# Logic below
#

# set up backend
mido.set_backend('mido.backends.rtmidi')

# system command to set up the midi thru port
# TODO would be nice to do this in python, but
# rtmidi has issues seeing ports it has created
runCmd = "amidithru '" + name + "' &"
os.system(runCmd)

# regex to match on rtmidi port name convention
nameRegex = "(" + name + ":" + name + "\s+\d+:\d+)"
matcher = re.compile(nameRegex)
newList = list(filter(matcher.match, mido.get_input_names()))
input_name = newList[0]

inport = mido.open_input(input_name)

def uptime():
  with open('/proc/uptime', 'r') as f:
    uptime_seconds = float(f.readline().split()[0])
    return uptime_seconds

# keep running and watch for midi cc
while True:
  time.sleep(.1)
  while inport.pending():
    msg = inport.receive()
    if msg.type == "control_change":
      if msg.control in cmds:
        if msg.value in cmds[msg.control]:
          myCmd = cmds[msg.control][msg.value]["cmd"] + " &"
          upcheck = cmds[msg.control][msg.value]["uptime"]
          if upcheck > 0:
            if uptime() > upcheck:
              os.system(myCmd)
          else:
            os.system(myCmd)
