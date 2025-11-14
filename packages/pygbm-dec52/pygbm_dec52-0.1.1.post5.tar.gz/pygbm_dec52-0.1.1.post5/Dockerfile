# syntax=docker/dockerfile:1
ARG PYTHON_VERSION=3.12.9
FROM python:${PYTHON_VERSION}-slim as base

# Prevents Python from writing pyc files.
ENV PYTHONDONTWRITEBYTECODE=1

# Keeps Python from buffering stdout and stderr to avoid situations where
# the application crashes without emitting any logs due to buffering.
ENV PYTHONUNBUFFERED=1

# Install git
RUN apt-get update && apt-get install -y git

WORKDIR /app

# Copy the source code into the container.
COPY . .

# Install required dependencies for building the package
RUN pip install --upgrade pip setuptools wheel setuptools_scm build

# Install runtime dependencies listed in pyproject.toml
RUN pip install .

# Build the package
RUN python -m build