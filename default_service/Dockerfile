# Use an official Python runtime as a parent image
FROM python:3.11

WORKDIR app/

# Copy the requirements file into the container at /app
COPY requirements.txt /app/
COPY text_corpus /app/text_corpus

# Install any needed packages specified in requirements.txt
RUN pip install -r requirements.txt

# Copy the rest of the application code into the container at /app
COPY ./default_service /app/

# Port of my application
EXPOSE 5001

# Run __main__.py which will start a uvicorn server for the fast API
CMD ["python","."]