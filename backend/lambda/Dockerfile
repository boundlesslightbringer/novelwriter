# this image is optimized and does not need multi-stage build
FROM public.ecr.aws/lambda/python:3.12-x86_64

COPY pyproject.toml ./
COPY config.json ./
COPY pydantic_models.py ./
COPY entity_miner.py ./

# Install dependencies to system site-packages (not --user)
# This ensures Lambda runtime can find the packages
RUN pip install --no-cache-dir .

CMD ["entity_miner.lambda_handler"]