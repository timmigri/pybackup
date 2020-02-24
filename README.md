# Получение токена для Yandex
1. Находим ID проекта на https://oauth.yandex.ru
2. Переходим по ссылке https://oauth.yandex.ru/authorize?response_type=token&client_id=PROJECT_ID
3. Вставить в `auth/yandex/data.json` в виде `{"token": "Some token"}`

# Получение данных для Google
1. https://console.cloud.google.com/apis/credentials?project=PROJECT_ID
2. Создать credentials `OAuth Client Id`
3. Скачать файл и вставить его в `auth/google/client_secret.json`