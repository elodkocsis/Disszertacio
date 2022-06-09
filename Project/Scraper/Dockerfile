FROM python:3.9

WORKDIR /app

# ADD . /app
ADD ./requirements.txt /app/requirements.txt
ADD ./ProxySetup /app/ProxySetup
ADD ./start_scraper.sh /app/start_scraper.sh

RUN apt-get update && apt-get -y upgrade && apt-get install -y tor privoxy curl netcat nano

RUN pip3 install --upgrade pip && pip3 install -r requirements.txt

RUN cp ProxySetup/torrc /etc/tor/ && cp ProxySetup/config /etc/privoxy/ && rm /etc/privoxy/default.action && touch rm /etc/privoxy/default.action

ENV AM_I_IN_A_DOCKER_CONTAINER True

ENTRYPOINT ["/bin/bash", "start_scraper.sh"]
