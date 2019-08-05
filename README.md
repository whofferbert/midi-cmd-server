# midi-cmd-server

midi_cmd_server.py

A midi listening device to execute pre-programmed commands based on MIDI control change messages.

```python
import time
import mido
import os
import subprocess
import re
```

Also requires the 'amidithru' command

The script creates a virtual midi device (MidiCmdServer, name adjustable in script), and listens to it for incoming midi control change (and note!) messages.

In the script, you can add control change identifiers, values, and the desired command to run, along with an optional uptime restriction.
You will find this section around line 44 or so:
```python
# set up midi commands here
# midi_cc_cmd( cc, cc_val, command, optional uptime seconds restriction) 
midi_cc_cmd(64, 127, "echo '64 on' >> /tmp/test", 120)
# this would be the shutdown server functionality here
#midi_cc_cmd(64, 127, "init 0", 120)
midi_cc_cmd(64, 0,   "echo '64 off' >> /tmp/test")
```

The script was recently updated to also handle commands triggered from midi notes. The section to edit them is just below the midi_cc_cmd parts.

Generally, add an entry to your crontab to call the script on startup:
(Make sure you set your path properly)

```bash
@reboot /usr/bin/sudo /path/to/midi_cmd_server.py &
```

Note about sudo
---------------

This script requires root to run, so you need to call it with sudo, without a password, or save the startup under the root crontab without the need for sudo.

To have this work on boot with sudo, you must not have sudo require a password to work.

You can achieve this by adding a new file and rule to your sudoers config. with visudo (username modep in examples):

```bash
sudo visudo -f /etc/sudoers.d/modep
```

Once in visudo, write the sudoers rule to allow your user to run sudo without a password:

```bash
modep ALL = (ALL:ALL) NOPASSWD: ALL
```

After that, you can log out and back in or reboot, and then be able to run sudo things without a password.
