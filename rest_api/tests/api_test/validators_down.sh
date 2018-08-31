 #!/bin/bash
 sudo kill -9  $(ps aux | grep 'sawtooth' | awk '{print $2}')
 echo "$(ps aux | grep 'sawtooth')"
