# dialogue-service-api-main
 
# Fastapi gateway for dialogue service

Quick access to the open api specification of the service - [here](./openapi.yaml)

Visualize - [here](https://editor.swagger.io)


### To run the full set of services locally
- create an up-to-date .env file based on .env.example
- create docker image: ``` docker build -t get-joke ./app/get_jokes ```
- sudo docker-compose run --rm "dialog-api" make migrate
- sudo docker-compose up --build -d
