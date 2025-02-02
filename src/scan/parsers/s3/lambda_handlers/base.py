from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional

from src.scan.pattern import DataPattern
from src.utils.logger import setup_logger

class LambdaBaseParser(ABC):
    """
    Base class for Lambda-based S3 file parsers / Lambda 기반 S3 파일 파서를 위한 기본 클래스
    """
    
    def __init__(self, patterns: List[DataPattern]):
        """Initialize parser with PII patterns. / 개인정보 패턴으로 파서를 초기화합니다.

        Args:
            patterns (List[DataPattern]): List of PII patterns to detect / 감지할 PII 패턴 리스트
        """
        self.patterns = patterns
        self.logger = setup_logger(f"{self.__class__.__name__}")
        
    @abstractmethod
    def can_handle(self, event: Dict[str, Any]) -> bool:
        """
        Check if parser can handle the S3 event. / S3 이벤트를 처리할 수 있는지 확인합니다.

        Args:
            event (Dict[str, Any]): Lambda S3 event dictionary / Lambda S3 이벤트 딕셔너리

        Returns:
            bool: True if parser can handle the event, False otherwise / 이벤트를 처리할 수 있으면 True, 그렇지 않으면 False
        """
        pass
    
    @abstractmethod
    def extract_text(self, event: Dict[str, Any]) -> Optional[str]:
        """
        Extract text content from S3 object. / S3 객체에서 텍스트를 추출합니다.

        Args:
            event (Dict[str, Any]): Lambda S3 event dictionary / Lambda S3 이벤트 딕셔너리

        Returns:
            Optional[str]: Extracted text or None if extraction fails / 추출된 텍스트 또는 실패 시 None
        """
        pass
    
    def scan(self, event: Dict[str, Any]) -> List[dict]:
        """
        Scan S3 object for PII patterns. / S3 객체에서 개인정보 패턴을 검사합니다.

        Args:
            event (Dict[str, Any]): Lambda S3 event dictionary / Lambda S3 이벤트 딕셔너리

        Returns:
            List[dict]: List of detected PII instances with pattern info / 감지된 개인정보와 패턴 정보를 포함한 리스트
        """
        text = self.extract_text(event)
        if not text:
            self.logger.warning(f"Failed to extract text from S3 object")
            return []
        
        results = []
        for pattern in self.patterns:
            # TODO: Implement pattern matching logic
            pass
        
        return results
    
    def get_s3_info(self, event: Dict[str, Any]) -> tuple[str, str]:
        """
        Extract S3 bucket and key from event. / 이벤트에서 S3 버킷과 키를 추출합니다.

        Args:
            event (Dict[str, Any]): Lambda S3 event dictionary / Lambda S3 이벤트 딕셔너리

        Returns:
            tuple[str, str]: Bucket name and object key / 버킷 이름과 객체 키
        """
        try:
            recode = event['Records'][0]['s3']
            bucket = recode['bucket']['name']
            key = recode['object']['key']
            
            return bucket, key
        
        except (KeyError, IndexError) as e:
            self.logger.error(f"Invalid S3 event structure: {e}")
            raise ValueError("Invalid S3 event structure")
        