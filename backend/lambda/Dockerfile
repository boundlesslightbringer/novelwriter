# this image is optimized and does not need multi-stage build
FROM public.ecr.aws/lambda/python:3.12-x86_64

COPY pyproject.toml ./
COPY config.json ./
COPY pydantic_models.py ./
COPY entity_miner.py ./

RUN pip install --no-cache-dir --user .

CMD ["entity_miner.lambda_handler"]