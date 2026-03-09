FROM public.ecr.aws/lambda/python:3.11

WORKDIR /var/task

COPY requirements.txt .
RUN pip install -r requirements.txt --no-cache-dir

COPY src/ ./src/
COPY models/ ./models/

CMD ["src.api.lambda_handler.handler"]