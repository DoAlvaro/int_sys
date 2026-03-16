#!/bin/bash

# teamA (side l)
python3 src/main.py --team teamA --role goalie --side l &
PID1=$!
sleep 1
python3 src/main.py --team teamA --role defender_center --side l &
PID2=$!
sleep 1
python3 src/main.py --team teamA --role forward_center --side l &
PID3=$!
sleep 1
python3 src/main.py --team teamA --role forward_top --side l &
PID4=$!

sleep 1
# teamB (side r)
python3 src/main.py --team teamB --role goalie --side r &
PID5=$!
sleep 1
python3 src/main.py --team teamB --role defender_center --side r &
PID6=$!
sleep 1
python3 src/main.py --team teamB --role forward_center --side r &
PID7=$!

echo "Lab6: teamA (l) — goalie, defender_center, forward_center, forward_top"
echo "      teamB (r) — goalie, defender_center, forward_center"
echo "Нажмите Enter для завершения"
read

kill $PID1 $PID2 $PID3 $PID4 $PID5 $PID6 $PID7 2>/dev/null
