# Copyright 2024 Zach Flynn

# Redistribution and use in source and binary forms, with or without modification, are permitted provided that the following conditions are met:

# 1. Redistributions of source code must retain the above copyright notice, this list of conditions and the following disclaimer.

# 2. Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the following disclaimer in the documentation and/or other materials provided with the distribution.

# 3. Neither the name of the copyright holder nor the names of its contributors may be used to endorse or promote products derived from this software without specific prior written permission.

# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS “AS IS” AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.


# Run this file from directory containing the runn_er directory

require 'gpgme'
require 'securerandom'
require 'readline'
require 'pg'
require 'open-uri'
require 'open3'

# Step 0. Make sure database doesn't exist.

db_user = Readline.readline("Database user: ", false)
db_password = Readline.readline("Database password: ", false)
memo_er_host = Readline.readline("Memo_er host (i.e. https://memoer.io): ", false)

con = PG::Connection.new user: db_user, password: db_password, dbname: "postgres"
res = con.exec "SELECT 1 FROM pg_database WHERE datname='runn_er'"
if not res.num_tuples.zero? and (res.getvalue(0,0) == "1")
  raise "Database runn_er exists. Please delete before continuing."
end
con.close


# Step 1. Create Runn_er GPG Key and import memoer.io key

ENV["GNUPGHOME"] = Dir.pwd + "/.gnupg"
Dir.mkdir(Dir.pwd + "/.gnupg")
File.chmod 0700, Dir.pwd + "/.gnupg"

runn_er_passphrase = SecureRandom.alphanumeric(20)

ctx = GPGME::Ctx.new :armor => true
ctx.generate_key(
  "<GnupgKeyParms format=\"internal\">
                Key-Type: RSA
                Key-Length: 3072
                Passphrase: #{runn_er_passphrase}
                Name-Real: Runn_er
</GnupgKeyParms>"
)

memoer_io_public_key = OpenURI::open_uri(File.join memo_er_host, "memo_er.asc").read

ctx.import_keys GPGME::Data.new(memoer_io_public_key)

key_text, status = Open3.capture2("gpg --show-keys", :stdin_data => memoer_io_public_key)
memo_er_fingerprint, status = Open3.capture2("sed -n '2 p'", :stdin_data => key_text)
memo_er_fingerprint.gsub!(/\s+/, "")

`echo "trusted-key #{memo_er_fingerprint}" >> #{Dir.pwd + "/.gnupg/gpg.conf"}`


# Step 2. Configure Runn_er

runn_er_creds = "
RUNN_ER_HOST = \"localhost\"
RUNN_ER_DB = \"runn_er\"
RUNN_ER_USER = \"#{db_user}\"
RUNN_ER_PASSWORD = \"#{db_password}\"
RUNN_ER_GPG_PASS = \"#{runn_er_passphrase}\"
"

runn_er_config = "
NUMBER_OF_QUEUES = 2
USE_ENCRYPTION = True
MEMOER_FINGERPRINT = \"#{memo_er_fingerprint}\"
MEMOER_HOME = \"#{Dir.pwd}\"
"

File.open("runn_er/credentials.py", "w") do |file|
  file.write(runn_er_creds)
end

File.open("runn_er/config.py", "w") do |file|
  file.write(runn_er_config)
end

# Step 3. Create database and environment

`echo "CREATE DATABASE runn_er;" | PGPASSWORD="#{db_password}" psql -U #{db_user} postgres`
`cat runn_er/sql/schema.sql | PGPASSWORD="#{db_password}" psql -U #{db_user} runn_er`
Dir.chdir("runn_er") do
  `python3 hash.py #{runn_er_passphrase}`
end

`sed -i 's@%MEMOER_HOME%@#{Dir.pwd}@g' runn_er/runn_er.profile`

Dir.mkdir(Dir.pwd + "/results")
Dir.mkdir(Dir.pwd + "/env")
Dir.mkdir(Dir.pwd + "/py")
Dir.mkdir(Dir.pwd + "/logs")

puts "Runn_er API Key: #{runn_er_passphrase}"
