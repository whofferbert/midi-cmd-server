#!/usr/bin/python3
# by William Hofferbert
# Midi Command Server
# creates a virtual midi device via amidithru,
# then listens for a control change message
# on that device, running the defined commands
# via os.system when it receives the proper
# midi CC and value.

import time
import mido
import os
import re

cmds = dict()

def midi_cmd(cc, val, cmd, uptime = 0):
  global cmds
  if cc not in cmds:
    cmds[cc] = {}
  cmds[cc][val] = {}
  cmds[cc][val]["cmd"] = cmd
  cmds[cc][val]["uptime"] = uptime

#
# Script setup
#

# midi device naming
name = "MidiCmdServer"

# set up midi commands here
# midi_cmd ( cc, cc_val, command, optional uptime seconds restriction )
midi_cmd(64, 127, "echo '64 on' >> /tmp/test", 120)
# this would be the shutdown server functionality here
#midi_cmd(64, 127, "init 0", 120)
midi_cmd(64, 0,   "echo '64 off' >> /tmp/test")

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
          # apped " &" to the end of commands, to run them in background
          # and immediately get back to the script
          myCmd = cmds[msg.control][msg.value]["cmd"] + " &"
          upCheck = cmds[msg.control][msg.value]["uptime"]
          if upCheck > 0:
            if uptime() > upCheck:
              os.system(myCmd)
          else:
            os.system(myCmd)
