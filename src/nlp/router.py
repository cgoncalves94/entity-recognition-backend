from auth.jwt import parse_jwt_user_data
from auth.schemas import JWTData

from fastapi import APIRouter, Depends
from typing import List
from nlp.config import nlp_config

from nlp.schemas import InputText, Recommendation

from .service import (load_tech_entities, initialize_matcher_with_patterns, load_bertopic_model, extract_tech_entities, classify_text, dynamic_score_entities, recommend_technologies)

router = APIRouter()


@router.post("/process/", response_model=List[Recommendation])
async def process_texts(
    input_text: InputText, 
    jwt_data: JWTData = Depends(parse_jwt_user_data)
):
    tech_entities = await load_tech_entities()
    matcher = await initialize_matcher_with_patterns(tech_entities)
    model_dir = nlp_config.MODEL_DIR
    
    topic_model = load_bertopic_model(model_dir)
    topic_info = topic_model.get_topic_info()
    topic_name_mapping = dict(zip(topic_info['Topic'], topic_info['Name']))
    results = []

    for text in input_text.texts:
        extracted_entities = extract_tech_entities(text, tech_entities, matcher)
        entity_names = [entity['category'] for entity in extracted_entities]
        entity_string = ', '.join(entity_names)
        text_to_classify = text + ". " + entity_string
        topic_name, topic_keywords = classify_text(text_to_classify, topic_model, topic_name_mapping)
        sorted_entities = dynamic_score_entities(extracted_entities, topic_keywords, text, tech_entities)
        recommendations = recommend_technologies(sorted_entities)
        results.append({
            "input_text": text,
            "predicted_topic_name": topic_name,
            "extracted_entities": sorted_entities,
            "recommendations": recommendations
        })
    return results