# Scheduler / Processor

Applications used for scheduling URLs to be scraped and to be saved back into the database.

The scheduler is designed to run periodically, where it will read all the URLs from the database and send them over to 
the scrapers to be scraped of their content.

## Requirements

* Python 3.8 or higher
* pip3
* Docker

## Setup

The tool reads the necessary data for connecting to a message queue from the `config.conf` file.
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

3. Run the response processor

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
    docker run -d --name scheduler --network crawler_network scheduler:latest
    ```

## Author

**Előd Kocsis**

Email: elod.kocsis@outlook.com
