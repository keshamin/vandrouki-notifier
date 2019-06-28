FROM python:3.7-alpine
RUN apk update && apk upgrade && \
    apk add --no-cache bash git openssh
RUN git clone https://github.com/keshamin/vandrouki-notifier.git && \
    cd /vandrouki-notifier && \
    git checkout dev
WORKDIR /vandrouki-notifier
RUN pip install -r requirements.txt
CMD ["python", "bot.py"]
