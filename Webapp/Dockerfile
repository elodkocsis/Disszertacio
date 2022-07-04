FROM python:3.9

ENV PORT 80
ENV AM_I_IN_A_DOCKER_CONTAINER True

RUN apt-get update && apt-get -y upgrade && apt-get install -y curl openjdk-11-jdk

RUN pip3 install --upgrade pip && pip3 install anvil-app-server && anvil-app-server || true

WORKDIR /app

ADD . /app

RUN mkdir /app/.anvil-data && useradd anvil && chown -R anvil:anvil /app/.anvil-data

EXPOSE ${PORT}

USER anvil

ENTRYPOINT ["/bin/bash", "start_webapp.sh"]
