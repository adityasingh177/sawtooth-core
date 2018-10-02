 #!/bin/bash

systemctl start sawtooth-validator.service
systemctl start systemctl status sawtooth-rest-api.service
systemctl status sawtooth-settings-tp.service
systemctl status sawtooth-xo-tp-python.service
systemctl status sawtooth-intkey-tp-python.service