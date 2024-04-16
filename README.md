# Tech Entity Recognition

This FastAPI application is designed for technology entity recognition, topic classification, technology recommendation, dynamic scoring, and blueprint matching. It leverages Natural Language Processing (NLP) and Machine Learning (ML) techniques, utilizing libraries and models such as spaCy, BERTopic, and sentence-transformers, all within a secure and efficient web service.

## Key Features

- **Entity Recognition and Classification**: Identifies and categorizes technical entities using spaCy.
- **Topic Classification with BERTopic**: Enhances text understanding and categorization into predefined topics.
- **Dynamic Scoring**: Adjusts entity relevance scores based on context using `sentence-transformers/all-MiniLM-L6-v2`.
- **Recommendation System**: Suggests relevant technologies based on broader concepts identified in user inputs.
- **Blueprint Matching**: Matches extracted entities and recommendations with predefined blueprints and components.
- **JWT-based Authentication**: Secures access to NLP functionalities, with credentials and tokens stored in MongoDB.
- **Docker Integration**: Ensures consistent and scalable deployment across environments.
- **CI/CD Pipeline**: Automates testing and deployment processes using GitHub Actions, ensuring that the application is always up-to-date and stable.

### Deployment Process

1. **GitHub Actions Workflow**: Triggered by every push to the `main` branch.
2. **Docker Build**: Containerizes the application, ensuring environmental consistency.
3. **Fly.io Deployment**: Deploys the Dockerized application to Fly.io, leveraging its robust platform for running containerized applications.

For more details on our CI/CD process, refer to the `.github/workflows/flyio_deploy.yml` file in our repository.

## Installation and Running the Application

To run the application using Docker, ensure Docker and docker-compose are installed on your system. Then execute:

```bash
docker-compose up -d --build
```
This command builds the Docker image and starts the service. The application can be accessed at http://localhost:16000 with API documentation available at http://localhost:16000/docs.


## Project Structure

The project is structured as follows:

- `src/`: This directory contains the source code for the application.
  - `auth/`: Contains the authentication system's source code.
  - `nlp/`: Contains the NLP services' source code.
    - `services/`: Contains separate service files for different NLP functionalities.
      - `entity_extraction.py`: Contains functions related to entity extraction.
      - `topic_classification.py`: Contains functions related to topic classification.
      - `recommendation_generation.py`: Contains functions related to recommendation generation.
      - `blueprint_matching.py`: Contains functions related to blueprint matching.
    - `router.py`: Defines the API routes for the NLP services.
    - `schemas.py`: Defines the input and output schemas for the NLP services.
    - `utils.py`: Contains utility functions used across the NLP services.
  - `main.py`: The main script that runs the application.
- `data/`: This directory contains data files like `tech_entities.json` and `blueprints_metadata.json`, which contain patterns, information, and metadata about different technology-related entities and blueprints.
- `tests/`: Contains automated tests for the application, ensuring reliability and functionality.
  - `integration/`: Integration tests that test the application's components and their interactions.
    - `auth/test_routes.py`: Tests for the authentication routes.
    - `nlp/test_nlp_endpoints.py`: Tests for the NLP service endpoints.
  - `unit/`: Unit tests that test individual functions and components in isolation.
    - `test_entity_extraction.py`: Tests for the entity extraction functionality.
    - `test_match_blueprints.py`: Tests for the blueprint matching functionality.
    - `test_recommendation_generation.py`: Tests for the recommendation generation functionality.


## Running Tests

To run automated tests within the Docker environment, use the following command:

```bash
docker compose exec app pytest
```
This command executes the test suite, ensuring that all functionalities work as expected within the Dockerized application.


## Conclusion

The Tech Entity Recognition project has evolved significantly, incorporating Docker for deployment, enhancing security with JWT authentication, improving NLP functionalities, and adding blueprint matching capabilities. These advancements provide a solid foundation for further development and innovation.
