# For more information, please refer to https://aka.ms/vscode-docker-python
FROM python:3.11-slim-bookworm

# Keeps Python from generating .pyc files in the container
ENV PYTHONDONTWRITEBYTECODE=1

# Turns off buffering for easier container logging
ENV PYTHONUNBUFFERED=1

# Install pip requirements
COPY requirements.txt .
RUN python -m pip install -r requirements.txt

WORKDIR /app
COPY . /app
RUN mkdir -p dua/log

# Setting up time in container
RUN apt-get update && apt-get install -y tzdata
ENV TZ=America/Los_Angeles
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

# Creates a non-root user with an explicit UID and adds permission to access the /app folder
# For more info, please refer to https://aka.ms/vscode-docker-python-configure-containers
RUN adduser -u 1000 --disabled-password --gecos "" andrey && chown -R andrey /app
USER andrey
# RUN adduser -u 5678 --disabled-password --gecos "" appuser && chown -R appuser /app
# USER appuser

# EXPOSE 80

# During debugging, this entry point will be overridden. For more information, please refer to https://aka.ms/vscode-docker-python-debug
CMD ["python", "app.py", "p"]

# docker build -t dice_au .
# docker run -e -v /Users/andrey/dua:/app/dua -v /etc/localtime:/etc/localtime:ro dice_au
# -e TZ=America/New_York
