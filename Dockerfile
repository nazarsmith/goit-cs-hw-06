FROM python:3.11

RUN apt update

COPY Pipfile .
RUN python -m pip install pipenv
RUN pipenv install --system --skip-lock

COPY src /hw_project/src/
COPY main.py hw_project/

WORKDIR hw_project

ENTRYPOINT ["python", "main.py"]
