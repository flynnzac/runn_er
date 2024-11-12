# Copyright 2024 Zach Flynn

# Redistribution and use in source and binary forms, with or without modification, are permitted provided that the following conditions are met:

# 1. Redistributions of source code must retain the above copyright notice, this list of conditions and the following disclaimer.

# 2. Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the following disclaimer in the documentation and/or other materials provided with the distribution.

# 3. Neither the name of the copyright holder nor the names of its contributors may be used to endorse or promote products derived from this software without specific prior written permission.

# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS “AS IS” AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.


import threading
import queue
import runn_er.runner as runner
import runn_er.requirement as requirement
import logging
import os
from runn_er.config import MEMOER_HOME

class TaskQueue(threading.Thread):
    def __init__(self, queue):
        self.queue = queue
        threading.Thread.__init__(self)

    def run(self):
        while True:
            val = self.queue.get()
            if val is None:
                return

            method, args = val

            if args["reqs"] != "":
                requirement.install_requirements(args["reqs"])

            try:
                logger = logging.getLogger(args["result_id"])
                log_path = os.path.join(
                    MEMOER_HOME,
                    "logs",
                    args["result_id"] + ".log"
                )
                logger.addHandler(
                    logging.FileHandler(log_path, encoding="utf-8")
                )
            except:
                print("Creating logger failed")
                logger = None

            try:
                requirement.reinstall_requirements(logger)
                del args["reqs"]
                runner.create_memo(method, args)
            except Exception as e:
                print(str(e))

class TaskQueues:
  def __init__(self, n_threads):
    self.tasks = [ TaskQueue(queue.Queue())
                   for x in range(0, n_threads) ]
    self.cur_thread = 0
    self.n_threads = n_threads
    
  def put(self, obj):
    task = self.tasks[self.cur_thread]
    task.queue.put(obj)
    self.cur_thread = (self.cur_thread+1) % self.n_threads

  def start(self):
    for task in self.tasks:
      task.start()
  
