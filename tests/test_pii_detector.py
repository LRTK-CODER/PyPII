"""PIIDetector 테스트"""

import pytest
from pathlib import Path
import tempfile
from src.detector.pii_detector import PIIDetector, DetectionResult

@pytest.fixture
def pattern_file():
    """테스트용 패턴 파일 생성"""
    patterns_data = {
        "patterns": {
            "HIGH": [
                {
                    "name": "주민등록번호",
                    "pattern": r"(?:[0-9]{2}(?:0[1-9]|1[0-2])(?:0[1-9]|[1,2][0-9]|3[0,1]))-[1-4][0-9]{6}",
                    "description": "주민등록번호 패턴"
                }
            ],
            "MEDIUM": [
                {
                    "name": "휴대폰번호",
                    "pattern": r"01[016789]-?\d{3,4}-?\d{4}",
                    "description": "휴대폰 번호 패턴"
                }
            ]
        }
    }
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        import json
        json.dump(patterns_data, f, ensure_ascii=False, indent=2)
        return f.name

def test_pii_detector_init(pattern_file):
    """PIIDetector 초기화 테스트"""
    detector = PIIDetector(pattern_file)
    assert len(detector.patterns) == 2
    assert "주민등록번호" in detector.compiled_patterns

def test_detect_resident_number(pattern_file):
    """주민등록번호 검출 테스트"""
    detector = PIIDetector(pattern_file)
    text = "주민번호는 950101-1234567 입니다"
    results = detector.detect(text)
    
    assert len(results) == 1
    assert results[0].pattern_name == "주민등록번호"
    assert results[0].matched_text == "950101-1234567"

def test_detect_phone_number(pattern_file):
    """휴대폰번호 검출 테스트"""
    detector = PIIDetector(pattern_file)
    text = "연락처는 010-1234-5678 입니다"
    results = detector.detect(text)
    
    assert len(results) == 1
    assert results[0].pattern_name == "휴대폰번호"
    assert results[0].matched_text == "010-1234-5678"

def test_detect_multiple_patterns(pattern_file):
    """여러 패턴 동시 검출 테스트"""
    detector = PIIDetector(pattern_file)
    text = """
    주민번호는 950101-1234567 이고
    전화번호는 010-1234-5678 입니다
    """
    results = detector.detect(text)
    
    assert len(results) == 2
    pattern_names = {r.pattern_name for r in results}
    assert pattern_names == {"주민등록번호", "휴대폰번호"}

def test_detect_with_context(pattern_file):
    """문맥 포함 검출 테스트"""
    detector = PIIDetector(pattern_file)
    text = "이 사람의 주민번호는 950101-1234567 입니다"
    results = detector.detect(text, context_chars=10)
    
    assert len(results) == 1
    assert "주민번호는" in results[0].context
    assert "입니다" in results[0].context