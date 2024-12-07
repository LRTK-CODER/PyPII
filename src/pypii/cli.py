"""
PyPII CLI Interface

Command-line interface for detecting Personally Identifiable Information (PII).
This module provides a command-line tool for scanning files and directories for PII.

PyPII CLI 인터페이스

개인식별정보(PII) 검출을 위한 명령줄 인터페이스입니다.
이 모듈은 파일과 디렉토리에서 PII를 검사하기 위한 명령줄 도구를 제공합니다.

Usage example / 사용 예시:
    pypii scan /path/to/scan --pattern-file patterns.json --output report.json
"""

import argparse
import logging
from pathlib import Path
from typing import List
from .scanner.file_scanner import FileScanner
from .detector.pii_detector import PIIDetector
from .report.generator import ReportGenerator

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def create_parser() -> argparse.ArgumentParser:
    """
    Create command line argument parser.
    
    Returns:
        ArgumentParser object configured with PII detection tool options:
        - path: Path to file or directory to scan
        - pattern-file: Path to pattern definition file
        - output: Path to output report file
        - format: Report format (json/csv)
        - verbose: Enable detailed logging

    명령줄 인자 파서를 생성합니다.

    Returns:
        PII 검출 도구 옵션이 설정된 ArgumentParser 객체:
        - path: 스캔할 파일 또는 디렉토리 경로
        - pattern-file: 패턴 정의 파일 경로
        - output: 결과 리포트 파일 경로
        - format: 리포트 형식 (json/csv)
        - verbose: 상세 로깅 활성화
    """
    parser = argparse.ArgumentParser(
        description="PII(개인식별정보) 검출 도구 / PII(Personally Identifiable Information) Detection Tool",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument(
        "path",
        help="스캔할 파일 또는 디렉토리 경로 / Path to file or directory to scan"
    )
    
    parser.add_argument(
        "-p", "--pattern-file",
        default="patterns.json",
        help="PII 패턴 정의 파일 경로 (기본값: patterns.json) / Path to PII pattern definition file (default: patterns.json)"
    )
    
    parser.add_argument(
        "-o", "--output",
        default="pii_report.json",
        help="결과 리포트 파일 경로 (기본값: pii_report.json) / Path to output report file (default: pii_report.json)"
    )
    
    parser.add_argument(
        "-f", "--format",
        choices=["json", "csv"],
        default="json",
        help="리포트 형식 (기본값: json) / Report format (default: json)"
    )
    
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="상세 로깅 활성화 / Enable verbose logging"
    )
    
    return parser

def scan_files(path: str, pattern_file: str) -> List[Path]:
    """
    Execute file scanning for PII detection.

    Args:
        path: Path to file or directory to scan
        pattern_file: Path to PII pattern definition file

    Returns:
        ReportGenerator object containing scan results and statistics

    파일 스캔을 실행하여 PII를 검출합니다.

    Args:
        path: 스캔할 파일 또는 디렉토리 경로
        pattern_file: PII 패턴 정의 파일 경로

    Returns:
        스캔 결과와 통계가 포함된 ReportGenerator 객체
    """
    scanner = FileScanner()
    detector = PIIDetector(pattern_file)
    report_gen = ReportGenerator()
    
    logger.info(f"스캔 시작: {path}")
    
    target_path = Path(path)
    if target_path.is_file():
        files = [target_path]
    else:
        files = list(scanner.scan_directory(path))
        
    logger.info(f"검사할 파일 수: {len(files)}")
    
    for file in files:
        try:
            logger.debug(f"파일 검사 중: {file}")
            results = detector.detect_file(str(file))
            if results:
                report_gen.add_results(results, file)
                logger.info(f"발견된 PII - {file}: {len(results)}개")
        except Exception as e:
            logger.error(f"파일 처리 중 오류 발생 - {file}: {str(e)}")
            
    return report_gen

def main():
    """
    Main execution function for the CLI application.
    
    This function:
    - Parses command line arguments
    - Executes file scanning
    - Generates and saves the report
    - Displays summary information
    
    Returns:
        0 for successful execution, 1 for errors

    메인 실행 함수입니다.
    
    이 함수는:
    - 명령줄 인자를 파싱
    - 파일 스캔을 실행
    - 리포트 생성 및 저장
    - 요약 정보 출력
    
    Returns:
        정상 실행 시 0, 오류 발생 시 1
    """
    parser = create_parser()
    args = parser.parse_args()
    
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    try:
        report_gen = scan_files(args.path, args.pattern_file)
        
        # 결과 저장
        if args.format == "json":
            report_gen.save_json(args.output)
        else:
            report_gen.save_csv(args.output)
            
        logger.info(f"리포트 생성 완료: {args.output}")
        
        # 요약 정보 출력
        summary = report_gen.generate_summary()
        print("\n=== 검사 결과 요약 ===")
        print(f"검사한 파일 수: {summary.total_files}")
        print(f"발견된 PII 수: {summary.total_detections}")
        print("\n위험도별 발견 수:")
        for level, count in summary.risk_level_counts.items():
            print(f"- {level}: {count}")
            
    except Exception as e:
        logger.error(f"실행 중 오류 발생: {str(e)}")
        return 1
        
    return 0

if __name__ == "__main__":
    exit(main())