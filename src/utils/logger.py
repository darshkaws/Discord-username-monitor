"""
Discord Username Monitor - Logging Utilities
Centralized logging configuration and utilities
"""

import logging
import sys
from pathlib import Path
from datetime import datetime


def setup_logging(level=logging.INFO):
    """Setup logging configuration"""
    
    # Ensure logs directory exists
    logs_dir = Path("logs")
    logs_dir.mkdir(exist_ok=True)
    
    # Create formatters
    detailed_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    simple_formatter = logging.Formatter(
        '%(levelname)s: %(message)s'
    )
    
    # Create handlers
    # File handler for detailed logs
    file_handler = logging.FileHandler(
        logs_dir / f"monitor_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log",
        encoding='utf-8'
    )
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(detailed_formatter)
    
    # Error file handler
    error_handler = logging.FileHandler(
        logs_dir / "error_log.txt",
        encoding='utf-8'
    )
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(detailed_formatter)
    
    # Console handler for important messages
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.WARNING)
    console_handler.setFormatter(simple_formatter)
    
    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(level)
    
    # Remove existing handlers to avoid duplicates
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
    
    # Add handlers
    root_logger.addHandler(file_handler)
    root_logger.addHandler(error_handler)
    root_logger.addHandler(console_handler)
    
    # Reduce noise from external libraries
    logging.getLogger('selenium').setLevel(logging.WARNING)
    logging.getLogger('urllib3').setLevel(logging.WARNING)
    logging.getLogger('requests').setLevel(logging.WARNING)
    
    print(f"Logging initialized - Files saved to {logs_dir}")


def get_logger(name):
    """Get a logger instance for a module"""
    return logging.getLogger(name)


class FileLogger:
    """Simple file logger for specific data"""
    
    def __init__(self, filename):
        self.filename = Path("logs") / filename
        self.filename.parent.mkdir(exist_ok=True)
    
    def log(self, message):
        """Log a message with timestamp"""
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        log_entry = f"[{timestamp}] {message}\n"
        
        try:
            with open(self.filename, "a", encoding="utf-8") as f:
                f.write(log_entry)
                f.flush()
        except Exception as e:
            logging.error(f"Failed to write to {self.filename}: {e}")


class ResultLogger:
    """Logger for results and available usernames"""
    
    def __init__(self):
        self.results_dir = Path("results")
        self.results_dir.mkdir(exist_ok=True)
        
        self.available_file = self.results_dir / "available_usernames.txt"
        self.session_file = self.results_dir / f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
    
    def log_available_username(self, username, account):
        """Log an available username immediately"""
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        # Format: username:email:password:token
        entry = f"{username}:{account.email}:{account.password or 'N/A'}:{account.token}\n"
        
        try:
            # Log to main available file
            with open(self.available_file, "a", encoding="utf-8") as f:
                f.write(entry)
                f.flush()
            
            # Log to session file with timestamp
            session_entry = f"[{timestamp}] AVAILABLE: {entry}"
            with open(self.session_file, "a", encoding="utf-8") as f:
                f.write(session_entry)
                f.flush()
                
            logging.info(f"AVAILABLE: {username} - {account.email}")
            
        except Exception as e:
            logging.error(f"Failed to log available username: {e}")
    
    def log_claim_attempt(self, username, account, success):
        """Log a claim attempt"""
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        status = "SUCCESS" if success else "FAILED"
        
        entry = f"[{timestamp}] CLAIM_{status}: {username} - {account.email}\n"
        
        try:
            with open(self.session_file, "a", encoding="utf-8") as f:
                f.write(entry)
                f.flush()
                
            logging.info(f"CLAIM_{status}: {username} - {account.email}")
            
        except Exception as e:
            logging.error(f"Failed to log claim attempt: {e}")