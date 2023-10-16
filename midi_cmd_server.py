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

cmds = dict()

def midi_cc_cmd(chan, cc, val, cmd, uptime = 0):
  key = "control_change-{0}-{1}-{2}".format( chan, cc, val )
  cmds[ key ] = {
    'cmd': cmd + ' &',
    'uptime': uptime,
    'lastTriggered': 0
  }

def midi_note_cmd(chan, note, vel, cmd, uptime = 0):
  key = "note_on-{0}-{1}".format( chan, note )
  cmds[ key ] = {
    'velocity': vel,
    'cmd': cmd + ' &',
    'uptime': uptime,
    'lastTriggered': 0
  }


#
# Script setup
#

# midi device naming; avoid spaces
name = "MidiCmdServer2"

# set up midi cc commands here
# midi_cmd ( channel, cc, cc_val, command, optional uptime seconds restriction )
#midi_cc_cmd(0, 64, 127, "echo '64 on' >> /tmp/test", 120)
#midi_cc_cmd(0, 64, 0,   "echo '64 off' >> /tmp/test")
# this would be the shutdown server functionality here
#midi_cmd(64, 127, "init 0", 120)

# midi note cmd for switching to a pedalboard
# example modep-ctrl.py requires newest modep-btn-scripts: 
# https://github.com/BlokasLabs/modep-btn-scripts
#midi_note_cmd(channel, note, min velocity, "cmd", optional min uptime secs)
#midi_note_cmd(64, 64, "/usr/local/modep/modep-btn-scripts/modep-ctrl.py load-board DEFAULT")
#midi_note_cmd(0, 64, 64, "echo 'this was midi note 64 above velocity 64' >> /tmp/midinote")

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


def runcmd( cmd ):
  up = uptime()
  if cmd['uptime'] > 0 and up < cmd['uptime']: return
  if cmd['lastTriggered'] + note_cmd_retrigger_delay < up:
    os.system( cmd['cmd'] )
    cmd['lastTriggered'] = up


# keep running and watch for midi cc
for msg in inport:
  cmd = None
  key = None

  if msg.type == "control_change":
    key = "{0}-{1}-{2}-{3}".format( msg.type, msg.channel, msg.control, msg.value )
    cmd = cmds.get( key )
    if cmd is None: continue
    runcmd( cmd )
  if msg.type == "note_on":
    key = "{0}-{1}-{2}".format( msg.type, msg.channel, msg.note )
    cmd = cmds.get( key )
    if cmd is None: continue
    if msg.velocity >= cmd["velocity"]: runcmd( cmd )

