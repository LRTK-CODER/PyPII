import logging
import sys
from pathlib import Path

def setup_logger(name: str, log_level: str = "INFO", log_file: str = None) -> logging.Logger:
    """Initialize logger configuration. / 로거 설정을 초기화합니다.

        Args:
            name (str): Logger name / 로거 이름
            log_level (str, optional): Logging level. Defaults to "INFO". / 로깅 레벨. 기본값은 "INFO".
            log_file (str, optional): Log file path. Defaults to None. / 로그 파일 경로. 기본값은 None.

        Returns:
            logging.Logger: Configured logger instance / 설정된 로거 인스턴스
    """
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, log_level.upper()))

    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    if log_file:
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    return logger
