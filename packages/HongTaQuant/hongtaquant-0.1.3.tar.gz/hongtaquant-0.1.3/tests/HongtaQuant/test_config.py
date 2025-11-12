"""Test configuration models."""

from HongTaQuant.HongTaData import Settings


def test_settings_default_values() -> None:
    """测试配置默认值."""
    settings = Settings()
    assert settings.http_timeout == 30
    assert settings.kafka_bootstrap_servers == "localhost:9092"
    assert settings.log_level == "INFO"


def test_settings_kafka_topics_list() -> None:
    """测试Kafka topics列表转换."""
    settings = Settings(kafka_topics="topic1,topic2, topic3")
    topics = settings.kafka_topics_list
    assert len(topics) == 3
    assert "topic1" in topics
    assert "topic2" in topics
    assert "topic3" in topics
