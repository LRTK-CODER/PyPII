"""
파일 시스템 스캐닝 모듈

이 모듈은 지정된 디렉토리를 재귀적으로 스캔하여 지원되는 파일들을 찾습니다.
파일 타입은 MIME 타입을 기반으로 판단됩니다.

사용 예시:
    scanner = FileScanner()
    for file_path in scanner.scan_directory("/path/to/scan"):
        print(f"Found file: {file_path}")
"""

from pathlib import Path
from typing import Generator, List, Set
import magic
import logging

logger = logging.getLogger(__name__)

class FileScanner:
    """파일 시스템을 스캔하고 파일 타입을 감지하는 클래스"""
    
    def __init__(self, supported_types: Set[str] = None):
        """
        FileScanner 초기화

        Args:
            supported_types: 지원하는 MIME 타입 집합
                           기본값: text/plain, application/pdf
        """
        self.supported_types = supported_types or {
            'text/plain',
            'application/pdf',
            'application/vnd.openxmlformats-officedocument.wordprocessingml.document',  # docx
            'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'  # xlsx
        }
        
    def scan_directory(self, path: str) -> Generator[Path, None, None]:
        """
        디렉토리를 재귀적으로 스캔하여 지원되는 파일들을 찾습니다.

        Args:
            path: 스캔할 디렉토리 경로

        Yields:
            지원되는 파일들의 Path 객체

        Raises:
            FileNotFoundError: 디렉토리를 찾을 수 없는 경우
        """
        root_path = Path(path)
        if not root_path.exists():
            raise FileNotFoundError(f"디렉토리를 찾을 수 없습니다: {path}")
            
        logger.info(f"스캔 시작: {path}")
        for file_path in root_path.rglob("*"):
            if file_path.is_file():
                try:
                    if self._is_supported_file(file_path):
                        logger.debug(f"지원되는 파일 발견: {file_path}")
                        yield file_path
                except Exception as e:
                    logger.warning(f"파일 처리 중 오류 발생: {file_path} - {str(e)}")
                    
    def _is_supported_file(self, file_path: Path) -> bool:
        """
        파일이 지원되는 타입인지 확인합니다.

        Args:
            file_path: 확인할 파일 경로

        Returns:
            지원되는 파일이면 True, 아니면 False
        """
        try:
            mime = magic.from_file(str(file_path), mime=True)
            return mime in self.supported_types
        except Exception as e:
            logger.error(f"MIME 타입 감지 실패: {file_path} - {str(e)}")
            return False
        