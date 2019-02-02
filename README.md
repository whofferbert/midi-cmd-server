# midi-cmd-server

midi_cmd_server.py

A midi listening device to execute pre-programmed commands based on MIDI control change messages.

```python
import time
import mido
import os
import re
```

Also requires 'amidithru'

The script creates a virtual midi device (MidiCmdServer), and listens to it for incoming midi control change messages.

In the script, you can add control change identifiers, values, and the desired command to run, along with an optional uptime restriction.
You will find this section around line 32 or so:
```python
# set up midi commands here
# midi_cmd( cc, cc_val, command, optional uptime seconds restriction) 
midi_cmd(64, 127, "echo '64 on' >> /tmp/test", 120)
# this would be the shutdown server functionality here
#midi_cmd(64, 127, "init 0", 120)
midi_cmd(64, 0,   "echo '64 off' >> /tmp/test")
```

Generally, add an entry to your crontab to call the script on startup:
(Make sure you set your path properly)

```bash
@reboot /usr/bin/sudo /path/to/midi_cmd_server.py &
```
