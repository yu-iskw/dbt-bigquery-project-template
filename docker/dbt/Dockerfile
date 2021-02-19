FROM python:3.8

# NOTE
# The context should be the project root,
# because our dbt requires `./config` directory.

USER root
WORKDIR /root

# Install libraries
RUN apt-get update -y \
    && apt-get install -y --no-install-recommends \
        build-essential \
        yamllint \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Copy project files
COPY . .

# Create a symbolic link of dbt profiles
RUN ln -s ./docker/dbt/.dbt /root/.dbt

# Set up python environment
RUN pip install --no-cache-dir -U pip==20.3 \
    && make setup

# Expose port
EXPOSE 8080

# Set entrypoint and command
ENTRYPOINT ["dbt"]
CMD ["--help"]