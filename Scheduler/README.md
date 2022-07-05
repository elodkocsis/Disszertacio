# Scheduler / Processor

Applications used for scheduling URLs to be scraped and to be saved back into the database.

The scheduler is designed to run periodically, where it will read all schedulable URLs from the database and 
send them over to the scrapers to be scraped of their content.

The processor is responsible for reading the results sent by the scrapers from the message queue and save them to the
database.

## Requirements

* Python 3.8 or higher
* pip3
* Docker

## Setup

The tool reads the necessary data for connecting to a message queue and database from the `config.conf` file.
In case the data changes, change them accordingly in the configuration file.

### Running natively

1. Install the requirements

   ```shell
    pip install -r requirements.txt
    ```
    
    or 
    
    ```shell
    pip3 install -r requirements.txt
    ```

2. Run the Scheduler

    ```shell
    python scheduler_main.py
    ```
    
    or 
    
    ```shell
    python3 scheduler_main.py
    ```

3. Run the Processor

    ```shell
    python processor_main.py
    ```
    
    or 
    
    ```shell
    python3 processor_main.py
    ```

### Running in Docker

#### Scheduler

1. Build the image
    
    ```shell
    docker build . -f ./Dockerfile_scheduler -t scheduler:latest
    ```

   **Notes**: 
   * Command in this form should be run from the same directory the **Dockerfile** is located.
   * If the command is not run from the directory the Dockerfile is located in, replace the "." in the command with the
   relative path to the Dockerfile from the current directory.

2. Run the container

    ```shell
    docker run -d --name scheduler -e NUM_OF_URLS=<number_of_urls_to_schedule_in_a_run> scheduler:latest
    ```

#### Processor

1. Build the image
    
    ```shell
    docker build . -f ./Dockerfile_processor -t processor:latest
    ```

   **Notes**: 
   * Command in this form should be run from the same directory the **Dockerfile** is located.
   * If the command is not run from the directory the Dockerfile is located in, replace the "." in the command with the
   relative path to the Dockerfile from the current directory.

2. Run the container

    ```shell
    docker run -d --name processor -e NUM_OF_URLS=<number_of_urls_to_schedule_in_a_run> processor:latest
    ```

#### Notes:
   * If no  *NUM_OF_URLS* environment variable is defined, 8000 will be set by default.


## Author

**Előd Kocsis**

Email: elod.kocsis@outlook.com
