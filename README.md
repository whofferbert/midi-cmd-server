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

In the script, you can fill _ with control change identifiers, values, and the desired command to run.

Generally, add an entry to your crontab to call the script on startup:
(Make sure you set your path properly)

```bash
@reboot /usr/bin/sudo /path/to/midi_cmd_server.py &
```
