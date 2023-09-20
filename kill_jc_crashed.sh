#!/usr/bin/env sh

KILLSWITCH="off"
SLEEPTIME=5

echo $$ > /tmp/kill_jc_crashed.pid

while :
do
    TOPPROCESS=$(top -b -n 1 | sed 1,6d | sed -n 2p)
    TOPPID=$(echo $TOPPROCESS | awk '{print $1}')
    TOPPROCESSNAME=$(echo $TOPPROCESS | awk '{print $12}')
    TOPCPU=$(echo $TOPPROCESS | awk '{print $9}' | cut -d"," -f1)
    echo "$TOPPROCESSNAME (pid=$TOPPID): $TOPCPU %. Killswitch=$KILLSWITCH"

    if [ $TOPCPU -gt 95 ] && [ $TOPPROCESSNAME == "juliacl+" ] ; then
        echo "-> Top process is a julia process"
        if [ $KILLSWITCH == "off" ] ; then
            echo "-> Setting killswitch to 'on'"
            KILLSWITCH="on"
        elif [ $KILLSWITCH == "on" ] ; then
            echo "-> killswitch is 'on', killing the process!"
            kill -9 $TOPPID
        fi
    else
        echo "Nothing to report"
        KILLSWITCH="off"
    fi

    sleep $SLEEPTIME
done

# https://serverfault.com/questions/97541/kill-process-with-high-cpu-usage-after-x-time

# ## Note: will kill the top-most process if the $CPU_LOAD is greater than the $CPU_THRESHOLD.
# echo
# echo checking for run-away process ...

# CPU_LOAD=$(uptime | cut -d"," -f4 | cut -d":" -f2 | cut -d" " -f2 | sed -e "s/\.//g")
# CPU_THRESHOLD=300
# PROCESS=$(ps aux r)
# TOPPROCESS=$(ps -eo pid -eo pcpu -eo command | sort -k 2 -r | grep -v PID | head -n 1)

# if [ $CPU_LOAD -gt $CPU_THRESHOLD ] ; then
#   # kill -9 $(ps -eo pid | sort -k 1 -r | grep -v PID | head -n 1) #original
#   # kill -9 $(ps -eo pcpu | sort -k 1 -r | grep -v %CPU | head -n 1)
#   kill -9 $TOPPROCESS
#   echo system overloading!
#   echo Top-most process killed $TOPPROCESS
#   echo load average is at $CPU_LOAD
#   echo
#   echo Active processes...
#   ps aux r

#   # send an email using mail
#   SUBJECT="Runaway Process Report at Marysol"
#   # Email To ?
#   EMAIL="myemail@somewhere.org"
#   # Email text/message
#   EMAILMESSAGE="/tmp/emailmessage.txt"
#   echo "System overloading, possible runaway process."> $EMAILMESSAGE
#   echo "Top-most process killed $TOPPROCESS" >>$EMAILMESSAGE
#   echo "Load average was at $CPU_LOAD" >>$EMAILMESSAGE
#   echo "Active processes..." >>$EMAILMESSAGE
#   echo "$PROCESS" >>$EMAILMESSAGE
#   mail -s "$SUBJECT" "$EMAIL" < $EMAILMESSAGE

# else
#  echo
#  echo no run-aways.
#  echo load average is at $CPU_LOAD
#  echo
#  echo Active processes...
#  ps aux r
# fi
# exit 0
