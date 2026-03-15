#!/bin/bash
# Установка rcssserver + rcssmonitor на Linux по методичке (СтудИзба, раздел 1).
# Проверено на Ubuntu 20.04/22.04. Запуск: ./install_rcssserver_linux.sh

set -e
BUILD_DIR="${BUILD_DIR:-$HOME/rcss_build}"

echo "=== 1. Зависимости (сервер + монитор) ==="
if command -v apt-get &>/dev/null; then
  sudo apt-get update
  # Базовые зависимости для rcssserver (обязательно)
  sudo apt-get install -y build-essential automake libboost-all-dev flex bison \
    libxt-dev libxi-dev libxrender-dev libfontconfig1-dev \
    git curl
  # libfreetype: в новых дистрибутивах может быть libfreetype-dev вместо libfreetype6-dev
  sudo apt-get install -y libfreetype6-dev 2>/dev/null || sudo apt-get install -y libfreetype-dev
  # Монитор по методичке — нужен Qt4. В Ubuntu 22+ его нет в репозиториях, подключаем PPA.
  if apt-cache show libqt4-dev &>/dev/null; then
    sudo apt-get install -y libqt4-dev libaudio-dev qt4-dev-tools
  else
    echo "  Qt4 в репозиториях нет. Подключаем PPA для Qt4 (как в методичке)..."
    sudo apt-get install -y software-properties-common
    sudo add-apt-repository -y ppa:ubuntuhandbook1/ppa
    sudo apt-get update
    sudo apt-get install -y libqt4-dev libqtcore4 libqtgui4 qt4-dev-tools libaudio-dev
  fi
else
  echo "Нужен apt-get (Debian/Ubuntu). Для Fedora: dnf install gcc-c++ automake boost-devel flex bison."
  exit 1
fi

echo ""
echo "=== 1b. Компилятор с поддержкой C++17 ==="
CXX_COMPILER=""
for cxx in g++ g++-12 g++-11 g++-10 g++-9; do
  if command -v "$cxx" &>/dev/null; then
    if "$cxx" -std=c++17 -x c++ -c - -o /dev/null &>/dev/null <<< 'int main() { return 0; }'; then
      CXX_COMPILER="$cxx"
      break
    fi
  fi
done
if [[ -z "$CXX_COMPILER" ]]; then
  echo "  Стандартный g++ не поддерживает C++17. Пробуем установить g++-10..."
  sudo apt-get install -y g++-10 2>/dev/null || sudo apt-get install -y g++-9
  for cxx in g++-10 g++-9 g++; do
    if command -v "$cxx" &>/dev/null && "$cxx" -std=c++17 -x c++ -c - -o /dev/null &>/dev/null <<< 'int main() { return 0; }'; then
      CXX_COMPILER="$cxx"
      break
    fi
  done
fi
if [[ -z "$CXX_COMPILER" ]]; then
  echo "Ошибка: не найден компилятор с поддержкой C++17. Установите g++-10 или новее: sudo apt install g++-10"
  exit 1
fi
export CXX="$CXX_COMPILER"
export CXXFLAGS="-std=c++17"
echo "  Используем: $CXX $CXXFLAGS"

echo ""
echo "=== 2. Клонирование (методичка: git clone rcssserver, rcssmonitor) ==="
mkdir -p "$BUILD_DIR"
cd "$BUILD_DIR"
if [[ ! -d "rcssserver" ]]; then
  git clone https://github.com/rcsoccersim/rcssserver.git
  git clone https://github.com/rcsoccersim/rcssmonitor.git
fi

echo ""
echo "=== 3. Сборка сервера (методичка: cd rcssserver, ./bootstrap, ./configure, make, make install) ==="
cd "$BUILD_DIR/rcssserver"
./bootstrap
./configure CXX="$CXX" CXXFLAGS="$CXXFLAGS"
make -j$(nproc)
sudo make install

echo ""
echo "=== 4. ldconfig (методичка: /usr/local/share в ld.so.conf, ldconfig) ==="
if [[ -f /etc/ld.so.conf ]] && ! grep -q /usr/local/share /etc/ld.so.conf; then
  echo "/usr/local/share" | sudo tee -a /etc/ld.so.conf
fi
sudo ldconfig 2>/dev/null || true

echo ""
echo "=== 5. Сборка монитора (методичка: bootstrap, configure, make, make install) ==="
cd "$BUILD_DIR/rcssmonitor"
make distclean 2>/dev/null || true
./bootstrap
./configure CXX="$CXX" CXXFLAGS="$CXXFLAGS"
make -j$(nproc)
sudo make install

echo ""
echo "=== Готово. Порядок запуска по методичке: ==="
echo "  1. rcssserver"
echo "  2. rcssmonitor"
echo "  3. Программа агентов: cd lab1 && ./start.sh"
echo "  4. В мониторе: Kick off."
