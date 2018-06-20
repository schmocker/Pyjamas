# Use an official Python runtime as a parent image
FROM python:3.6-slim
#RPi: FROM resin/raspberry-pi-python:3.6-slim

# Set the working directory to /app
WORKDIR /app

# Copy the current directory contents into the container at /app
ADD . /app

#RPi: RUN #!/bin/bash
#RPi: RUN sudo apt-get update
#RPi: RUN sudo apt-get install build-essential libssl-dev libffi-dev python3-dev
#RPi:RUN pip install --upgrade pip setuptools wheel


# Install any required packages specified in requirements.txt
RUN pip install --trusted-host pypi.python.org -r requirements.txt

# Make port 80 available to the world outside this container
EXPOSE 5000

# This is only for some systems like rpi
CMD "#!/bin/bash"

# Run run.py when the container launches
CMD ["python", "run.py"]