"""
PII Detection Report Generation Module

This module generates reports in various formats (JSON, CSV, HTML) from PII detection results.
The reports include information about detected PII patterns, their locations, patterns, and risk levels.

PII 검출 결과 리포트 생성 모듈

이 모듈은 PII 검출 결과를 다양한 형식(JSON, CSV, HTML)의 리포트로 생성합니다.
검출된 PII 정보의 위치, 패턴, 위험도 등을 포함합니다.

Usage example / 사용 예시:
    generator = ReportGenerator()
    generator.add_results(detection_results)
    generator.save_json("report.json")
"""

import json
import csv
from pathlib import Path
from typing import List, Dict
from datetime import datetime
from dataclasses import dataclass, asdict
from ..detector.pii_detector import DetectionResult

@dataclass
class ScanSummary:
    """
    Summary information of scan results
    스캔 결과 요약 정보
    """
    total_files: int
    total_detections: int
    risk_level_counts: Dict[str, int]
    pattern_counts: Dict[str, int]
    scan_time: str

class ReportGenerator:
    """
    Class for generating PII detection reports
    PII 검출 결과 리포트 생성 클래스
    """
    
    def __init__(self):
        """
        Initialize ReportGenerator
        ReportGenerator 초기화
        """
        self.results: List[DetectionResult] = []
        self.scanned_files: List[Path] = []
        
    def add_results(self, results: List[DetectionResult], file_path: Path = None):
        """
        Add detection results to the report.

        Args:
            results: List of DetectionResult objects
            file_path: Path to the scanned file (optional)

        검출 결과 추가

        Args:
            results: DetectionResult 객체들의 리스트
            file_path: 검사한 파일 경로 (선택사항)
        """
        self.results.extend(results)
        if file_path:
            self.scanned_files.append(file_path)
            
    def generate_summary(self) -> ScanSummary:
        """
        Generate a summary of scan results including total files, detections, and pattern statistics.

        Returns:
            ScanSummary object containing the summarized information

        스캔 결과 요약 생성 - 총 파일 수, 검출 수, 패턴 통계 등을 포함

        Returns:
            요약 정보가 포함된 ScanSummary 객체
        """
        risk_counts = {}
        pattern_counts = {}
        
        for result in self.results:
            risk_counts[result.risk_level] = risk_counts.get(result.risk_level, 0) + 1
            pattern_counts[result.pattern_name] = pattern_counts.get(result.pattern_name, 0) + 1
            
        return ScanSummary(
            total_files=len(self.scanned_files),
            total_detections=len(self.results),
            risk_level_counts=risk_counts,
            pattern_counts=pattern_counts,
            scan_time=datetime.now().isoformat()
        )
    
    def save_json(self, output_path: str):
        """
        Save report in JSON format.

        Args:
            output_path: Path to save the report file

        JSON 형식으로 리포트 저장

        Args:
            output_path: 저장할 파일 경로
        """
        report = {
            'summary': asdict(self.generate_summary()),
            'detections': [
                {
                    'file': str(file),  # Convert Path to string
                    'results': [
                        {
                            **asdict(r),
                            'file_path': str(r.file_path) if r.file_path else None  # Convert Path to string
                        } 
                        for r in results
                    ]
                }
                for file, results in self._group_by_file().items()
            ]
        }
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)

    def save_csv(self, output_path: str):
        """
        Save report in CSV format.

        Args:
            output_path: Path to save the report file

        CSV 형식으로 리포트 저장

        Args:
            output_path: 저장할 파일 경로
        """
        with open(output_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            # Write header
            writer.writerow([
                'File', 'Pattern', 'Matched Text', 'Risk Level', 
                'Line Number', 'Start Position', 'End Position', 'Context'
            ])
            
            # Write detection results
            for file, results in self._group_by_file().items():
                for r in results:
                    writer.writerow([
                        str(file),
                        r.pattern_name,
                        r.matched_text,
                        r.risk_level,
                        r.line_number,
                        r.start_pos,
                        r.end_pos,
                        r.context
                    ])
                    
    def _group_by_file(self) -> Dict[Path, List[DetectionResult]]:
        """
        Group detection results by their source files.

        Returns:
            Dictionary with file paths as keys and lists of DetectionResult objects as values.
            Unknown source files are grouped under 'unknown' path.

        결과를 파일별로 그룹화합니다.

        Returns:
            파일 경로를 키로 하고 DetectionResult 객체들의 리스트를 값으로 하는 딕셔너리.
            출처를 알 수 없는 파일은 'unknown' 경로로 그룹화됩니다.
        """
        grouped = {}
        for result in self.results:
            file_path = result.file_path or Path('unknown')
            if file_path not in grouped:
                grouped[file_path] = []
            grouped[file_path].append(result)
        return grouped