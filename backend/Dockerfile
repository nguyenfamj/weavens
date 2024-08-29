FROM public.ecr.aws/lambda/python:3.10-arm64

ENV POETRY_VERSION=1.8.2

RUN pip install "poetry==$POETRY_VERSION"

WORKDIR ${LAMBDA_TASK_ROOT}

COPY pyproject.toml poetry.lock ./
RUN poetry config virtualenvs.create false \
    && poetry install --no-dev

COPY ./src ./src
COPY ./.env.prod ./.env

CMD [ "src.main.handler"]