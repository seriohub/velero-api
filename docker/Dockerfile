FROM python:3.10 as velero-api
LABEL mantainer="DS"

# Update packages and install basics
RUN apt-get update && apt-get install -y \
	wget \
	unzip \
	git \
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
#RUN find . -type f -name "tmp" -exec rm -rf {} +
#RUN find . -type f -name "*.yaml" -exec rm -f {} +
#RUN find . -type f -name "__pycache__" -exec rm -rf {} +
#RUN find . -type f -name "*.env" -exec rm -f {} +

#RUN rm -rf /app/tmp /app/__pycache__

RUN mkdir /app/velero-client
COPY ../velero-client /app/velero-client

# expose port
EXPOSE 8001

WORKDIR /app/
RUN echo "Ready!"
CMD ["python3", "-u" , "main.py"]
