# PyPII
Development of a CLI tool for searching and classifying sensitive data in local file systems<br>
PyPII는 파일과 디렉토리에서 개인식별정보(PII)를 검출하는 명령줄 도구입니다.

## Features / 주요 기능
- Detect various types of PII using customizable patterns / 커스터마이징 가능한 패턴으로 다양한 PII 검출
- Support for multiple file formats / 다양한 파일 형식 지원
- Risk level classification (HIGH/MEDIUM/LOW) / 위험도 분류 (상/중/하)
- Detailed reporting in JSON/CSV formats / JSON/CSV 형식의 상세 리포트
- Recursive directory scanning / 재귀적 디렉토리 스캔

## Installation / 설치
```bash
pip install pypii
```

## Usage / 사용법
Basic usage / 기본 사용법:
```bash
pypii scan /path/to/scan --pattern-file patterns.json --output report.json
```

Options / 옵션:
- `path`: Path to file or directory to scan / 스캔할 파일 또는 디렉토리 경로
- `-p, --pattern-file`: Pattern definition file (default: patterns.json) / 패턴 정의 파일 (기본값: patterns.json)
- `-o, --output`: Output report file (default: pii_report.json) / 결과 리포트 파일 (기본값: pii_report.json)
- `-f, --format`: Report format [json/csv] (default: json) / 리포트 형식 [json/csv] (기본값: json)
- `-v, --verbose`: Enable verbose logging / 상세 로깅 활성화

## Pattern Definition / 패턴 정의
Create a JSON file with pattern definitions / 패턴 정의 JSON 파일 생성:
```json
{
    "patterns": {
        "HIGH": [
            {
                "name": "SSN",
                "pattern": "\\d{3}-\\d{2}-\\d{4}",
                "description": "Social Security Number"
            }
        ],
        "MEDIUM": [...],
        "LOW": [...]
    }
}
```

## Example Output / 출력 예시
JSON Report / JSON 리포트:
```
{
    "summary": {
        "total_files": 10,
        "total_detections": 25,
        "risk_level_counts": {
            "HIGH": 5,
            "MEDIUM": 12,
            "LOW": 8
        }
    },
    "detections": [...]
}
```

## Contributing / 기여하기
Contributions are welcome! Please feel free to submit a Pull Request.<br>
기여는 언제나 환영합니다! Pull Request를 자유롭게 제출해주세요.

## License / 라이선스
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.<br>
이 프로젝트는 MIT 라이선스를 따릅니다 - 자세한 내용은 [LICENSE](LICENSE) 파일을 참고하세요.