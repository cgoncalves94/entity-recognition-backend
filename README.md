# Tech Entity Recognition

This project is a sophisticated Python application designed to perform technology entity recognition and topic classification. It leverages the power of Natural Language Processing (NLP) and Machine Learning (ML) to analyze text and extract meaningful insights.

The application uses a BERTopic model, a topic modeling technique that utilizes transformers and c-TF-IDF to create dense clusters of similar documents. This model is used to classify the text into various topics.

In addition, the application uses Spacy, a powerful library for advanced NLP in Python, for entity extraction. It identifies and extracts technology-related entities from the text, providing a deeper understanding of the content.

The application also uses the `sentence-transformers/all-MiniLM-L6-v2` model to generate embeddings for the input text. These embeddings capture the contextual meaning of the text and are used in the dynamic scoring algorithm to measure the relevance of entities to the text and topic keywords.

The combination of these techniques allows the application to dynamically score entities based on their relevance to the text and the topic keywords, providing valuable insights into the analyzed text.

## Dependencies

The project requires the following Python packages:

-   `bertopic==0.16.0`
-   `spacy==3.7.2`
-   `torch==2.2.0`
-   `numpy==1.26.2`
-   `scikit-learn==1.4.0`
-   `transformers==4.37.2`

You can install all dependencies using the following command:

```bash
pip install -r requirements.txt
```

## Project Structure

The project is structured as follows:

-   `main.py`: The main script that runs the application.
-   `src/`: This directory contains the source code for the application.
    -   `entity_extraction.py`: Contains functions for extracting technology-related entities from text.
    -   `topic_classification.py`: Contains functions for classifying text into topics.
    -   `dynamic_scoring.py`: Contains functions for dynamically scoring entities based on their relevance to the text and the topic keywords.
    -   `utilities.py`: Contains utility functions like `load_json_file`.
-   `models/`: This directory contains the BERTopic model used for topic classification.
-   `data/`: This directory contains data files like `tech_entities.json`, which contains patterns and information about different technology-related entities.

## Running the Application

You can run the application using the following command:

```bash
python main.py
```

