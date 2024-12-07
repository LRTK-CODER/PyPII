"""
patterns.py 모듈에 대한 테스트
"""

import pytest
from pathlib import Path
import json
import tempfile
from src.detector.patterns import PatternLoader, PIIPattern, RiskLevel


@pytest.fixture
def sample_patterns_file():
    """테스트용 임시 패턴 파일을 생성하는 fixture"""
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
            ],
            "LOW": [
                {
                    "name": "이메일",
                    "pattern": r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}",
                    "description": "이메일 주소 패턴"
                }
            ]
        }
    }
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        json.dump(patterns_data, f, ensure_ascii=False, indent=2)
        temp_file_path = f.name
    
    yield temp_file_path
    
    # 테스트 후 임시 파일 삭제
    Path(temp_file_path).unlink()


def test_risk_level_enum():
    """RiskLevel 열거형 테스트"""
    assert RiskLevel.HIGH.value == "HIGH"
    assert RiskLevel.MEDIUM.value == "MEDIUM"
    assert RiskLevel.LOW.value == "LOW"


def test_pii_pattern_dataclass():
    """PIIPattern 데이터클래스 테스트"""
    pattern = PIIPattern(
        name="테스트",
        pattern=".*",
        risk_level=RiskLevel.HIGH,
        description="테스트 패턴"
    )
    
    assert pattern.name == "테스트"
    assert pattern.pattern == ".*"
    assert pattern.risk_level == RiskLevel.HIGH
    assert pattern.description == "테스트 패턴"


def test_pattern_loader_with_valid_file(sample_patterns_file):
    """유효한 패턴 파일 로드 테스트"""
    patterns = PatternLoader.load_patterns(sample_patterns_file)
    
    assert len(patterns) == 3
    
    # HIGH 레벨 패턴 확인
    high_pattern = next(p for p in patterns if p.risk_level == RiskLevel.HIGH)
    assert high_pattern.name == "주민등록번호"
    
    # MEDIUM 레벨 패턴 확인
    medium_pattern = next(p for p in patterns if p.risk_level == RiskLevel.MEDIUM)
    assert medium_pattern.name == "휴대폰번호"
    
    # LOW 레벨 패턴 확인
    low_pattern = next(p for p in patterns if p.risk_level == RiskLevel.LOW)
    assert low_pattern.name == "이메일"


def test_pattern_loader_with_invalid_file():
    """존재하지 않는 파일 로드 시 예외 테스트"""
    with pytest.raises(FileNotFoundError):
        PatternLoader.load_patterns("non_existent_file.json")


def test_pattern_loader_with_invalid_json(tmp_path):
    """잘못된 JSON 형식 파일 로드 시 예외 테스트"""
    invalid_json_file = tmp_path / "invalid.json"
    invalid_json_file.write_text("{invalid json")
    
    with pytest.raises(json.JSONDecodeError):
        PatternLoader.load_patterns(str(invalid_json_file))