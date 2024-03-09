# Tech Entity Recognition

This FastAPI application is designed for technology entity recognition, topic classification, technology recommendation, and dynamic scoring. It leverages Natural Language Processing (NLP) and Machine Learning (ML) techniques, utilizing libraries and models such as Spacy, BERTopic, and sentence-transformers, all within a secure and efficient web service.

## Key Features

- Entity Recognition and Classification: Identifies and categorizes technical entities using Spacy.
- Topic Classification with BERTopic: Enhances text understanding and categorization into predefined topics.
- Dynamic Scoring: Adjusts entity relevance scores based on context using `sentence-transformers/all-MiniLM-L6-v2`.
- Recommendation System: Suggests relevant technologies based on broader concepts identified in user inputs.
- JWT-based Authentication: Secures access to NLP functionalities, with credentials and tokens stored in MongoDB.
- Docker Integration: Ensures consistent and scalable deployment across environments.

## Installation and Running the Application

To run the application using Docker, ensure Docker and docker-compose are installed on your system. Then execute:

```bash
docker network create app_main
docker-compose up -d --build
```
This command builds the Docker image and starts the service. The application can be accessed at http://localhost:16000 with API documentation available at http://localhost:16000/docs.

## Project Structure

The project is structured as follows:


-   `src/`: This directory contains the source code for the application.
    -   `auth/`: Contains the authentication system's source code.
    -   `nlp/`: Contains the NLP services' source code.
    -   `main.py`: The main script that runs the application.
-   `data/`: This directory contains data files like `tech_entities.json`, which contains patterns and information about different technology-related entities.
-   `tests/`: Contains automated tests for the application, ensuring reliability and functionality. This includes tests for authentication routes and other critical functionalities.


## Running Tests

To run automated tests within the Docker environment, use the following command:

```bash
docker compose exec app pytest
```
This command executes the test suite, ensuring that all functionalities work as expected within the Dockerized application.


## Conclusion

The Tech Entity Recognition project has evolved significantly, incorporating Docker for deployment, enhancing security with JWT authentication, and improving NLP functionalities. These advancements provide a solid foundation for further development and innovation.
