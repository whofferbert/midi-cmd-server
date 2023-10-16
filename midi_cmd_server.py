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
import subprocess
import re

cc_cmds = dict()
note_cmds = dict()

def midi_cc_cmd(cc, val, cmd, uptime = 0):
  global cc_cmds
  if cc not in cc_cmds:
    cc_cmds[cc] = {}
  cc_cmds[cc][val] = {}
  cc_cmds[cc][val]["cmd"] = cmd
  cc_cmds[cc][val]["uptime"] = uptime

def midi_note_cmd(note, vel, cmd, uptime = 0):
  global note_cmds
  if note not in note_cmds:
    note_cmds[note] = {}
  note_cmds[note]["velocity"] = vel
  note_cmds[note]["cmd"] = cmd
  note_cmds[note]["uptime"] = uptime
  note_cmds[note]["lastTriggered"] = 0;

#
#
# Script setup
#

# midi device naming; avoid spaces
name = "MidiCmdServer2"

# set up midi cc commands here
# midi_cmd ( cc, cc_val, command, optional uptime seconds restriction )
midi_cc_cmd(64, 127, "echo '64 on' >> /tmp/test", 120)
midi_cc_cmd(64, 0,   "echo '64 off' >> /tmp/test")
# this would be the shutdown server functionality here
#midi_cmd(64, 127, "init 0", 120)

# midi note cmd for switching to a pedalboard
# example modep-ctrl.py requires newest modep-btn-scripts: 
# https://github.com/BlokasLabs/modep-btn-scripts
#midi_note_cmd(note, min velocity, "cmd", optional min uptime secs)
#midi_note_cmd(64, 64, "/usr/local/modep/modep-btn-scripts/modep-ctrl.py load-board DEFAULT")
midi_note_cmd(64, 64, "echo 'this was midi note 64 above velocity 64' >> /tmp/midinote")

# the minimum number of seconds that must pass before
# a note on can retrigger it's command. May need to
# increase this if you have notes that ring out, or shorten
# it if you need commands to retrigger very quickly
note_cmd_retrigger_delay = .5

#
# Logic below
#

# set up backend
mido.set_backend('mido.backends.rtmidi')

# system command to set up the midi thru port
# TODO would be nice to do this in python, but
# rtmidi has issues seeing ports it has created
#os.system(runCmd)
amidiProc = subprocess.Popen(['amidithru', name])
#print("launched amidithru with pid %s" % amidiProc.pid)

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
  time.sleep(.01)
  for msg in inport:
    if msg.type == "control_change":
      if msg.control in cc_cmds:
        if msg.value in cc_cmds[msg.control]:
          # apped " &" to the end of commands, to run them in background
          # and immediately get back to the script
          myCmd = cc_cmds[msg.control][msg.value]["cmd"] + " &"
          upCheck = cc_cmds[msg.control][msg.value]["uptime"]
          if upCheck > 0:
            if uptime() > upCheck:
              os.system(myCmd)
          else:
            os.system(myCmd)
    if msg.type == "note_on":
      if msg.note in note_cmds:
        if msg.velocity > note_cmds[msg.note]["velocity"]:
          # do not trigger too quickly on notes
          if note_cmds[msg.note]["lastTriggered"] + note_cmd_retrigger_delay < uptime():
            note_cmds[msg.note]["lastTriggered"] = uptime()
            # apped " &" to the end of commands, to run them in background
            # and immediately get back to the script
            myCmd = note_cmds[msg.note]["cmd"] + " &"
            upCheck = note_cmds[msg.note]["uptime"]
            if upCheck > 0:
              if uptime() > upCheck:
                os.system(myCmd)
            else:
              os.system(myCmd)
