import pytest
from opinion_clob_sdk.model import TopicStatus, TopicType, TopicStatusFilter


class TestEnums:
    """Test enum values match expected API values"""

    def test_topic_status_values(self):
        """Test TopicStatus enum values"""
        assert TopicStatus.CREATED.value == 1
        assert TopicStatus.ACTIVATED.value == 2
        assert TopicStatus.RESOLVING.value == 3
        assert TopicStatus.RESOLVED.value == 4
        assert TopicStatus.FAILED.value == 5
        assert TopicStatus.DELETED.value == 6

    def test_topic_type_values(self):
        """Test TopicType enum values"""
        assert TopicType.BINARY.value == 0
        assert TopicType.CATEGORICAL.value == 1

    def test_topic_status_filter_values(self):
        """Test TopicStatusFilter enum values"""
        assert TopicStatusFilter.ALL.value is None  # Changed to None
        assert TopicStatusFilter.ACTIVATED.value == "activated"  # Changed to string
        assert TopicStatusFilter.RESOLVED.value == "resolved"  # Changed to string

    def test_enum_membership(self):
        """Test enum membership"""
        assert TopicStatus.ACTIVATED in TopicStatus
        assert TopicType.BINARY in TopicType
        assert TopicStatusFilter.ALL in TopicStatusFilter

    def test_enum_iteration(self):
        """Test enum iteration"""
        status_values = [status.value for status in TopicStatus]
        assert 1 in status_values
        assert 2 in status_values
        assert 4 in status_values

        type_values = [t.value for t in TopicType]
        assert 0 in type_values
        assert 1 in type_values
