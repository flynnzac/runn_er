# This file is the firejail profile that will be applied to user code run by the Runn_er.
# Modify it as you'd like, depending on how much you trust code sent to your Runn_er.

caps.drop all
nonewprivs
seccomp
noroot
net none
blacklist %MEMOER_HOME%/runn_er
blacklist %MEMOER_HOME%/memo_er
blacklist %MEMOER_HOME%/results
blacklist %MEMOER_HOME%/logs
blacklist %MEMOER_HOME%/py
blacklist %MEMOER_HOME%/.gnupg
read-only %MEMOER_HOME%/lib
read-only %MEMOER_HOME%
read-only /tmp

