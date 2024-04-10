import pytest

from src.nlp.services.blueprint_matching import load_blueprints_corpus, match_blueprints


@pytest.fixture
async def blueprints_corpus():
    """Async fixture to load the blueprints_corpus from the JSON file."""
    return await load_blueprints_corpus()


@pytest.fixture
def nlp_output():
    """Fixture for the NLP output with extracted entities and recommendations."""
    return [
        {
            "extracted_entities": [
                {"entity_name": "TypeScript", "category": "Frontend Programming Languages"},
                {"entity_name": "React", "category": "JavaScript Frameworks/Libraries"},
            ],
            "recommendations": [
                {"category": "Frontend Programming Languages", "recommendation": "Express.js"},
                {"category": "JavaScript Frameworks/Libraries", "recommendation": "React"},
            ],
        }
    ]


@pytest.mark.asyncio
async def test_match_blueprints(blueprints_corpus, nlp_output):
    """Tests that the match_blueprints() function correctly matches recommendations."""
    matched_blueprints = match_blueprints(nlp_output, await blueprints_corpus)

    assert matched_blueprints is not None
    assert isinstance(matched_blueprints, list)

    for blueprint in matched_blueprints:
        assert "matched_tags" in blueprint
        matched_tags = set(blueprint["matched_tags"])

        # Approach 1: Using get() for flexibility
        if matched_tags.issubset(set(blueprint.get("tags", []))):
            pass  # Test passes if subset holds and 'tags' exists

        # Approach 2: Explicitly checking for the 'tags' key
        elif "tags" in blueprint:
            assert matched_tags.issubset(set(blueprint["tags"]))


@pytest.mark.asyncio
async def test_match_blueprints_no_matching_blueprints(blueprints_corpus):
    """Tests that the match_blueprints() function correctly handles no matching blueprints."""
    nlp_output = [
        {
            "recommendations": [{"recommendation": "Unknown Technology"}],
            "extracted_entities": [],
        }
    ]

    blueprints_data = await blueprints_corpus
    matched_blueprints = match_blueprints(nlp_output, blueprints_data)
    assert matched_blueprints is None
