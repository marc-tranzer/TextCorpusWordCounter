# Display Most Frequent Words in Text Corpus

Text data is generated in many sparse locations.
The most frequently used words (10 by default) alongside their occurrences  will be returned by a publicly accessible endpoint
The system should follow the fog-computing approach by performing part of the computation on edge nodes
(which have access to the text stream) and then aggregated and finalized on a central one
(which has access to the display).

## Proposed Architecture

### Backend Software Architecture
Although this doesn't represent a real-case scenario the corpus will be stored locally in a folder,
accessible from both central and remote node

On real life scenario:
- We may want to have a File Database to store the entire corpus,
- or be able to automatically retrieve file from a web URL.

The goal of the project is to be able to process large file corpus within a 
limited amount of time. The project should take into account that as the corpus grows larger, 
one machine will not be able to process all the text.

We will need to design an architecture that can be efficiently deployed on a distributed system.

The most time-consuming part of this project is parsing a document and creating a dictionary of text occurrences.
Each file with the text corpus may have a different size, thus each file may require a different amount of computation time.

The main goal of this project is to efficiently distribute the load of text processing across different nodes.

We will use the following architecture:

A main (central) node with a web API accessible privately with the following responsibilities:

- API endpoint that accepts a folder of text for processing.
  - Read all the file locations inside the folder and store them in a task SQL Database.
    - If a second folder is provided it will be added to the list of text to process
  - Then it fills message queue with all the files that need to be processed.
    - The task queue should support message acknowledgment:
      - If the result hasn't been acknowledged, the task will be pushed again (the node might be offline).
      - This kind of acknowledgment on broken node  will not be implemented here.
      - If the result has been acknowledged but with an error, the task will be retried three times. 

- An API endpoint to receive results after a job was processed:
  - It pushes the remote node result in a result queue that will process the results
  - Update the result occurrence dict of the given task
  - Update the status to PROCESS/FAILED and handle retry

- The central node will have one result processor worker
  - It processes the results from the result queue and update the global word count DB

- Finally, we will have most_frequent_words_count endpoint  that returns the most frequent words from the text corpus

For processing the text, we set up a group of 10 remote nodes with the following responsibilities:
  - Dequeue a task from the task queue
  - Perform text word occurrence count
  - Send the processing result with the occurrence dict
  - It will poll for tasks and push for result with the central node via RestAPI

API design:

The main node API will contain the following endpoints. See [Documentation](default_service/openapi.yaml)
- /tasks_queue
  - Method GET: Will dequeue the older task from the queue
  - Method POST: Will enqueue a new task to the queue
- /processing_text_tasks/{uuid}/results
  - Method PUT: 
    - Update the result occurrence dict of the given task
    - Update the status to PROCESS/FAILED and handle retry
    - Update the word occurrence count table
- /text_corpus_locations
  - Method POST: Add a new text corpus to process
- /most_frequent_words_count
  - Method GET: Show the result of the scan
    - top_word_to_return_count: int = 10
    - wait_for_final_result: bool = True

DB design:

Proposed architecture:

Table1:

    name: processing_text_task

    id: unique incremented int. Index of the table. # Will be used as identifier for the nodes
    uuid: unique uuid. # Will be used as identifier on the API side ( protecting against sequential ID attack)
    status: Enum stored as integer  
    StatusEnum: PROCESSED/IN_PROGRESS/NOT_STARTED/FAILED
    file_location: str

Table2:

    name: word_occurrence
      
    word: unique string. Index of the table
    occurrence: int
    present_in_text_ids: int list of analysed_text indexes

We should store the queue in a [Redis Queue](https://redis.com/glossary/redis-queue) to simplify the messaging system between the nodes

### Docker Architecture

On this project we suppose that the file are stored locally and accessible to the node.
The corpus folder will be stored locally on each node to mock this comportment

In a real life scenario we should be able to specify a list of WEB URL or upload a folder of file

The project has 2 docker file

- One Dockerfile to start the central server
- One Dockerfile to start a processing node

And a docker compose file that generate 10 processing node and the central server 

### Alternative approach And Discussion

This approach scales well with CPU intensive processing task, which is not the case on this project.
It scales poorly with I/O intensive operations which is the main bottleneck of the project.

A different approach should have been to use the MapReduce approach with consistent hashing

- Each filename is hashed and then distribute to the  "map node" directly using consistent hashing
- The map node will count every wor on the file
- Then when every task have been processed ( every words counted on each file), they are sent to a cluster on reduce function
- Each word key is associate to one of the "reduce node" using consistent hashing
- The reduce node will be able to create the final word count for each unique word,
- Each reduce will return the TOP10 word occurences it processed
- The master node which will finish the work by getting the global TOP10 word occurences.

## Develop And Test the project

### Install the code for local testing

    python3.11 -m venv .venv
    source .venv/bin/activate
    pip install -U pip setuptools wheel pip-tools
    pip install -r requirements-dev.txt -r requirements.txt



### Run the tests

Although this is a bad practice, this project doesn't implement any unit-test.
To ensure our solution is stable we should have unit testing including:

- Test on the API Queue
- Word Occurrence Count Algorithm
- Node Result Processing

### Run the project locally

    # Launch Central Node
    source .venv/bin/activate
    python3 default_service

    # launch One Remote Nopde
    source .venv/bin/activate
    python3 workers/text_processor


### Starting the docker

A docker compose file was created to simplify the development.

    docker-compose build
    docker-compose up -d


### Test Corpus

I used this [Open Source Corpus Of Political Text](https://dataverse.harvard.edu/dataset.xhtml?persistentId=doi:10.7910/DVN/YU5JPQ)
as a data source to test the system. 
What I liked with this corpus is that it has different subset of data of different sizes:
- List of Ted Talks transcripts of 2MBs

- Result:
  - ('the', 195345), 
  - ('to', 123326),
  - ('of', 113555), 
  - ('and', 105622),
  - ('a', 102722), 
  - ('that', 76218), 
  - ('in', 71755), 
  - ('I', 64563), 
  - ('is', 58649),
  - ('you', 49969)

- List of Wikipedia Political Text of more than 1.4 GBs

This allows me to test my solution with a small dataset for development
and then use the wikipedia data as a workload test


