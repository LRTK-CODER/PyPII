"""
PII 검출 결과 리포트 생성 모듈

이 모듈은 PII 검출 결과를 다양한 형식(JSON, CSV, HTML)의 리포트로 생성합니다.
검출된 PII 정보의 위치, 패턴, 위험도 등을 포함합니다.

사용 예시:
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
    """스캔 결과 요약 정보"""
    total_files: int
    total_detections: int
    risk_level_counts: Dict[str, int]
    pattern_counts: Dict[str, int]
    scan_time: str

class ReportGenerator:
    """PII 검출 결과 리포트 생성 클래스"""
    
    def __init__(self):
        """ReportGenerator 초기화"""
        self.results: List[DetectionResult] = []
        self.scanned_files: List[Path] = []
        
    def add_results(self, results: List[DetectionResult], file_path: Path = None):
        """
        검출 결과 추가

        Args:
            results: DetectionResult 객체들의 리스트
            file_path: 검사한 파일 경로 (선택사항)
        """
        self.results.extend(results)
        if file_path:
            self.scanned_files.append(file_path)
            
    def generate_summary(self) -> ScanSummary:
        """스캔 결과 요약 생성"""
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
        JSON 형식으로 리포트 저장

        Args:
            output_path: 저장할 파일 경로
        """
        report = {
            'summary': asdict(self.generate_summary()),
            'detections': [
                {
                    'file': str(file),
                    'results': [asdict(r) for r in results]
                }
                for file, results in self._group_by_file().items()
            ]
        }
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
            
    def save_csv(self, output_path: str):
        """
        CSV 형식으로 리포트 저장

        Args:
            output_path: 저장할 파일 경로
        """
        with open(output_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['File', 'Pattern', 'Risk Level', 'Line Number', 'Matched Text', 'Context'])
            
            for file, results in self._group_by_file().items():
                for r in results:
                    writer.writerow([
                        str(file),
                        r.pattern_name,
                        r.risk_level,
                        r.line_number,
                        r.matched_text,
                        r.context
                    ])
                    
    def _group_by_file(self) -> Dict[Path, List[DetectionResult]]:
        """결과를 파일별로 그룹화"""
        grouped = {}
        for result in self.results:
            file_path = result.file_path or Path('unknown')
            if file_path not in grouped:
                grouped[file_path] = []
            grouped[file_path].append(result)
        return grouped