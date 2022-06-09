#!/bin/bash

service tor start && privoxy --pidfile /run/privoxy.pid /etc/privoxy/config && python3 main.py
