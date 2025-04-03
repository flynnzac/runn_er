# Writes a memo from command-line by taking in a base64-encoded json as a command-line argument
# Does NOT check for API Keys or permissions, etc

import sys
import base64
import json
import runn_er.background as bg
import uuid
from runn_er.config import MEMOER_HOME
import runn_er.memo as memo

call = json.loads(base64.b64decode(sys.argv[1]))
result_id = uuid.uuid1()
method = ["run_product"]

if call["topic"]["given"] != "":
    method.append("given")

if call["topic"]["conclude"] != "":
    method.append("conclude")


args = {
    "topic": call["topic"],
    "args": call["args"],
    "data": call["data"],
    "reqs": call["requirement"],
    "arg_display": call["arg_display"],
    "result_id": str(result_id)
}

bg.process(method, args)


