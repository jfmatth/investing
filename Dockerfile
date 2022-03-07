ARG TOKEN
# FROM python:3.8-slim

FROM python:3.8 AS PIPENV

WORKDIR /usr/src/pipenv
COPY Pipfile Pipfile.lock /usr/src/pipenv/

RUN pip install pipenv
RUN pipenv lock --requirements > requirements.txt


FROM python:3.8-slim-buster
WORKDIR /usr/src/app
ENV IEX_TOKEN $(TOKEN)
ENV PROJECT_DIR /usr/src/app

COPY --from=PIPENV /usr/src/pipenv/requirements.txt /usr/src/app/
RUN pip install -r /usr/src/app/requirements.txt

# New for Pipenv - Credit to https://jonathanmeier.io/using-pipenv-with-docker/
# RUN pip install pipenv
# ENV PROJECT_DIR /usr/src/app
# WORKDIR ${PROJECT_DIR}
# COPY Pipfile Pipfile.lock ${PROJECT_DIR}/
# RUN pipenv install --system --deploy

COPY investing / ${PROJECT_DIR}/

RUN python manage.py collectstatic --no-input

ENTRYPOINT ["waitress-serve"]
CMD ["--host=0.0.0.0", "--port=80", "investing.wsgi:application"]