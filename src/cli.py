"""
PyPII CLI 인터페이스

개인식별정보(PII) 검출을 위한 명령줄 인터페이스입니다.

사용 예시:
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
    """명령줄 인자 파서 생성"""
    parser = argparse.ArgumentParser(
        description="개인식별정보(PII) 검출 도구",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument(
        "path",
        help="스캔할 파일 또는 디렉토리 경로"
    )
    
    parser.add_argument(
        "-p", "--pattern-file",
        default="patterns.json",
        help="PII 패턴 정의 파일 경로 (기본값: patterns.json)"
    )
    
    parser.add_argument(
        "-o", "--output",
        default="pii_report.json",
        help="결과 리포트 파일 경로 (기본값: pii_report.json)"
    )
    
    parser.add_argument(
        "-f", "--format",
        choices=["json", "csv"],
        default="json",
        help="리포트 형식 (기본값: json)"
    )
    
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="상세 로깅 활성화"
    )
    
    return parser

def scan_files(path: str, pattern_file: str) -> List[Path]:
    """파일 스캔 실행"""
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
    """메인 실행 함수"""
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