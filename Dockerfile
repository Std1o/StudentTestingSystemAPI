
FROM python:3.9


WORKDIR /code


COPY ./Pipfile /code/Pipfile


# Установка pipenv
RUN pip install pipenv

# Копируем Pipfile и Pipfile.lock
COPY ./Pipfile ./Pipfile.lock /code/

# Устанавливаем зависимости из Pipfile.lock
RUN pip install pipenv && \
    pipenv sync --system && \
    pip install sqlalchemy-utils && \
    pip install websockets && \
    pip install gigachat

COPY ./src /code/src
COPY ./images /code/images
COPY ./www.testingsystem.ru.crt /code/
COPY ./www.testingsystem.ru.key /code/

# Добавляем src в PYTHONPATH
ENV PYTHONPATH=/code/src

# Запускаем как модуль
CMD ["python", "-m", "testing_system"]
