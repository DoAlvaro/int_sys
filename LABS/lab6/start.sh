#!/bin/bash
# Один игрок (forward_center). Для полной команды: python3 src/start_team.py --team teamA --side l
# Для матча: python3 src/start_match.py (из каталога src)
python3 src/main.py --team teamA --role forward_center --side l &
echo "Нажмите Enter для завершения"
read
kill %1 2>/dev/null
