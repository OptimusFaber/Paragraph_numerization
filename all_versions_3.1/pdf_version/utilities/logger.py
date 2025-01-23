import logging
from functools import wraps

class DocumentErrorLogger:
    _instances = {}
    
    def __new__(cls, log_path='default.log'):
        if log_path not in cls._instances:
            cls._instances[log_path] = super().__new__(cls)
        return cls._instances[log_path]
    
    def __init__(self, log_path='default.log'):
        if not hasattr(self, 'logger'):
            self.logger = logging.getLogger(f'document_processor')
            if not self.logger.hasHandlers():
                self.logger.setLevel(logging.DEBUG)
                
                # Formatter
                formatter = logging.Formatter(
                    '%(asctime)s %(levelname)s module: %(name)s line num: %(lineno)s '
                    'func: %(funcName)s %(message)s'
                )
                
                # File handler
                file_handler = logging.FileHandler(log_path, encoding='utf-8')
                file_handler.setFormatter(formatter)
                self.logger.addHandler(file_handler)

def log_errors(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        error_path = kwargs.get('error_path')
        
        if not error_path and args and hasattr(args[0], 'error_path'):
            error_path = args[0].error_path
        
        # Кэшируем логгер по пути log_path
        logger = DocumentErrorLogger(error_path or 'default.log')
        
        try:
            return func(*args, **kwargs)
        except Exception as e:
            if args and hasattr(args[0].__class__, func.__name__):
                class_name = args[0].__class__.__name__
                func_name = f"{class_name}.{func.__name__}"
            else:
                func_name = func.__name__

            try:
                txt_path = kwargs.get('txt_path') or getattr(args[0], 'txt_path', 'N/A')
            except:
                txt_path = 'N/A'
            logger.logger.error(f"Error in {func_name}: {str(e)}\nText path: {txt_path}")
            raise
    return wrapper

class DocumentLogger:
    _instances = {}
    
    def __new__(cls, log_path='default.log'):
        if log_path not in cls._instances:
            cls._instances[log_path] = super().__new__(cls)
        return cls._instances[log_path]
    
    def __init__(self, log_path='default.log'):
        if not hasattr(self, 'logger'):
            self.logger = logging.getLogger(f'document_processor_logger')
            if not self.logger.hasHandlers():
                self.logger.setLevel(logging.DEBUG)
                
                # Formatter
                formatter = logging.Formatter(
                    '%(asctime)s %(levelname)s module: %(name)s line num: %(lineno)s '
                    'func: %(funcName)s %(message)s'
                )
                
                # File handler
                file_handler = logging.FileHandler(log_path, encoding='utf-8')
                file_handler.setFormatter(formatter)
                self.logger.addHandler(file_handler)

def logger(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        log_path = kwargs.get('log_path')
        
        if not log_path and args and hasattr(args[0], 'log_path'):
            log_path = args[0].log_path
        
        # Кэшируем логгер по пути log_path
        logger = DocumentLogger(log_path or 'default.log')
        
        try:
            return func(*args, **kwargs)
        except Exception as e:
            if args and hasattr(args[0].__class__, func.__name__):
                class_name = args[0].__class__.__name__
                func_name = f"{class_name}.{func.__name__}"
            else:
                func_name = func.__name__
            
            txt_path = kwargs.get('txt_path') or getattr(args[0], 'txt_path', 'N/A')
            logger.logger.error(f"Error in {func_name}: {str(e)}\nText path: {txt_path}")
            raise
    return wrapper

# dict([(key, value) for key, value in logger._instances.items() if key.endswith('log')])
