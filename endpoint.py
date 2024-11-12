# Copyright 2024 Zach Flynn

# Redistribution and use in source and binary forms, with or without modification, are permitted provided that the following conditions are met:

# 1. Redistributions of source code must retain the above copyright notice, this list of conditions and the following disclaimer.

# 2. Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the following disclaimer in the documentation and/or other materials provided with the distribution.

# 3. Neither the name of the copyright holder nor the names of its contributors may be used to endorse or promote products derived from this software without specific prior written permission.

# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS “AS IS” AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.


import os
import uuid
import bcrypt
from runn_er.memo import set_status
from runn_er.config import MEMOER_HOME

def check_arg(args, req, resp):
    body = req.get_media()
    for arg in args:
        if arg not in body:
            resp.media = {
                "status": "error",
                "data": "missing '{}' argument.".format(arg)
            }
            return False
        
    return True

def check_api(conn, req):
    body = req.get_media()
    if "api" not in body:
        return False

    if "user_id" not in body:
        return False
    
    cur = conn.cursor()
    check_sql = ("select api, can_run, can_read_result "
                 "from keys WHERE user_id=%s")
    cur.execute(check_sql, (body["user_id"],))
    results = cur.fetchone()
    cur.close()
    if results is None:
        return False
    else:
        api, can_run, can_read_result = results
        if not bcrypt.checkpw(body["api"].encode("utf-8"), api.tobytes()):
            return False
        else:
            return results


class HealthEndpoint:
    def __init__(self, conn):
        self.conn = conn
        
    def on_post(self, req, resp):
        key_check = check_api(self.conn, req)

        if not key_check:
            resp.media = { "status": "error",
                           "data": "invalid key." }
            return
        elif not key_check[2]:
            resp.media = { "status": "error",
                           "data": "invalid permissions." }
            return

        resp.media = { "status": "success",
                       "data": "can connect."}
    
class StatusEndpoint:
    def __init__(self, conn):
        self.conn = conn
        
    def on_post(self, req, resp):
        key_check = check_api(self.conn, req)
        if not key_check:
            resp.media = { "status": "error",
                           "data": "invalid key." }
            return
        elif not key_check[2]:
            resp.media = { "status": "error",
                           "data": "invalid permissions." }
            return

        if not check_arg(["result_id"], req, resp):
            return

        body = req.get_media()

        try:
            result_id = str(uuid.UUID(body["result_id"]))
        except ValueError:
            resp.media = {
                "status": "error",
                "data": "invalid result_id."
            }
            return 
        

        status_file = os.path.join(MEMOER_HOME,
                                   "results/",
                                   result_id + "_status.txt")
        
        if os.path.exists(status_file):
            with open(status_file, "r") as f:
                status = f.read()

            resp.media = {
                "status" : "success",
                "data": status
            }
        else:
            resp.media = {
                "status": "error",
                "data": "invalid result_id."
            }

class RunEndpoint:
    def __init__(self, tq, conn):
        self.tq = tq
        self.conn = conn

    def on_post(self, req, resp):
        body = req.get_media()
        key_check = check_api(self.conn, req)

        if not key_check:
            resp.media = { "status": "error",
                           "data": "invalid key." }
            return
        elif not key_check[1]:
            resp.media = { "status": "error",
                           "data": "invalid permissions." }
            return
        
        if not check_arg(["topic", "args", "arg_display"], req, resp):
            return

        if "code" not in body["topic"]:
            resp.media = { "status": "error",
                           "data": "Missing 'code' in topic." }
            return
        
        if "function" not in body["topic"]:
            resp.media = { "status": "error",
                           "data": "Missing 'function' in topic." }
            return
        
        args = body["args"]
        result_id = uuid.uuid1()
        method = ["run_product"]

        if body["topic"]["given"] != "":
            method.append("given")

        if body["topic"]["conclude"] != "":
            method.append("conclude")

        set_status(result_id, "queued")
        self.tq.put((method,
                {
                    "topic": body["topic"],
                    "args": args,
                    "data": body["data"],
                    "reqs": body["requirement"],
                    "arg_display": body["arg_display"],
                    "result_id": str(result_id),
                }))

        resp.media = {
            "status": "success",
            "data": str(result_id)
        }
        

class ResultEndpoint:
    def __init__(self, conn):
        self.conn = conn

    def on_post(self, req, resp):
        body = req.get_media()

        key_check = check_api(self.conn, req)

        if not key_check:
            resp.media = { "status": "error",
                           "data": "invalid key." }
            return
        elif not key_check[2]:
            resp.media = { "status": "error",
                           "data": "invalid permissions." }
            return

        if not check_arg(["result_id"], req, resp):
            return

        try:
            result_id = str(uuid.UUID(body["result_id"]))
        except ValueError:
            resp.media = {
                "status": "error",
                "data": "invalid result_id."
            }
            return 
        
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
            resp.media = {
                "status": "success",
                "data": text
            }
        else:
            resp.media = {
                "status": "not_ready",
                "data": "Result not ready."
            }
            return

        if os.path.isfile(path_given):
            with open(path_given, "r") as f:
                text = f.read()
            resp.media["given"] = text

        if os.path.isfile(path_conclude):
            with open(path_conclude, "r") as f:
                text = f.read()

            resp.media["conclude"] = text
                
        
        
        
