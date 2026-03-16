#!/bin/bash

# Start Passer (игрок, дающий голевой пас)
python3 src/main.py --team teamA --role passer --x -15 --y 0 &
PASS_PID=$!

# Start Scorer (игрок, забивающий гол)
python3 src/main.py --team teamA --role scorer --x -15 --y 10 &
SCORE_PID=$!

# Start Goalie Defender для teamB (вратарь у нижней штанги)
# Согласно заданию 4.2: защитники стоят у ворот для предотвращения offside
# Вратари могут использовать move во время игры
python3 src/main_defender.py --team teamB --x -48 --y -5 &
GOALIE_PID=$!

# Start Static Defender для teamB (обычный игрок у верхней штанги)
# Использует dash 0 для удержания позиции
python3 src/main_defender.py --team teamB --x -48 --y 5 &
DEFENDER_PID=$!

echo "Agents started. Press Ctrl+C to stop."
echo "  - Passer (teamA): (-15, 0)"
echo "  - Scorer (teamA): (-15, 10)"
echo "  - Goalie Defender (teamB): (-48,  5) у нижней штанги"
echo "  - Static Defender (teamB): (-48, -5) у верхней штанги"

trap "kill $PASS_PID $SCORE_PID $GOALIE_PID $DEFENDER_PID; exit" INT
wait
