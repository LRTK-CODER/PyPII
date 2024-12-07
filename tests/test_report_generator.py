"""ReportGenerator 테스트"""

import pytest
import json
import csv
from pathlib import Path
from datetime import datetime
from src.report.generator import ReportGenerator
from src.detector.pii_detector import DetectionResult

@pytest.fixture
def sample_results():
    """테스트용 샘플 검출 결과"""
    return [
        DetectionResult(
            pattern_name="주민등록번호",
            matched_text="950101-1234567",
            start_pos=0,
            end_pos=14,
            risk_level="HIGH",
            line_number=1,
            context="주민번호는 950101-1234567 입니다",
            file_path=None
        ),
        DetectionResult(
            pattern_name="휴대폰번호",
            matched_text="010-1234-5678",
            start_pos=0,
            end_pos=13,
            risk_level="MEDIUM",
            line_number=2,
            context="전화번호는 010-1234-5678 입니다",
            file_path=None
        )
    ]

def test_report_generator_init():
    """ReportGenerator 초기화 테스트"""
    generator = ReportGenerator()
    assert len(generator.results) == 0
    assert len(generator.scanned_files) == 0

def test_add_results(sample_results):
    """결과 추가 테스트"""
    generator = ReportGenerator()
    generator.add_results(sample_results, Path("test.txt"))
    
    assert len(generator.results) == 2
    assert len(generator.scanned_files) == 1

def test_generate_summary(sample_results):
    """요약 생성 테스트"""
    generator = ReportGenerator()
    generator.add_results(sample_results, Path("test.txt"))
    
    summary = generator.generate_summary()
    assert summary.total_files == 1
    assert summary.total_detections == 2
    assert summary.risk_level_counts == {"HIGH": 1, "MEDIUM": 1}
    assert summary.pattern_counts == {"주민등록번호": 1, "휴대폰번호": 1}

def test_save_json(sample_results, tmp_path):
    """JSON 저장 테스트"""
    output_file = tmp_path / "report.json"
    
    generator = ReportGenerator()
    generator.add_results(sample_results, Path("test.txt"))
    generator.save_json(str(output_file))
    
    assert output_file.exists()
    with open(output_file, 'r', encoding='utf-8') as f:
        report = json.load(f)
        assert 'summary' in report
        assert 'detections' in report

def test_save_csv(sample_results, tmp_path):
    """CSV 저장 테스트"""
    output_file = tmp_path / "report.csv"
    
    generator = ReportGenerator()
    generator.add_results(sample_results, Path("test.txt"))
    generator.save_csv(str(output_file))
    
    assert output_file.exists()
    with open(output_file, 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        headers = next(reader)  # 헤더 읽기
        assert len(headers) == 6  # 예상되는 컬럼 수
        rows = list(reader)
        assert len(rows) == 2  # 예상되는 행 수