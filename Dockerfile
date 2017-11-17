# Use python 3
FROM python:3

# Make port 4444 available to the world outside this container
EXPOSE 4444

# Add the local files 
ADD ./requirements.txt /etree/
ADD ./python /etree/python
ADD ./web /etree/web

# Set working directory
WORKDIR /etree

# Install dependencies
RUN pip3 install -r requirements.txt

# Run the server when the container launches
CMD ["python3", "python/server.py"]