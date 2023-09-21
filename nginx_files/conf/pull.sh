#!/bin/bash

# Переходим в директорию с вашим репозиторием
cd /myproject/ 

# Получаем последние изменения из репозитория
git fetch

# Получаем имя текущей ветки
branch=$(git rev-parse --abbrev-ref HEAD)

# Проверяем, есть ли изменения в текущей ветке
if [ $(git rev-parse HEAD) != $(git rev-parse @{u}) ]; then
    # Если есть изменения, то выполняем команду git pull
    git pull origin $branch
    echo "Репозиторий успешно обновлен"
else
    echo "Репозиторий уже на последнем обновлении"
fi

