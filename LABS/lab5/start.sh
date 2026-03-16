#!/bin/bash

python3 src/main.py --team teamA --role attacker --x -20 --y -17 &
PID1=$!

sleep 1
python3 src/main.py --team teamA --role attacker --x -20 --y 17 &
PID2=$!

sleep 1
python3 src/main.py --team teamB --role defender --x -5 --y -5 &
PID3=$!

sleep 1
python3 src/main.py --team teamB --role defender --x -5 --y 5 &
PID4=$!

sleep 1
python3 src/main.py --team teamB --role goalie --x -50 --y 0 &
PID5=$!

echo "Нажмите Enter для завершения"
read

kill $PID1 $PID2 $PID3 $PID4 $PID5 2>/dev/null
