import os
import re

import pfw.console
import pfw.shell



def install( ):
   result = pfw.shell.execute( "apt update", sudo = True, output = pfw.shell.eOutput.PTY )
   result = pfw.shell.execute( "apt install -y ca-certificates curl gnupg lsb-release", sudo = True, output = pfw.shell.eOutput.PTY )

   DOCKER_URL = "https://download.docker.com/linux/ubuntu"
   DOCKER_GPG_KEY_URL = f"{DOCKER_URL}/gpg"
   KEYRING_FILE = "/usr/share/keyrings/docker-archive-keyring.gpg"

   command = f"if [ ! -f {KEYRING_FILE} ]; then curl -fsSL {DOCKER_GPG_KEY_URL} | sudo -S gpg --dearmor -o {KEYRING_FILE}; fi"
   result = pfw.shell.execute( command, output = pfw.shell.eOutput.PTY )

   target_string = f"deb [arch=$(dpkg --print-architecture) signed-by={KEYRING_FILE}] {DOCKER_URL} $(lsb_release -cs) stable"
   command = "echo \"" + target_string + "\" | sudo -S tee /etc/apt/sources.list.d/docker.list > /dev/null"
   result = pfw.shell.execute( command, output = pfw.shell.eOutput.PTY )

   result = pfw.shell.execute( "apt update", sudo = True, output = pfw.shell.eOutput.PTY )
   result = pfw.shell.execute( "apt install -y docker-ce docker-ce-cli containerd.io", sudo = True, output = pfw.shell.eOutput.PTY )
   result = pfw.shell.execute( "groupadd docker", sudo = True, output = pfw.shell.eOutput.PTY )
   result = pfw.shell.execute( "usermod -aG docker ${USER}", sudo = True, output = pfw.shell.eOutput.PTY )
# def install

def prune( ):
   result = pfw.shell.execute( "docker system prune --all --volumes", output = pfw.shell.eOutput.PTY )

   return 0 == result["code"]
# def prune
