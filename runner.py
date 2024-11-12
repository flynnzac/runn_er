# Copyright 2024 Zach Flynn

# Redistribution and use in source and binary forms, with or without modification, are permitted provided that the following conditions are met:

# 1. Redistributions of source code must retain the above copyright notice, this list of conditions and the following disclaimer.

# 2. Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the following disclaimer in the documentation and/or other materials provided with the distribution.

# 3. Neither the name of the copyright holder nor the names of its contributors may be used to endorse or promote products derived from this software without specific prior written permission.

# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS “AS IS” AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.


import os
import sys
import shutil
import subprocess
import pandas as pd
import datetime
import json
import uuid
import base64
from runn_er.topic import (
    convert_text_to_object,
    make_main_script,
    fetch_data
)
from runn_er.memo import set_status
from runn_er.config import MEMOER_HOME

def create_memo(method, args):
    set_status(args["result_id"], "running")
    retcodes = []
    if "given" in method:
        given, retcode_given = run_product(subtopic="given", **args)
        retcodes.append(retcode_given)

    output, retcode_output = run_product(subtopic="function", **args)
    retcodes.append(retcode_output)

    if ("conclude" in method) and (retcode_output == 0):
        conclude, retcode_conclude = run_product(
            subtopic="conclude",
            result_id=args["result_id"],
            topic=args["topic"],
            args={"output": output},
            arg_display={}
        )
        retcodes.append(retcode_conclude)

    error = any(retcodes)
    with open(os.path.join(MEMOER_HOME, "results/",
                           f"{args['result_id']}_finished.txt"), "w") as f:
        f.write("done")

    set_status(args["result_id"], "done" if not error else "error")
    
def deploy_product(topic, path, args, subtopic):
    with open(os.path.join(path, 'library.py'), 'wb') as f:
        f.write(base64.b64decode(topic["code"].encode('utf-8')))

    main_script = make_main_script(os.path.join(path, "library.py"),
                                   topic[subtopic])
    
    with open(os.path.join(path, 'main.py'), 'w') as f:
        f.write(main_script)
    with open(os.path.join(path, "args.json"), "w") as f:
        f.write(json.dumps(args))

def translate_output(obj):
    output = None
    if isinstance(obj, pd.DataFrame):
        output = obj
    elif isinstance(obj, list):
        output = pd.DataFrame({"Value": obj})
    elif isinstance(obj, dict):
        output = pd.DataFrame({"Parameter": list(obj.keys()),
                               "Value": list(obj.values())})
    else:
        output = pd.DataFrame({"Value": [obj]})

    return output
    
def dump_output(output, args, arg_display, result_id, subtopic):
    # re-key args for display
    args_out = args.copy()
    for arg in args.keys():
        if arg in arg_display:
            args_out[arg_display[arg]] = args_out.pop(arg)

    output.fillna(value='', inplace=True)
    output_dict = {
        "result": output.to_dict('split'),
        "args": args_out,
        "runtime": str(datetime.datetime.now().isoformat(sep=" ", timespec="seconds"))
    }
    
    output_string = json.dumps(output_dict)
    with open(os.path.join(MEMOER_HOME, "results/", f"{result_id}{subtopic}.json"), "w") as f:
        f.write(output_string)

def run_product(topic, result_id, args, arg_display, data=None, subtopic=""):
    id = uuid.uuid1()
    path = os.path.join(MEMOER_HOME, "env/", str(id) + "/")
    os.mkdir(path)

    fj_profile = os.path.join(
        MEMOER_HOME,
        "runn_er/runn_er.profile"
    )
    obj = None
    returncode = 1
    try:
        if data is not None:
            fetch_data(path, data)
    except Exception as e:
        obj = pd.DataFrame({"Data Fetch Error": [str(e)]})
        output = translate_output(obj)
        dump_output(output, args, arg_display, result_id, subtopic)
        return obj, 1
    
    try:
        deploy_product(topic, path, args, subtopic)
        proc = subprocess.run(["firejail",
                               f"--profile={fj_profile}",
                               "python3",
                               os.path.join(path, "main.py")],
                              cwd=path,
                              timeout=60*60*24,
                              capture_output=True)

        result = proc.stdout.decode("utf-8")
        returncode = proc.returncode
        if proc.returncode != 0:
            obj = proc.stderr.decode("utf-8")
        else:
            obj = convert_text_to_object(result)
    except Exception as e:
        obj = pd.DataFrame({
            "Error":
            ["Internal error. Either try again or reach out to support at zach@memoer.io."]
        })
        returncode = 1
    finally:
        shutil.rmtree(path)

    output = translate_output(obj)
    dump_output(output, args, arg_display, result_id, subtopic)

    return obj, returncode

