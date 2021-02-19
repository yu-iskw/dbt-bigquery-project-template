FROM python:3.8

# NOTE
# The context should be the project root.

USER root
WORKDIR /root

# Install libraries
RUN apt-get update -y \
    && apt-get install -y --no-install-recommends \
        build-essential \
        yamllint \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Copy files
COPY . .

# Set up python environment
RUN pip install --no-cache-dir -U pip==20.3 \
    && pip install --no-cache-dir -e "./python/dbt-helper"

ENTRYPOINT ["dbt-helper"]
CMD ["--help"]