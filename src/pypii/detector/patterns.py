"""
PII Pattern Definition and Loading Module

This module loads and manages PII patterns from JSON files.

Patterns are organized by risk levels (HIGH, MEDIUM, LOW),
and each pattern includes a name, regex pattern, and description.

PII(개인식별정보) 패턴을 정의하고 로드하는 모듈

이 모듈은 JSON 파일에서 PII 패턴을 로드하고 관리합니다.

패턴은 위험도 레벨(HIGH, MEDIUM, LOW)별로 구성되며,
각 패턴은 이름, 정규표현식 패턴, 설명을 포함합니다.

Usage example / 사용 예시:
    loader = PatternLoader()
    patterns = loader.load_patterns("patterns.json")

JSON file format / JSON 파일 형식:
{
    "patterns": {
        "HIGH": [
            {
                "name": "주민등록번호",
                "pattern": "정규표현식",
                "description": "설명"
            }
        ],
        "MEDIUM": [...],
        "LOW": [...]
    }
}
"""

from enum import Enum
from dataclasses import dataclass
from pathlib import Path
import json
from typing import List, Dict


class RiskLevel(Enum):
    """
    Enumeration defining risk levels for PII patterns.

    Attributes:
        HIGH: High risk (e.g., National ID, Passport number)
        MEDIUM: Medium risk (e.g., Phone number, Bank account)
        LOW: Low risk (e.g., Email address, IP address)

    PII 패턴의 위험도 레벨을 정의하는 열거형

    Attributes:
        HIGH: 높은 위험도 (예: 주민등록번호, 여권번호)
        MEDIUM: 중간 위험도 (예: 전화번호, 계좌번호)
        LOW: 낮은 위험도 (예: 이메일 주소, IP 주소)
    """
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"


@dataclass
class PIIPattern:
    """
    Data class containing PII pattern information.

    Attributes:
        name: Pattern name (e.g., "National ID")
        pattern: Regular expression pattern string
        risk_level: Risk level (RiskLevel enum)
        description: Pattern description

    PII 패턴의 정보를 담는 데이터 클래스

    Attributes:
        name: 패턴의 이름 (예: "주민등록번호")
        pattern: 정규표현식 패턴 문자열
        risk_level: 위험도 레벨 (RiskLevel 열거형)
        description: 패턴에 대한 설명
    """
    name: str
    pattern: str
    risk_level: RiskLevel
    description: str


class PatternLoader:
    """
    Class for loading PII patterns from JSON files.
    JSON 파일에서 PII 패턴을 로드하는 클래스
    """

    @staticmethod
    def load_patterns(pattern_file: str) -> List[PIIPattern]:
        """
        Load PII patterns from the specified JSON file.

        Args:
            pattern_file: Path to pattern definition JSON file

        Returns:
            List[PIIPattern]: List of loaded PII pattern objects

        Raises:
            FileNotFoundError: When pattern file is not found
            json.JSONDecodeError: When JSON file format is invalid

        지정된 JSON 파일에서 PII 패턴들을 로드합니다.

        Args:
            pattern_file: 패턴 정의가 포함된 JSON 파일 경로

        Returns:
            List[PIIPattern]: 로드된 PII 패턴 객체들의 리스트

        Raises:
            FileNotFoundError: 패턴 파일을 찾을 수 없는 경우
            json.JSONDecodeError: JSON 파일 형식이 잘못된 경우
        """
        path = Path(pattern_file)
        if not path.exists():
            raise FileNotFoundError(f"패턴 파일을 찾을 수 없습니다: {pattern_file}")
            
        with path.open('r', encoding='utf-8') as f:
            data = json.load(f)
            
        patterns = []
        for risk_level, pattern_list in data['patterns'].items():
            for p in pattern_list:
                pattern = PIIPattern(
                    name=p['name'],
                    pattern=p['pattern'],
                    risk_level=RiskLevel[risk_level],
                    description=p.get('description', '')
                )
                patterns.append(pattern)
                
        return patterns