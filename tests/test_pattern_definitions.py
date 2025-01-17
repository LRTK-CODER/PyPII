import pytest
import json
from src.scan.pattern import RiskLevel, DataPattern, PatternLoader

@pytest.fixture
def sample_pattern_file(tmp_path):
    """Create temporary pattern file for testing. / 테스트용 임시 패턴 파일을 생성합니다.
    
    Args:
        tmp_path: Temporary directory path provided by pytest / pytest에서 제공하는 임시 디렉토리 경로

    Returns:
        Path: Path to temporary pattern file / 임시 패턴 파일의 경로
        
    Note:
        - Creates a JSON file with sample patterns / 샘플 패턴이 포함된 JSON 파일 생성
        - Includes patterns for all risk levels / 모든 위험도 레벨의 패턴 포함
    """
    pattern_data = {
        "patterns": {
            "HIGH": [
                {
                    "name": "RRN",
                    "pattern": "(?:[0-9]{2}(?:0[1-9]|1[0-2])(?:0[1-9]|[1,2][0-9]|3[0,1]))-[1-4][0-9]{6}",
                    "description": "RRN Pattern (YYMMDD-XXXXXXX)"
                },
                {
                    "name": "BIN",
                    "pattern": "(?:4[0-9]{12}(?:[0-9]{3})?|5[1-5][0-9]{14}|3[47][0-9]{13}|3(?:0[0-5]|[68][0-9])[0-9]{11})",
                    "description": "BIN Pattern"
                }
            ],
            "MEDIUM": [
                {
                    "name": "Phone Number",
                    "pattern": "01[016789]-?\\d{3,4}-?\\d{4}",
                    "description": "Korea Phone number Pattern"
                }
            ],
            "LOW": [
                {
                    "name": "Email",
                    "pattern": "[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}",
                    "description": "Email Pattern"
                }
            ]
        }
    }
    
    pattern_file = tmp_path / "test_patterns.json"
    with pattern_file.open("w", encoding="utf-8") as f:
        json.dump(pattern_data, f, ensure_ascii=False, indent=2)
    
    return pattern_file

def test_risk_level_enum():
    """Test RiskLevel enumeration values. / RiskLevel 열거형 값을 테스트합니다.
    
    Verification Items / 검증 항목:
        1. Verify HIGH risk level value / HIGH 위험도 값 검증
        2. Verify MEDIUM risk level value / MEDIUM 위험도 값 검증
        3. Verify LOW risk level value / LOW 위험도 값 검증
        4. Verify total number of risk levels / 전체 위험도 레벨 수 검증
    """
    assert RiskLevel.HIGH.value == "HIGH"
    assert RiskLevel.MEDIUM.value == "MEDIUM"
    assert RiskLevel.LOW.value == "LOW"
    assert len(RiskLevel) == 3

def test_data_pattern_creation():
    """Test DataPattern class instantiation. / DataPattern 클래스 인스턴스 생성을 테스트합니다.
    
    Verification Items / 검증 항목:
        1. Verify pattern name assignment / 패턴 이름 할당 검증
        2. Verify regex pattern assignment / 정규식 패턴 할당 검증
        3. Verify risk level assignment / 위험도 레벨 할당 검증
        4. Verify description assignment / 설명 할당 검증
    """
    pattern = DataPattern(
        name = "Test Pattern",
        pattern = r"\d+",
        risk_level = RiskLevel.HIGH,
        description = "Test pattern description"
    )

    assert pattern.name == "Test Pattern"
    assert pattern.pattern == r"\d+"
    assert pattern.risk_level == RiskLevel.HIGH
    assert pattern.description == "Test pattern description"

def test_pattern_loader_with_valid_file(sample_pattern_file):
    """Test pattern loading with valid JSON file. / 유효한 JSON 파일에서 패턴 로딩을 테스트합니다.
    
    Args:
        sample_pattern_file: Path to test pattern file / 테스트 패턴 파일 경로

    Verification Items / 검증 항목:
        1. Verify total number of patterns loaded / 로드된 전체 패턴 수 검증
        2. Verify each pattern is DataPattern instance / 각 패턴이 DataPattern 인스턴스인지 검증
        3. Verify required attributes exist / 필수 속성 존재 여부 검증
        4. Verify risk level types / 위험도 레벨 타입 검증
    """
    patterns = PatternLoader.load_patterns(str(sample_pattern_file))

    assert len(patterns) == 4

    for pattern in patterns:
        assert isinstance(pattern, DataPattern)
        assert pattern.name
        assert pattern.pattern
        assert isinstance(pattern.risk_level, RiskLevel)
        assert pattern.description

def test_pattern_loader_with_invalid_file():
    """Test exception handling for invalid file path. / 잘못된 파일 경로에 대한 예외 처리를 테스트합니다.
    
    Verification Items / 검증 항목:
        1. Verify FileNotFoundError is raised / FileNotFoundError 발생 여부 검증
        2. Verify error message content / 에러 메시지 내용 검증
    
    Expected Behavior / 예상 동작:
        - Should raise FileNotFoundError for non-existent file / 존재하지 않는 파일에 대해 FileNotFoundError 발생
    """
    with pytest.raises(FileNotFoundError) as exc_info:
        PatternLoader.load_patterns("non_existent_file.json")
    
    assert "Not found Pattern file" in str(exc_info.value)

def test_pattern_loader_with_invalid_json(tmp_path):
    """Test exception handling for invalid JSON format. / 잘못된 JSON 형식에 대한 예외 처리를 테스트합니다.
    
    Args:
        tmp_path: Temporary directory path from pytest / pytest의 임시 디렉토리 경로

    Verification Items / 검증 항목:
        1. Verify JSONDecodeError is raised / JSONDecodeError 발생 여부 검증
    
    Expected Behavior / 예상 동작:
        - Should raise JSONDecodeError for invalid JSON format / 잘못된 JSON 형식에 대해 JSONDecodeError 발생
    """
    invalid_file = tmp_path / "invalid.json"
    invalid_file.write_text("{invalid json", encoding="utf-8")

    with pytest.raises(json.JSONDecodeError):
        PatternLoader.load_patterns(str(invalid_file))