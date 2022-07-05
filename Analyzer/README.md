# Analyzer

Application which serves as a search engine. It creates a Top2Vec model from the scraped data pages and 
uses it to find the related documents for a users query.

## Requirements

* Python 3.8 or higher
* pip3
* Docker

## Setup

The tool reads the necessary data for connecting the database from the `config.conf` file.
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

2. Run the tool

    ```shell
    python main.py
    ```
    
    or 
    
    ```shell
    python3 main.py
    ```

### Running in Docker

1. Build the image
    
    ```shell
    docker build . -t analyzer:latest
    ```

   **Notes**: 
   * Command in this form should be run from the same directory the **Dockerfile** is located.
   * If the command is not run from the directory the Dockerfile is located in, replace the "." in the command with the
   relative path to the Dockerfile from the current directory.

2. Run the container

    ```shell
    docker run -d --name analyzer -e UPLINK=<uplink_url> -e UPLINK_KEY=<uplink_key> \
   -e TRAINER_THREADS=<number_of_trainer_threads>  analyzer:latest
    ```


#### Notes:
   * Running the analyzer natively requires the presence of the following environment variables:
      1. UPLINK
      2. UPLINK_KEY
      3. TRAINER_THREADS

      *UPLINK* is the uplink URL where the analyzer has to register its functions
      
      *UPLINK_KEY* is the key used to authenticate with the webapp

      *TRAINER_THREADS* is the number of threads used for training the model. CPU cores / 2 is the ideal.
   * If no *UPLINK* or *UPLINK_KEY* environment variable is defined the application will exit.
   * If no *TRAINER_THREADS* environment variable is defined, 8 will be used by default(this will be adjusted to the
   number of CPU cores in the future, until then, change the number in the code).
   

## Author

**Előd Kocsis**

Email: elod.kocsis@outlook.com
