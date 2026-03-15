#!/bin/bash
# Установка rcssserver + rcssmonitor на Linux по методичке (СтудИзба, раздел 1).
# Проверено на Ubuntu 20.04/22.04. Запуск: ./install_rcssserver_linux.sh

set -e
BUILD_DIR="${BUILD_DIR:-$HOME/rcss_build}"

echo "=== 1. Зависимости (методичка: build-essential, automake, libboost-all-dev, flex, bison) ==="
if command -v apt-get &>/dev/null; then
  sudo apt-get update
  sudo apt-get install -y build-essential automake libboost-all-dev flex bison \
    libqt4-dev libaudio-dev libxt-dev libxi-dev libxrender-dev \
    libfreetype6-dev libfontconfig1-dev \
    git curl
else
  echo "Нужен apt-get (Debian/Ubuntu). Для Fedora: dnf install gcc-c++ automake boost-devel flex bison."
  exit 1
fi

echo ""
echo "=== 2. Клонирование (методичка: git clone rcssserver, rcssmonitor) ==="
mkdir -p "$BUILD_DIR"
cd "$BUILD_DIR"
if [[ ! -d "rcssserver" ]]; then
  git clone https://github.com/rcsoccersim/rcssserver.git
  git clone https://github.com/rcsoccersim/rcssmonitor.git
fi

echo ""
echo "=== 3. Сборка сервера (методичка: cd rcssserver, ./bootstrap, ./configure CXXFLAGS=-std=c++14, make, make install) ==="
cd "$BUILD_DIR/rcssserver"
./bootstrap
./configure CXXFLAGS='-std=c++14'
make -j$(nproc)
sudo make install

echo ""
echo "=== 4. ldconfig (методичка: /usr/local/share в ld.so.conf, ldconfig) ==="
if [[ -f /etc/ld.so.conf ]] && ! grep -q /usr/local/share /etc/ld.so.conf; then
  echo "/usr/local/share" | sudo tee -a /etc/ld.so.conf
fi
sudo ldconfig 2>/dev/null || true

echo ""
echo "=== 5. Сборка монитора (методичка: cd rcssmonitor, те же шаги) ==="
cd "$BUILD_DIR/rcssmonitor"
./bootstrap
./configure CXXFLAGS='-std=c++14'
make -j$(nproc)
sudo make install

echo ""
echo "=== Готово. Порядок запуска по методичке: ==="
echo "  1. rcssserver"
echo "  2. rcssmonitor"
echo "  3. Программа агентов (например: cd lab1 && ./start.sh)"
echo "  4. В мониторе: Kick off."
