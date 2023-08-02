#!/usr/bin/env sh

# Configuration of DaemonConductor

# When the daemon starts, it pays attention to the following
# environmental variables:

# JULIA_DAEMON_SERVER (default: /run/user/$UID/julia-daemon.sock), the
# socket the client connects to.

# JULIA_DAEMON_WORKER_ARGS (default: --startup-file=no), arguments
# passed to the worker Julia processes (individual arguments are split
# on whitespace).

# JULIA_DAEMON_WORKER_MAXCLIENTS (default: 1), the maximum number of
# clients a worker may be attached to at once. Set to 0 to disable.

# JULIA_DAEMON_WORKER_EXECUTABLE (default: julia on PATH), the path to
# the Julia executable used by the workers.

# JULIA_DAEMON_WORKER_TTL (default: 7200, 2h), the number of seconds a
# worker should be kept alive for after the last client disconnects from
# it. This variable can be updated within the worker itself.

# Similarly, the client pays attention to JULIA_DAEMON_SERVER to make
# sure it connects to the right socket.

# export JULIA_DAEMON_SERVER=/run/user/1000/julia/
# export JULIA_DAEMON_WORKER_MAXCLIENTS=2
# export JULIA_DAEMON_WORKER_ARGS="--startup-file=no"


python sbi4abm/utils/job_script.py \
    --task MultiIndustryABM \
    --method maf_gru \
    --outloc results \
    --nsims 20x1 \
    --nw 3
