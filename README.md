# Сервис проверки видеофайлов на нарушение авторских прав

В репозитории представлено решение задачи нахождения нарушений авторских прав в видеофайлах.

Сервис использует **Python** для работы с моделями нейросетей, **GO** для обработки видеофайлов и передачи информации в веб-сервис, **Kafka** для общения между бекендом и ML сервисами. Мета-информация хранится в **PostgreSQL**, видео в **S3**. Для хранения эмбеддингов видео используется векторная база данных **Milvus**.

Более подробная техническая документация представлена в **DOCUMENTATION.md.**
Пайплайн обучения модели детекции картинки в картинке находится в **notebooks/pip_train.ipynb**.

## Структура проекта
```
├── configs
│   └── (Конфигурационные файлы)
├── emb-service
│   └── (Сервис для подсчета эмбеддингов)
├── front
│   └── (Сервис для )
├── notebooks
│   └── (Эксперименты с данными)
├── s3/data
│   └── (Данные, хранящиеся в S3)
├── video-service
│   └── (Сервис для обработки видео)
├── Makefile
├── README.md
└── docker-compose.yml
```

### Запуск
```
docker compose up -d --build
```

### STOP
```
docker compose down
```

### Тестирование
```
curl -X POST "http://localhost:1111/video" \
  -F "video=@/path/to/your/video.mp4" \
  -F "name=video.mp4" \
  -F "index=true"
```

### GET
```
curl http://localhost:1111/video/{uuid}
```
### GET PROCESSING
```
curl http://localhost:1111/processing/{uuid}
```
