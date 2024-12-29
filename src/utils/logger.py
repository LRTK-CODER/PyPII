import logging
import sys
from pathlib import Path

def setup_logger(name: str, log_level: str = "INFO", log_file: str = None) -> logging.Logger:
    """로거 설정을 초기화합니다.

    Args:
        name (str): 로거 이름
        log_level (str, optional): 로깅 레벨. Defaults to "INFO".
        log_file (str, optional): 로그 파일 경로. Defaults to None.

    Returns:
        logging.Logger: 설정된 로거 인스턴스
    """
    # 로거 생성
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, log_level.upper()))

    # 로그 포맷 설정
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    # 콘솔 핸들러 설정
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # 파일 핸들러 설정 (옵션)
    if log_file:
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    return logger
