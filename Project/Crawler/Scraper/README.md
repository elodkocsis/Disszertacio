# Scraper

Application used for scraping the text contents, URLs and metadata of webpages.

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

3. Run the tool

    ```shell
    python main.py
    ```
    
    or 
    
    ```shell
    python3 main.py
    ```

### Running in Docker

Since the tool has to go through more than 210 mil chatters, it is advised to run the tool in docker,
preferably on a server which can connect to the mongodb instance that has to be scrubbed.

1. Build the image
    
    ```shell
    docker build . -t scraper:latest
    ```

   **Notes**: 
   * Command in this form should be run from the same directory the **Dockerfile** is located.
   * If the command is not run from the directory the Dockerfile is located in, replace the "." in the command with the
   relative path to the Dockerfile from the current directory.

2. Run the container

    ```shell
    docker run -d --name scraper --network crawler scraper:latest
    ```

## Author

**Előd Kocsis**

Email: elod.kocsis@outlook.com
