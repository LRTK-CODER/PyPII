"""FileScanner 테스트"""

import pytest
from pathlib import Path
import tempfile
import magic
from src.scanner.file_scanner import FileScanner

@pytest.fixture
def temp_dir():
    """테스트용 임시 디렉토리 생성"""
    with tempfile.TemporaryDirectory() as tmpdirname:
        yield Path(tmpdirname)

@pytest.fixture
def sample_files(temp_dir):
    """테스트용 샘플 파일 생성"""
    # 텍스트 파일 생성
    text_file = temp_dir / "test.txt"
    text_file.write_text("This is a test file")
    
    # PDF 파일 모사
    pdf_file = temp_dir / "test.pdf"
    pdf_file.write_bytes(b'%PDF-1.4')
    
    # Excel 파일 생성
    excel_file = temp_dir / "test.xlsx"
    excel_file.write_bytes(b'PK\x03\x04')
    
    # 지원하지 않는 파일들 생성
    binary_file = temp_dir / "test.bin"
    binary_file.write_bytes(b'\x00\x01\x02\x03')
    
    # 숨김 파일 생성
    hidden_file = temp_dir / ".hidden.txt"
    hidden_file.write_text("hidden content")
    
    return temp_dir

def test_file_scanner_init():
    """FileScanner 초기화 테스트"""
    scanner = FileScanner()
    assert 'text/plain' in scanner.supported_types
    
    custom_types = {'application/pdf'}
    scanner = FileScanner(supported_types=custom_types)
    assert scanner.supported_types == custom_types

def test_scan_directory(sample_files):
    """디렉토리 스캔 테스트"""
    scanner = FileScanner()
    files = list(scanner.scan_directory(str(sample_files)))
    
    # 지원되는 파일만 감지되어야 함
    assert len(files) > 0
    # 파일 이름으로 검증
    file_names = [f.name for f in files]
    assert "test.txt" in file_names
    assert "test.bin" not in file_names

def test_scan_nonexistent_directory():
    """존재하지 않는 디렉토리 스캔 테스트"""
    scanner = FileScanner()
    with pytest.raises(FileNotFoundError):
        list(scanner.scan_directory("/nonexistent/path"))

def test_custom_file_types():
    """사용자 정의 파일 타입 테스트"""
    custom_types = {'application/pdf', 'application/xml'}
    scanner = FileScanner(supported_types=custom_types)
    assert scanner.supported_types == custom_types
    assert 'text/plain' not in scanner.supported_types

def test_empty_directory(temp_dir):
    """빈 디렉토리 스캔 테스트"""
    scanner = FileScanner()
    files = list(scanner.scan_directory(str(temp_dir)))
    assert len(files) == 0

def test_nested_directory_scan(temp_dir):
    """중첩 디렉토리 스캔 테스트"""
    # 중첩 디렉토리 생성
    nested_dir = temp_dir / "nested" / "deep"
    nested_dir.mkdir(parents=True)
    
    # 중첩 디렉토리에 파일 생성
    test_file = nested_dir / "nested.txt"
    test_file.write_text("nested content")
    
    scanner = FileScanner()
    files = list(scanner.scan_directory(str(temp_dir)))
    
    assert len(files) == 1
    assert files[0].name == "nested.txt"

def test_invalid_file_handling(temp_dir):
    """손상된 파일 처리 테스트"""
    # 권한이 없는 파일 생성 (Unix 시스템에서만 동작)
    import os
    import sys
    
    if sys.platform != "win32":
        no_access_file = temp_dir / "no_access.txt"
        no_access_file.write_text("restricted content")
        os.chmod(str(no_access_file), 0o000)
        
        scanner = FileScanner()
        files = list(scanner.scan_directory(str(temp_dir)))
        assert len(files) == 0