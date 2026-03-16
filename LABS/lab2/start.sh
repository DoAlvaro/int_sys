#!/bin/bash
python3 src/main.py --team teamA --x -15 --y 0 &
echo "Нажмите Enter для завершения"
read
kill %1 2>/dev/null
