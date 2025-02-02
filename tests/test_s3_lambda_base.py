import pytest
from typing import Dict, Any, List

from src.scan.pattern import DataPattern, RiskLevel
from src.scan.parsers.s3.lambda_handlers.base import LambdaBaseParser


class MockLambdaParser(LambdaBaseParser):
    """
    Mock parser for testing. / 테스트를 위한 목 파서
    """
    
    def can_handle(self, event: Dict[str, Any]) -> bool:
        return True
        
    def extract_text(self, event: Dict[str, Any]) -> str:
        return "Sample text for testing"
    
    
@pytest.fixture
def sample_patterns() -> List[DataPattern]:
    """
    Create sample patterns for testing. / 테스트용 샘플 패턴을 생성합니다.

    Returns:
        List[DataPattern]: List of test patterns for PII detection / PII 감지를 위한 테스트 패턴 리스트
    """
    return [
        DataPattern(
            name="Test Pattern",
            pattern=r"\d+",
            risk_level=RiskLevel.HIGH,
            description="Test pattern"
        )
    ]
    
@pytest.fixture
def sample_s3_event() -> Dict[str, Any]:
    """
    Create sample S3 event for testing. / 테스트용 S3 이벤트를 생성합니다.

    Returns:
        Dict[str, Any]: Sample S3 event dictionary / 샘플 S3 이벤트 딕셔너리
    """
    return {
        'Records': [{
            's3': {
                'bucket': {'name': 'test-bucket'},
                'object': {'key': 'test/file.txt'}
            }
        }]
    }
    
    
def test_get_s3_info(sample_s3_event):
    """
    Test S3 info extraction from event. / 이벤트에서 S3 정보 추출을 테스트합니다.

    Args:
        sample_s3_event (Dict[str, Any]): Sample S3 event fixture / 샘플 S3 이벤트 fixture
    """
    parser = MockLambdaParser(patterns=[])
    bucket, key = parser.get_s3_info(sample_s3_event)
    assert bucket == 'test-bucket'
    assert key == 'test/file.txt'
    
def test_get_s3_info_invalid_event():
    """
    Test error handling for invalid event. / 잘못된 이벤트에 대한 에러 처리를 테스트합니다.
    """
    parser = MockLambdaParser(patterns=[])
    with pytest.raises(ValueError):
        parser.get_s3_info({})
        
def test_scan_with_empty_text(sample_patterns, sample_s3_event):
    """
    Testing scanning with empty text. / 빈 텍스트 검사를 테스트합니다.

    Args:
        sample_patterns (List[DataPattern]): Sample patterns fixture / 샘플 패턴 fixture
        sample_s3_event (Dict[str, Any]): Sample S3 event fixture / 샘플 S3 이벤트 fixture
    """
    class EmptyTextParser(MockLambdaParser):
        def extract_text(self, event: Dict[str, Any]) -> str:
            return ""
    
    parser = EmptyTextParser(patterns=sample_patterns)
    results = parser.scan(sample_s3_event)
    assert len(results) == 0
