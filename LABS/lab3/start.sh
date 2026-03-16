#!/bin/bash

ACTIONS='[{"act": "flag", "fl": "frb"}, {"act": "kick", "fl": "b", "goal": "gr"}]'

python3 src/main.py --team teamA --x 0 --y 0 --actions "$ACTIONS" &
PID1=$!

sleep 1
python3 src/main.py --team teamA --x 3 --y 0 --actions "$ACTIONS" &
PID2=$!

sleep 1
python3 src/main.py --team teamA --x 0 --y 3 --actions "$ACTIONS" &
PID3=$!

sleep 1
python3 src/main.py --team teamB --x -45 --y 0 --goalie &
PID4=$!

echo "Нажмите Enter для завершения"
read

kill $PID1 $PID2 $PID3 $PID4 2>/dev/null
