 #!/bin/bash

sudo -u sawtooth sawtooth-validator -vv &
sudo -u sawtooth settings-tp -vv &
sudo -u sawtooth intkey-tp-python -C tcp://127.0.0.1:4004 -v & 
sudo -u sawtooth xo-tp-python -C tcp://127.0.0.1:4004 -v &
