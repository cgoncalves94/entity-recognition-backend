# Tech Entity Recognition

This project is a sophisticated FastAPI application designed to perform technology entity recognition, topic classification, and technology recommendation. It leverages the power of Natural Language Processing (NLP) and Machine Learning (ML) to analyze text and extract meaningful insights, all within a secure and efficient web service.

The application uses a BERTopic model, a topic modeling technique that utilizes transformers and c-TF-IDF to create dense clusters of similar documents. This model is used to classify the text into various topics.

In addition, the application uses Spacy, a powerful library for advanced NLP in Python, for entity extraction. It identifies and extracts technology-related entities from the text, providing a deeper understanding of the content.

The application also uses the `sentence-transformers/all-MiniLM-L6-v2` model to generate embeddings for the input text. These embeddings capture the contextual meaning of the text and are used in the dynamic scoring algorithm to measure the relevance of entities to the text and topic keywords.

The combination of these techniques allows the application to dynamically score entities based on their relevance to the text and the topic keywords, providing valuable insights into the analyzed text. Furthermore, the application provides technology recommendations based on the scored entities, making it a useful tool for technology-related decision-making processes.

The application is secured with a JWT-based authentication system, ensuring that only authenticated users can access the NLP services. User credentials and refresh tokens are securely stored in MongoDB, facilitating efficient token management and validation processes.

## Dependencies


You can install all dependencies using the following command:

```bash
pip install -r requirements.txt
```

## Project Structure

The project is structured as follows:

-   `main.py`: The main script that runs the application.
-   `src/`: This directory contains the source code for the application.
    -   `auth/`: Contains the authentication system's source code.
    -   `nlp/`: Contains the NLP services' source code.
-   `models/`: This directory contains the BERTopic model used for topic classification.
-   `data/`: This directory contains data files like `tech_entities.json`, which contains patterns and information about different technology-related entities.

## Running the Application

You can run the application using the following command:

```bash
uvicorn main:app --reload
```

This will start the FastAPI application with hot-reloading enabled. You can access the application at http://localhost:8000 and the API documentation at http://localhost:8000/docs.

## Future Work

The project is poised for further enhancements and feature additions.