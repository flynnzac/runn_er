# Copyright 2024 Zach Flynn

# Redistribution and use in source and binary forms, with or without modification, are permitted provided that the following conditions are met:

# 1. Redistributions of source code must retain the above copyright notice, this list of conditions and the following disclaimer.

# 2. Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the following disclaimer in the documentation and/or other materials provided with the distribution.

# 3. Neither the name of the copyright holder nor the names of its contributors may be used to endorse or promote products derived from this software without specific prior written permission.

# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS “AS IS” AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

import os
from runn_er.config import MEMOER_HOME

def set_status(result_id, status):
    with open(os.path.join(MEMOER_HOME,
                           "results",
                           str(result_id) + "_status.txt"), "w") as f:
        f.write(status)

        
def load_result(result_id):

    result = {}
    path = os.path.join(MEMOER_HOME,
                        "results", result_id + "function.json")
    path_check = os.path.join(MEMOER_HOME,
                              "results", result_id + "_finished.txt")
    path_given = os.path.join(MEMOER_HOME,
                              "results", result_id + "given.json")
    path_conclude = os.path.join(MEMOER_HOME,
                                 "results", result_id + "conclude.json")

    if os.path.isfile(path_check):
        with open(path, "r") as f:
            text = f.read()
        result = {
            "status": "success",
            "data": text
        }
    else:
        result = {
            "status": "not_ready",
            "data": "Result not ready."
        }
        return result

    if os.path.isfile(path_given):
        with open(path_given, "r") as f:
            text = f.read()
        result["given"] = text

    if os.path.isfile(path_conclude):
        with open(path_conclude, "r") as f:
            text = f.read()

        result["conclude"] = text

    return result

    
