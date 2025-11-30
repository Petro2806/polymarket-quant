FROM python:3.12-slim


COPY mining/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt


COPY mining/collector.py ./collector.py

CMD ["python", "-u",  "collector.py"]
