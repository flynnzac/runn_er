# Copyright 2024 Zach Flynn

# Redistribution and use in source and binary forms, with or without modification, are permitted provided that the following conditions are met:

# 1. Redistributions of source code must retain the above copyright notice, this list of conditions and the following disclaimer.

# 2. Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the following disclaimer in the documentation and/or other materials provided with the distribution.

# 3. Neither the name of the copyright holder nor the names of its contributors may be used to endorse or promote products derived from this software without specific prior written permission.

# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS “AS IS” AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.


import base64
import os
import subprocess
from runn_er.config import MEMOER_HOME

requirement_path = os.path.join(
    MEMOER_HOME,
    "py/"
    "requirements.txt"
)

def install_requirements(reqs):
    reqs_text = base64.b64decode(reqs.encode('utf-8'))
    with open(requirement_path, "wb") as f:
        f.write(reqs_text)

def reinstall_requirements(logger):
    output = subprocess.run(
        ["python3", "-m", "pip", "install", "-r",
         requirement_path, "--break-system-packages"],
        capture_output=True
    )
    if logger is not None:
        stdout = output.stdout.decode("utf-8")
        stderr = output.stderr.decode("utf-8")

        logger.error("REQUIREMENTS INSTALL:")
        logger.error("STDOUT:")
        logger.error(stdout)
        logger.error("STDERR:")
        logger.error(stderr)

    
