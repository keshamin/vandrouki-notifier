FROM python:3.7-alpine
RUN git clone https://github.com/keshamin/vandrouki-notifier.git
WORKDIR /vandrouki-notifier
RUN pip install -r requirements.txt
CMD ["python", "bot.py"]
