#!/bin/bash

python3 src/main.py --team teamA --x 10 --y 10 --rotation 10 &
PID1=$!

sleep 1
python3 src/main.py --team teamA --x 7 --y 10 --rotation 20 &
PID2=$!

echo "Нажмите Enter для завершения"
read

kill $PID1 $PID2 2>/dev/null
