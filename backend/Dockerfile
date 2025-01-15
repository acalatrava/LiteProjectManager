# Use the official Python 3.11 image as the base image
FROM python:3.11

# Set the working directory in the container
WORKDIR /app

# Install the required system packages
RUN apt-get update && apt-get install -y \
    libmagic1

# Copy the requirements.txt file to the container
COPY requirements.txt .

# Install the Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code to the container
COPY . .

# Install Cron
RUN apt-get update
RUN apt-get -y install cron

# Add cron jobs
#RUN crontab -l | { cat; echo "0 8 * * * cd /app && /usr/local/bin/python cron.py 24"; } | crontab -

# Set the port on which the FastAPI app will run
ENV SERVER_PORT=8000

# Expose the port on which the FastAPI app will run
EXPOSE 8000

# Start the FastAPI app using Uvicorn
CMD ["/bin/sh", "start.sh"]
