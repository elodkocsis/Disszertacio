# Analyzer

Application that serves as the front-end of the system. It handles user inputs and displays the search results for user 
queries.

## Requirements

* Python 3.8 or higher
* pip3
* Docker
* Java 11

## Setup

### Running natively

1. Install the requirements

   ```shell
    pip install -r requirements.txt
    ```
    
    or 
    
    ```shell
    pip3 install -r requirements.txt
    ```

2. Run the app server

    ```shell
    anvil-app-server --app DrkSrch --uplink-key <uplink_key> --port <exposed_port>
    ```

### Running in Docker

1. Build the image
    
    ```shell
    docker build . -t webapp:latest
    ```

   **Notes**: 
   * Command in this form should be run from the same directory the **Dockerfile** is located.
   * If the command is not run from the directory the Dockerfile is located in, replace the "." in the command with the
   relative path to the Dockerfile from the current directory.

2. Run the container

    ```shell
    docker run -d --name webapp -e KEY=<uplink_key> -e PORT=<exposed_port>  webapp:latest
    ```


#### Notes:
   * Running the analyzer natively requires the presence of the following environment variables:
      1. KEY
      2. PORT

      *KEY* is the key used to define an authentication key for applications and services that want to register
   functions to the uplink.
      
      *PORT* is the port the webapp should be reachable on. 

   * If no *KEY* environment variable is defined or passed to the *anvil-app-server* command, applications cannot
register functions and methods with the appserver.
   

## Author

**Előd Kocsis**

Email: elod.kocsis@outlook.com
