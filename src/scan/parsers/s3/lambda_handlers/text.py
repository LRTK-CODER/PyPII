import boto3
import re
from typing import Any, Dict, Optional, Set
from botocore.exceptions import ClientError

from .base import LambdaBaseParser

class TextParser(LambdaBaseParser):
    """
    Text file parser for PII detection in Lambda. / Lambda에서 개인정보 감지를 위한 텍스트 파일 파서"

    Args:
        LambdaBaseParser (_type_): _description_
    """
    DEFAULT_TEXT_EXTENSIONS = set()
    
    def __init__(self, *args, text_extensions: Optional[Set[str]] = None, **kwargs):
        """
        Initialize text parser. / 텍스트 파서를 초기화합니다.

        Args:
            text_extensions (Optional[Set[str]]): Set of text file extensions to handle / 처리할 텍스트 파일 확장자 집합
            *args, **kwargs: Arguments for parent class / 부모 클래스 인자

        Raises:
            ValueError: If no text extensions are provided / 텍스트 확장자가 제공되지 않으면 발생
        """
        super().__init__(*args, **kwargs)
        self.s3_client = boto3.client('s3')
        self.text_extensions = self.DEFAULT_TEXT_EXTENSIONS.union(text_extensions or set())
        
        if not self.text_extensions:
            raise ValueError("Text extensions set cannot be empty. Please provide valid extensions.")
        
    def can_handle(self, event: Dict[str, Any]) -> bool:
        """
        Check if S3 object is a text file. / S3 객체가 텍스트 파일인지 확인합니다.

        Args:
            event (Dict[str, Any]): Lambda S3 event dictionary / Lambda S3 이벤트 딕셔너리

        Returns:
            bool: True if file is text type, False otherwise / 텍스트 파일이면 True, 아니면 False
        """
        try:
            _, key = self.get_s3_info(event)
            return any(key.lower().endswith(ext.lower()) for ext in self.text_extensions)
        
        except ClientError as e:
            self.logger.error(f"Error checking file type: {e}")
            return False
        
    def extract_text(self, event: Dict[str, Any], encoding: str = 'utf-8') -> Optional[str]:
        """
        Extract text content from S3 object. / S3 객체에서 텍스트를 추출합니다.

        Args:
            event (Dict[str, Any]): Lambda S3 event dictionary / Lambda S3 이벤트 딕셔너리
            encoding (str): Encoding to use for text extraction / 텍스트 추출에 사용할 인코딩

        Returns:
            Optional[str]: Extracted text or None if extraction fails / 추출된 텍스트 또는 실패 시 None
        """
        try:
            bucket, key = self.get_s3_info(event)
            response = self.s3_client.get_object(Bucket=bucket, Key=key)
            
            try:
                return response['Body'].read().decode(encoding)
            
            except UnicodeDecodeError:
                self.logger.error(f"Unicode decode error for {bucket}/{key} with encoding {encoding}: {e}")
                return None  
            
        except Exception as e:
            self.logger.error(f"Error extracting text from {bucket}/{key}: {e}")
            return None

    def scan(self, event: Dict[str, Any]) -> Dict[str, Any]:
        """_summary_

        Args:
            event (Dict[str, Any]): _description_

        Returns:
            List[str]: _description_
        """
        text = self.extract_text(event)
        if text is None:
            return {}
        
        self.logger.info("Scanning entire text for PII patterns.")
                
        file_results = {"Type": "Text"}

        lines = text.splitlines()
        
        for pattern in self.patterns:
            line_numbers = set()
            
            for line_number, line in enumerate(lines, start=1):
                if re.search(pattern.pattern, line):
                    line_numbers.add(line_number)
            
            if line_numbers:
                file_results[pattern.name] = {
                    "pii-total": len(line_numbers),
                    "location": sorted(line_numbers)
                }
            else:
                file_results[pattern.name] = None
                        
        return file_results