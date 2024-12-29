import os
import pytest
import logging
from src.utils.logger import setup_logger

@pytest.fixture
def temp_log_file(tmp_path):
    """테스트용 임시 로그 파일을 생성하는 fixture
    
    Args:
        tmp_path: pytest에서 제공하는 임시 디렉토리 경로

    Returns:
        str: 임시 로그 파일의 전체 경로
        
    Note:
        - 테스트 실행마다 새로운 임시 파일이 생성됨
        - 테스트 종료 후 자동으로 삭제됨
    """
    return str(tmp_path / "test.log")

def test_setup_logger_basic():
    """기본 로거 설정에 대한 테스트
    
    검증 항목:
        1. 로거가 logging.Logger 인스턴스인지 확인
        2. 로거 이름이 올바르게 설정되었는지 확인
        3. 기본 로그 레벨이 INFO로 설정되었는지 확인
        4. 정확히 하나의 핸들러가 설정되었는지 확인
        5. 해당 핸들러가 StreamHandler 타입인지 확인
    """
    logger = setup_logger(name="test")
    assert isinstance(logger, logging.Logger)
    assert logger.name == "test"
    assert logger.level == logging.INFO
    assert len(logger.handlers) == 1
    assert isinstance(logger.handlers[0], logging.StreamHandler)

def test_setup_logger_with_custom_level():
    """사용자 정의 로그 레벨 설정 테스트
    
    검증 항목:
        - DEBUG 레벨로 설정 시 로거의 레벨이 정확히 DEBUG로 설정되는지 확인
    """
    logger = setup_logger(name="test", log_level="DEBUG")
    assert logger.level == logging.DEBUG

def test_setup_logger_with_file(temp_log_file):
    """파일 로깅 기능 테스트
    
    Args:
        temp_log_file: pytest fixture로 생성된 임시 로그 파일 경로

    검증 항목:
        1. 로그 파일이 실제로 생성되는지 확인
        2. 로그 메시지가 파일에 정확히 기록되는지 확인
        3. 파일이 UTF-8로 올바르게 인코딩되는지 확인
    """
    logger = setup_logger(name="test", log_file=temp_log_file)
    test_message = "Test log message"
    logger.info(test_message)

    assert os.path.exists(temp_log_file)
    with open(temp_log_file, "r", encoding="utf-8") as f:
        log_content = f.read()
        assert test_message in log_content

def test_setup_logger_with_invalid_level():
    """잘못된 로그 레벨 입력 시 예외 처리 테스트
    
    검증 항목:
        - 잘못된 로그 레벨 문자열 입력 시 AttributeError가 발생하는지 확인
    
    예상 동작:
        - 'INVALID_LEVEL'과 같은 잘못된 로그 레벨 입력 시 AttributeError 발생
    """
    with pytest.raises(AttributeError):
        setup_logger(name="test", log_level="INVALID_LEVEL")

def test_setup_logger_creates_log_directory(temp_log_file):
    """로그 디렉토리 자동 생성 기능 테스트
    
    Args:
        temp_log_file: pytest fixture로 생성된 임시 로그 파일 경로

    검증 항목:
        1. 중첩된 디렉토리 구조가 자동으로 생성되는지 확인
        2. 생성된 경로에 로그 파일이 정상적으로 생성되는지 확인
    
    Note:
        - 여러 단계의 하위 디렉토리가 한 번에 생성되는지 테스트
    """
    nested_log_path = os.path.join(os.path.dirname(temp_log_file), "nested", "path", "test.log")
    logger = setup_logger(name="test_logger", log_file=nested_log_path)
    logger.info("test")
    assert os.path.exists(nested_log_path)