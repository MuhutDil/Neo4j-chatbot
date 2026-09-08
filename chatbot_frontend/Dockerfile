FROM python:3.12-slim

WORKDIR /app

COPY ./pyproject.toml /code/pyproject.toml
RUN pip install /code/.

COPY ./src .

CMD ["sh", "entrypoint.sh"]