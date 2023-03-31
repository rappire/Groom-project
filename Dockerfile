FROM tiangolo/uvicorn-gunicorn:python3.10
COPY . /app
COPY ./requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt
EXPOSE 8000
ENV PORT 8000