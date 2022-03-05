ARG TOKEN

FROM python:3.8-slim

ENV IEX_TOKEN $(TOKEN)

# New for Pipenv - Credit to https://jonathanmeier.io/using-pipenv-with-docker/
RUN pip install pipenv
ENV PROJECT_DIR /usr/src/app
WORKDIR ${PROJECT_DIR}
COPY Pipfile Pipfile.lock ${PROJECT_DIR}/
RUN pipenv install --system --deploy

COPY investing / ${PROJECT_DIR}/

RUN python manage.py collectstatic --no-input

ENTRYPOINT ["waitress-serve"]
CMD ["--host=0.0.0.0", "--port=80", "investing.wsgi:application"]