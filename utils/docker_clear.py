'''stop and remove all docker containers'''

import os

os.system("docker ps -aq | xargs docker stop | xargs docker rm")
