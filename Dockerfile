FROM python:3.10-slim-buster

ENV PYTHONPATH "${PYTHONPATH}:/shop"

ENV PYTHONFAULTHANDLER=1 \
  PYTHONUNBUFFERED=1 \
  PYTHONHASHSEED=random \
  POETRY_VERSION=1.7.0 \
  POETRY_VIRTUALENVS_CREATE=false \
  POETRY_CACHE_DIR='/var/cache/pypoetry'

RUN apt-get update && apt-get install -y \
    curl \
    libpq-dev \
    libpangocairo-1.0-0

RUN apt-get autoremove -y && apt-get clean -y && rm -rf /var/lib/apt/lists/* \
  && pip install "poetry-core==1.8.1" "poetry==$POETRY_VERSION" && poetry --version

WORKDIR /shop
COPY ./poetry.lock ./pyproject.toml /shop/

RUN poetry install

COPY . /shop

RUN chmod +x /shop/start_web.sh
CMD ["bash", "/shop/start_web.sh"]
