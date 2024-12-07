"""
File System Scanner Module

This module recursively scans directories to find supported files.
File types are determined based on MIME types.

파일 시스템 스캐너 모듈

이 모듈은 지정된 디렉토리를 재귀적으로 스캔하여 지원되는 파일들을 찾습니다.
파일 타입은 MIME 타입을 기반으로 판단됩니다.

Usage example / 사용 예시:
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
    """
    Class for scanning file system and detecting file types
    파일 시스템을 스캔하고 파일 타입을 감지하는 클래스
    """
    
    def __init__(self, supported_types: Set[str] = None):
        """
        Initialize FileScanner

        Args:
            supported_types: Set of supported MIME types
                           Default: text/plain, application/pdf

        FileScanner 초기화

        Args:
            supported_types: 지원하는 MIME 타입 집합
                           기본값: text/plain, application/pdf
        """
        self.supported_types = supported_types or {
            'text/plain',
            'application/pdf',
            'application/vnd.openxmlformats-officedocument.wordprocessingml.document',  # docx
            'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',  # xlsx
            'application/msword' # doc
        }
        
    def scan_directory(self, path: str) -> Generator[Path, None, None]:
        """
        Recursively scan directory to find supported files.

        Args:
            path: Directory path to scan

        Yields:
            Path objects of supported files

        Raises:
            FileNotFoundError: When directory is not found

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
        Check if the file is of a supported type.

        Args:
            file_path: Path to the file to check

        Returns:
            True if the file is supported, False otherwise

        파일이 지원되는 타입인지 확인합니다.

        Args:
            file_path: 확인할 파일 경로

        Returns:
            지원되는 파일이면 True, 아니면 False
        """
        try:
            # 파일 확장자 먼저 확인
            if file_path.suffix.lower() == '.docx':
                logger.debug(f"DOCX 파일 감지됨: {file_path}")
                return True
                
            # MIME 타입 확인
            mime = magic.from_file(str(file_path), mime=True)
            logger.debug(f"파일 MIME 타입: {mime} - {file_path}")
            
            is_supported = mime in self.supported_types
            if is_supported:
                logger.debug(f"지원되는 파일 타입: {file_path}")
            else:
                logger.debug(f"지원되지 않는 파일 타입: {file_path} ({mime})")
                
            return is_supported
            
        except Exception as e:
            logger.error(f"MIME 타입 감지 실패: {file_path} - {str(e)}")
            return False
        