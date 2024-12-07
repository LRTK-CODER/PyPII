"""CLI 인터페이스 테스트"""

import pytest
from pathlib import Path
import tempfile
import json
import os
from src.cli import create_parser, scan_files

@pytest.fixture
def sample_files():
    """테스트용 임시 파일 생성"""
    with tempfile.TemporaryDirectory() as tmpdir:
        # 패턴 파일 생성
        pattern_file = Path(tmpdir) / "patterns.json"
        patterns = {
            "patterns": {
                "HIGH": [
                    {
                        "name": "주민등록번호",
                        "pattern": r"\d{6}-[1-4]\d{6}",
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
        pattern_file.write_text(json.dumps(patterns, ensure_ascii=False))
        
        # 테스트 파일들 생성
        test_files = {
            "test1.txt": "주민번호는 950101-1234567 입니다",
            "test2.txt": "전화번호는 010-1234-5678 입니다",
            "test3.txt": "일반 텍스트 파일입니다",
            "nested/test4.txt": "중첩된 주민번호 950101-1234567"
        }
        
        for file_path, content in test_files.items():
            file = Path(tmpdir) / file_path
            file.parent.mkdir(parents=True, exist_ok=True)
            file.write_text(content)
        
        yield tmpdir, pattern_file

def test_scan_single_file(sample_files):
    """단일 파일 스캔 테스트"""
    tmpdir, pattern_file = sample_files
    test_file = Path(tmpdir) / "test1.txt"
    
    report_gen = scan_files(str(test_file), str(pattern_file))
    summary = report_gen.generate_summary()
    
    assert summary.total_files == 1
    assert summary.total_detections == 1
    assert summary.risk_level_counts["HIGH"] == 1

def test_scan_directory(sample_files):
    """디렉토리 스캔 테스트"""
    tmpdir, pattern_file = sample_files
    
    report_gen = scan_files(str(tmpdir), str(pattern_file))
    summary = report_gen.generate_summary()
    
    assert summary.total_files > 1
    assert summary.total_detections >= 2
    assert "HIGH" in summary.risk_level_counts
    assert "MEDIUM" in summary.risk_level_counts

def test_cli_arguments():
    """CLI 인자 파싱 테스트"""
    parser = create_parser()
    
    # 기본 인자 테스트
    args = parser.parse_args(["test_path"])
    assert args.path == "test_path"
    assert args.pattern_file == "patterns.json"
    assert args.output == "pii_report.json"
    assert args.format == "json"
    assert not args.verbose
    
    # 모든 옵션 지정 테스트
    args = parser.parse_args([
        "test_path",
        "-p", "custom_patterns.json",
        "-o", "custom_report.csv",
        "-f", "csv",
        "-v"
    ])
    assert args.path == "test_path"
    assert args.pattern_file == "custom_patterns.json"
    assert args.output == "custom_report.csv"
    assert args.format == "csv"
    assert args.verbose

def test_invalid_path(sample_files):
    """존재하지 않는 경로 테스트"""
    tmpdir, pattern_file = sample_files
    
    with pytest.raises(FileNotFoundError):
        scan_files("/invalid/path", str(pattern_file))