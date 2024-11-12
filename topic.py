# Copyright 2024 Zach Flynn

# Redistribution and use in source and binary forms, with or without modification, are permitted provided that the following conditions are met:

# 1. Redistributions of source code must retain the above copyright notice, this list of conditions and the following disclaimer.

# 2. Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the following disclaimer in the documentation and/or other materials provided with the distribution.

# 3. Neither the name of the copyright holder nor the names of its contributors may be used to endorse or promote products derived from this software without specific prior written permission.

# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS “AS IS” AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.



import pickle
import base64
import gnupg
import requests
import sqlalchemy
import os
import pandas as pd
from runn_er.config import MEMOER_HOME
import runn_er.credentials as creds

gpg = gnupg.GPG(gnupghome=os.path.join(MEMOER_HOME, ".gnupg"))

def convert_text_to_object(txt):
    b64 = txt.encode('ascii')
    byte = base64.b64decode(b64)
    return pickle.loads(byte)

def convert_object_to_text(obj):
    byte = pickle.dumps(obj)
    b64 = base64.b64encode(byte)
    txt = b64.decode('ascii')
    return txt

def make_main_script(path, function):
    result = """
import sys
import os
import io
import pickle
import base64    
import json
import importlib.util, sys

def convert_object_to_text(obj):
    byte = pickle.dumps(obj)
    b64 = base64.b64encode(byte)
    txt = b64.decode('ascii')

    return txt
    
spec = importlib.util.spec_from_file_location("module.name",
        os.path.join("{}")
    )
mod = importlib.util.module_from_spec(spec)
sys.modules["module.name"] = mod
spec.loader.exec_module(mod)

__analysis_func = getattr(mod, "{}")

with open('args.json', 'r') as __analysis_args_json:
    __analysis_args = json.loads(__analysis_args_json.read())

save_stdout = sys.stdout
sys.stdout = io.StringIO()
__analysis_output = __analysis_func(**__analysis_args)
__analysis_serial_output = convert_object_to_text(__analysis_output)
sys.stdout = save_stdout
print(__analysis_serial_output)
""".format(path, function)
    return result

def fetch_via_sql(spec):
    sql_url = str(gpg.decrypt(spec["sql_url"],
                          passphrase=creds.RUNN_ER_GPG_PASS))

    if spec["db_type"] == "":
        url = sql_url
    else:
        url = spec["db_type"] + "://" + sql_url
    
    engine = sqlalchemy.create_engine(url)

    query = str(gpg.decrypt(spec["command"],
                            passphrase=creds.RUNN_ER_GPG_PASS))
    
    query = base64.b64decode(query).decode("utf-8")
    df = pd.read_sql_query(query, con=engine)

    return df

def fetch_via_post(spec):
    url = spec["url"]
    headers = {"Content-Type": spec["content_type"]}
    body = str(gpg.decrypt(spec["command"],
                           passphrase=creds.RUNN_ER_GPG_PASS))

    body = base64.b64decode(body).decode("utf-8")
    resp = requests.post(url, data=body, headers=headers)
    return resp.text

def fetch_via_get(spec):
    url = spec["url"]
    resp = requests.get(url)
    return resp.text

def fetch_data(path, data_specs):
    for spec in data_specs:
        output_file = os.path.join(path, str(spec["id"]) + ".data")
        if os.path.isfile(output_file):
            continue
        if spec["kind"] == "SQL":
            result = fetch_via_sql(spec)
            result.to_csv(output_file, index=False)
        elif spec["kind"] == "POST":
            result = fetch_via_post(spec)
            with open(output_file, "w") as f:
                f.write(result)
        elif spec["kind"] == "GET":
            result = fetch_via_get(spec)
            with open(output_file, "w") as f:
                f.write(result)
        
    
        
