from enum import Enum
from dataclasses import dataclass
from pathlib import Path
from typing import List
import json

class RiskLevel(Enum):
    """Enumeration defining risk levels for PII patterns. / PII 패턴의 위험도 레벨을 정의하는 열거형

    Attributes:
        HIGH: High risk (e.g., National ID, Passport number) / 높은 위험도 (예: 주민등록번호, 여권번호)
        MEDIUM: Medium risk (e.g., Phone number, Bank account) / 중간 위험도 (예: 전화번호, 계좌번호)
        LOW: Low risk (e.g., Email address, IP address) / 낮은 위험도 (예: 이메일 주소, IP 주소)
    """
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"

@dataclass
class DataPattern:
    """Data class containing PII pattern information. / PII 패턴 정보를 담는 데이터 클래스

    Attributes:
        name: Pattern name (e.g., "National ID") / 패턴 이름 (예: "주민등록번호")
        pattern: Regular expression pattern string / 정규표현식 패턴 문자열
        risk_level: Risk level (RiskLevel enum) / 위험도 레벨 (RiskLevel 열거형)
        description: Pattern description / 패턴에 대한 설명
    """
    name: str
    pattern: str
    risk_level: RiskLevel
    description: str

class PatternLoader:
    """Class for loading PII patterns from JSON files. / JSON 파일에서 PII 패턴을 로드하는 클래스"""

    @staticmethod
    def load_patterns(pattern_file:str) -> List[DataPattern]:
        """Load PII patterns from the specified JSON file. / 지정된 JSON 파일에서 PII 패턴들을 로드합니다.

        Args:
            pattern_file: Path to pattern definition JSON file / 패턴 정의가 포함된 JSON 파일 경로

        Returns:
            List[PIIPattern]: List of loaded PII pattern objects / 로드된 PII 패턴 객체들의 리스트

        Raises:
            FileNotFoundError: When pattern file is not found / 패턴 파일을 찾을 수 없는 경우
            json.JSONDecodeError: When JSON file format is invalid / JSON 파일 형식이 잘못된 경우
        """
        path = Path(pattern_file)
        if not path.exists():
            raise FileNotFoundError(f"Not found Pattern file: {pattern_file}")
        
        with path.open("r", encoding="utf-8") as f:
            data = json.load(f)

        patterns = []
        for risk_level, pattern_list in data["patterns"].items():
            for p in pattern_list:
                pattern = DataPattern(
                    name = p["name"],
                    pattern = p["pattern"],
                    risk_level = RiskLevel[risk_level],
                    description = p.get("description", "")
                )
                patterns.append(pattern)

        return patterns
