# Use Python 3.9 base image
FROM python:3.9

# Set working directory inside the container
WORKDIR /app

# Install necessary packages
RUN apt-get update && apt-get install -y --no-install-recommends libjemalloc2 git && rm -rf /var/lib/apt/lists/*

# Copy and install requirements
COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt
RUN python -m pip install --no-cache-dir --upgrade pip

# Copy the bot's source code into the container
COPY . .

# Command to stop any other processes and then run the bot
CMD bash -c "pkill -9 -f 'python main.py' || true && exec python main.py"
