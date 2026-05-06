# INA-Monitor

Мониторинг даннных с датчика INА219 для Raspberry Pi

## Возможности
 - отображение мгновенного значения напряжения, тока и мощности
 - графики напряжения, тока и мощности
 
## Требования
- python3
- flask
- smbus2
- uv

## Предварительно

1. Включить интерфейс I2C

- Запустить в терминале sudo raspi-config
- Перейти в Interfacing Options
- Выбрать I2C и нажать Yes для включения
- Перезагрузить raspberry

2. Установить инструменты для работы с шиной

```
sudo apt-get install -y i2c-tools
```
 
## Быстрый старт 
```
# 1. Клонирование репозитория
git clone https://github.com/rodnaxel/ina-monitor.git
cd gmessage

# 2. Устанавливаем uv (https://github.com/astral-sh/uv)

# для windows
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex

# для linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# 3. Установка зависимостей
uv sync --frozen

# 4. Запуск программы
uv run main.py
```

## F.A.Q

1. Если не подключается к устройство, то необходимо проверить правильность адреса

```
sudo i2cdetect -y 1
```
