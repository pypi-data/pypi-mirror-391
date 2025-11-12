import pytest
from datetime import datetime, timedelta
from cryptography.fernet import Fernet
from memoria import MemoryVault, SemanticSearcher, TimelineManager, AIEnhancer


@pytest.fixture
def vault():
    """Create an in-memory MemoryVault instance with encryption key for tests."""
    key = Fernet.generate_key()
    return MemoryVault(db_path=':memory:', key=key)


def test_add_and_query_memory(vault):
    """Test adding a memory and querying it via semantic search."""
    vault.add_memory("Test content", datetime.now(), "test")
    searcher = SemanticSearcher(vault)
    results = searcher.query("Test content")
    assert len(results) > 0
    assert "Test content" in results[0]['content']


def test_generate_insight_local_provider(vault):
    """Test generating an insight summary with local provider."""
    timeline = TimelineManager(vault)
    vault.add_memory("Test event", datetime.now(), "test")
    events = timeline.get_playback(datetime.now() - timedelta(days=1), datetime.now())
    insight = timeline.generate_insight(events, provider='local')
    assert isinstance(insight, str)
    assert len(insight) > 0


def test_generate_insight_cloud_provider(monkeypatch, vault):
    """Test insight generation with a mocked cloud provider response."""
    def mock_generate(*args, **kwargs):
        return "Mocked cloud summary"

    monkeypatch.setattr("google.generativeai.GenerativeModel.generate_content", mock_generate)
    timeline = TimelineManager(vault)
    vault.add_memory("Test event", datetime.now(), "test")
    events = timeline.get_playback(datetime.now() - timedelta(days=1), datetime.now())
    insight = timeline.generate_insight(events, provider='gemini', api_key='dummy_key')
    assert "Mocked" in insight


def test_rate_limit_handling(monkeypatch, vault):
    """Test retry logic for API rate limit handling raises after retries."""

    def mock_rate_limit(*args, **kwargs):
        from google.generativeai.types import BlockedPromptException
        raise BlockedPromptException("Rate limit")

    monkeypatch.setattr("google.generativeai.GenerativeModel.generate_content", mock_rate_limit)
    timeline = TimelineManager(vault)
    with pytest.raises(Exception, match="API error after retries"):
        timeline.generate_insight([], provider='gemini', api_key='dummy_key')


def test_question_answering_local(vault):
    """Test question answering feature with local provider."""
    enhancer = AIEnhancer(vault)
    context = "The meeting is scheduled for 3 PM."
    answer = enhancer.question_answering("When is the meeting?", context, provider='local')
    assert "3 PM" in answer


def test_topic_modeling_local(vault):
    """Test topic modeling clusters texts when using local provider."""
    enhancer = AIEnhancer(vault)
    texts = ["I love AI", "AI is great", "Python is cool"]
    clusters = enhancer.topic_modeling(texts, provider='local')
    assert isinstance(clusters, dict)
    assert len(clusters) > 0
