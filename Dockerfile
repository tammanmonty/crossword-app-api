FROM ubuntu:latest
LABEL authors="Tamman Montanaro"

FROM python:3.8-slim

ENTRYPOINT ["top", "-b"]