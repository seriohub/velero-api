FROM python:3.10-slim as velero-api-base
LABEL maintainer="DS"

# ARG VERSION
# ARG BUILD_DATE
#
# ENV BUILD_VERSION=$VERSION
# ENV BUILD_DATE=$BUILD_DATE

# Update packages and install basics
RUN apt-get update && apt-get install -y \
	wget \
	unzip \
	git \
	curl \
	nano

RUN apt-get -y install python3-pip

RUN pip install --upgrade pip

COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt

# prepare dir
RUN mkdir /app

# Set the working directory inside the container
WORKDIR /app

# Copy the project files to the container
COPY /src /app

# Exclude specific files or directories from the project
# Add more `--exclude` arguments as needed
RUN find . -type f -name "tmp" -exec rm -rf {} +
RUN find . -type f -name "*.yaml" -exec rm -f {} +
RUN find . -type f -name "*.db" -exec rm -f {} +
RUN find . -type f -name "__pycache__" -exec rm -rf {} +
RUN find . -type f -name "*.env" -exec rm -f {} +

# RUN rm -rf /app/tmp /app/__pycache__

# install kubectl
RUN curl -LO https://storage.googleapis.com/kubernetes-release/release/$(curl -s https://storage.googleapis.com/kubernetes-release/release/stable.txt)/bin/linux/amd64/kubectl
RUN chmod +x ./kubectl
RUN mv ./kubectl /usr/local/bin

RUN mkdir /app/data

RUN mkdir /app/velero-client
COPY ../velero-client /app/velero-client

RUN mkdir /app/velero-client-binary

# expose port
EXPOSE 8001
# Expose a volume the database
VOLUME /app/data

# Expose a volume for custom binary download
VOLUME /app/velero-client-binary

WORKDIR /app/
RUN echo "Ready!"
CMD ["python3", "-u" , "main.py"]

FROM velero-api-base as velero-api
ARG VERSION
ARG BUILD_DATE

ENV BUILD_VERSION=$VERSION
ENV BUILD_DATE=$BUILD_DATE
