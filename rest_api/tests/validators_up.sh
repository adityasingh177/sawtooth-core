 #!/bin/bash

sudo -u sawtooth systemctl start sawtooth-validator.service
sudo -u sawtooth systemctl start systemctl status sawtooth-rest-api.service
sudo -u sawtooth systemctl status sawtooth-settings-tp.service
sudo -u sawtooth systemctl status sawtooth-xo-tp-python.service
sudo -u sawtooth systemctl status sawtooth-intkey-tp-python.service