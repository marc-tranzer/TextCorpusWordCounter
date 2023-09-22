# Use an official Python runtime as a parent image
FROM python:3.11

WORKDIR app/

# Copy the requirements file into the container at /app
COPY requirements.txt /app/

# NOT IMPLEMENTED: We can assume that the file we want to scan
COPY text_corpus /app/text_corpus

# Install any needed packages specified in requirements.txt
RUN pip install -r requirements.txt

# Copy the rest of the application code into the container at /app
COPY ./remote_workers /app/

# Run __main__.py, we don't need to expose any port for this private service
CMD ["python","find_word_occurrence"]