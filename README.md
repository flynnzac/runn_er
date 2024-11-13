# Memo_er

Memo\_er (https://memoer.io) is a different way of thinking about self-serve data analysis. Instead of creating dashboards and graphs, Memo\_er writes automated memos. The key idea is that self-serve data analysis should be just like normal data analysis done by a data scientist. Normal data analysis does not and should not just produce a series of graphs and dashboards. It should produce a document with a clear explanation of assumptions and conclusions. Memo\_er automates this process so that anyone on the team can provide the inputs to power the analysis.

Data scientists can write Topics in Python and these get translated into Memo's by a Runn_er, which is the code contained in this repo.

# Runn_er

Runn\_er processes memos from Memo\_er. This repo includes a script to make it easy to get set up with a Runn\_er to use on memoer.io.

There is also a video walkthrough of how to do this step-by-step on a Debian AWS instance: https://www.youtube.com/watch?v=Nm_ikB9-eOg

To get started do the following on a Debian box (the AWS debian image is a clean way to do this). 

1. Clone the repo into an empty, non-HOME directory, i.e. don't clone it to the HOME/runn\_er directory, clone it to HOME/environment/runn\_er directory. 
2. `cd environment`. Run all commands from this folder.
3. For easiest setup, run `sudo bash runn_er/deploy/debian.sh`. Note that this will overwrite the 000-default.conf site for Apache.
4. Create a Postgres database user with a password (e.g. `CREATE USER runn_er WITH ENCRYPTED PASSWORD 'mypassword';`). Let this user create databases (`ALTER USER runn_er CREATEDB;`).
5. Configure Postgres to use scram-sha-256 authentication method for local database users by editing the configure (on Debian, in `/etc/postgresql/*/*/pg_hba.conf`. Then, restart postgres with `sudo systemctl restart postgresql.service`.
6. Run `ruby runn_er/install.rb`. Enter the database user and password and then it will set everything else up.
7. Start creating a Runn\_er on memoer.io: https://memoer.io/runn_ers/make and add your IP and put port 80.
8. Copy the API Key output by ruby runn_er/install.rb and paste it into the API Key field for the Runn\_er on memoer.io.
9. Run `GNUPGHOME=.gnupg gpg --export -a Runn_er` and copy the output to the "Public Key for Runn_er".
10. Create the Runn_er.
11. Run `python3 -m gunicorn runn_er.api` (usually, I put this in a `screen` session).
12. Go to https://memoer.io/runn_ers and click the "Test Connection" button. If it works, you're all set! If not, probably the issue is that your server isn't allowing connections on port 80.
