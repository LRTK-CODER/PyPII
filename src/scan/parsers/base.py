from abc import ABC, abstractmethod
from typing import Optional, List
from pathlib import Path

from ..pattern import DataPattern
from ...utils.logger import setup_logger


class BaseParser(ABC):
    """
    Base class for file parsers. / 파일 파서를 위한 기본 클래스
    """
    
    def __init__(self, patterns: List[DataPattern]):
        """Initialize parser with PII patterns. / 개인정보 패턴 파서를 초기화합니다.

        Args:
            patterns (List[DataPattern]): List of PII patterns to detect / 감지할 개인정보 패턴 리스트
        """
        self.patterns = patterns
        self.logger = setup_logger(f"{self.__class__.__name__}")
        
    @abstractmethod
    def extract_text(self, file_path: Path) -> Optional[str]:
        """
        Extract text content from file. / 파일에서 텍스트 내용을 추출합니다.

        Args:
            file_path (Path): Path to the file / 파일 경로

        Returns:
            Optional[str]: Extracted text or None if extraction fails / 추출된 텍스트 또는 실패 시 None
        """
        pass
    
    @abstractmethod
    def can_handle(self, file_path: Path) -> bool:
        """
        Check if parser can handle the given file. / 주어진 파일을 처리할 수 있는지 확인합니다.

        Args:
            file_path (Path): Path to the file / 파일 경로

        Returns:
            bool: True if parser can handle the file, False otherwise / 파일을 처리할 수 있으면 True, 그렇지 않으면 False
        """
        pass
    
    def scan(self, file_path: Path) -> List[dict]:
        """
        Scan file for PII patterns. / 파일에서 PII 패턴을 검사합니다.

        Args:
            file_path (Path): Path to the file / 파일 경로

        Returns:
            List[dict]: List of detected PII instances with pattern info / 감지된 PII 정보와 패턴 정보를 포함한 리스트
        """
        text = self.extract_text(file_path)
        if not text:
            self.logger.warning(f"Failed to extract text from {file_path}")
            return []
        
        results = []
        for pattern in self.patterns:
            #TODO: Implement pattern matching logic
            pass
        
        return results
        
    
    