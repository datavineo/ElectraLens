"""
Production Security Configuration for ElectraLens
"""
import os
from datetime import timedelta

class ProductionConfig:
    """Production-ready configuration settings."""
    
    # Database Configuration
    DATABASE_URL = os.getenv('DATABASE_URL')
    
    # JWT Configuration
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'CHANGE-THIS-SECRET-KEY')
    JWT_ALGORITHM = 'HS256'
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv('JWT_ACCESS_TOKEN_EXPIRE_MINUTES', 30))
    
    # Application Settings
    ENVIRONMENT = os.getenv('ENVIRONMENT', 'production')
    DEBUG = os.getenv('DEBUG', 'false').lower() == 'true'
    
    # URLs Configuration
    FRONTEND_URL = os.getenv('FRONTEND_URL', 'https://datavineo.vercel.app')
    BACKEND_URL = os.getenv('BACKEND_URL', 'https://electra-lens.vercel.app')
    API_BASE_URL = os.getenv('API_BASE_URL', 'https://electra-lens.vercel.app')
    
    # CORS Configuration
    CORS_ORIGINS = [
        "https://datavineo.vercel.app",
        "https://electra-lens.vercel.app",
        "https://datavineo.github.io"
    ]
    
    # If in development, add localhost
    if ENVIRONMENT == 'development':
        CORS_ORIGINS.extend([
            "http://localhost:8501",
            "http://localhost:3000",
            "http://127.0.0.1:8501",
            "http://127.0.0.1:3000"
        ])
    
    # Security Settings
    RATE_LIMITING_ENABLED = os.getenv('RATE_LIMITING_ENABLED', 'true').lower() == 'true'
    SESSION_TIMEOUT = timedelta(minutes=int(os.getenv('SESSION_TIMEOUT_MINUTES', 30)))
    
    # Database Connection Pool
    DB_POOL_SIZE = int(os.getenv('DB_POOL_SIZE', 10))
    DB_MAX_OVERFLOW = int(os.getenv('DB_MAX_OVERFLOW', 20))
    DB_POOL_RECYCLE = int(os.getenv('DB_POOL_RECYCLE', 3600))
    
    # Default User Credentials (should be changed in production!)
    DEFAULT_ADMIN_USERNAME = os.getenv('DEFAULT_ADMIN_USERNAME', 'admin')
    DEFAULT_ADMIN_PASSWORD = os.getenv('DEFAULT_ADMIN_PASSWORD', 'admin123')
    DEFAULT_ADMIN_FULLNAME = os.getenv('DEFAULT_ADMIN_FULLNAME', 'System Administrator')
    
    DEFAULT_VIEWER_USERNAME = os.getenv('DEFAULT_VIEWER_USERNAME', 'viewer')
    DEFAULT_VIEWER_PASSWORD = os.getenv('DEFAULT_VIEWER_PASSWORD', 'viewer123')
    DEFAULT_VIEWER_FULLNAME = os.getenv('DEFAULT_VIEWER_FULLNAME', 'Demo Viewer')
    
    # Password Requirements
    PASSWORD_MIN_LENGTH = int(os.getenv('PASSWORD_MIN_LENGTH', 8))
    PASSWORD_REQUIRE_UPPERCASE = os.getenv('PASSWORD_REQUIRE_UPPERCASE', 'true').lower() == 'true'
    PASSWORD_REQUIRE_LOWERCASE = os.getenv('PASSWORD_REQUIRE_LOWERCASE', 'true').lower() == 'true'
    PASSWORD_REQUIRE_NUMBERS = os.getenv('PASSWORD_REQUIRE_NUMBERS', 'true').lower() == 'true'
    PASSWORD_REQUIRE_SPECIAL = os.getenv('PASSWORD_REQUIRE_SPECIAL', 'false').lower() == 'true'
    
    @classmethod
    def validate_config(cls):
        """Validate critical configuration settings."""
        errors = []
        
        if not cls.DATABASE_URL:
            errors.append("DATABASE_URL is required")
        
        if cls.JWT_SECRET_KEY == 'CHANGE-THIS-SECRET-KEY':
            errors.append("JWT_SECRET_KEY must be changed from default")
        
        if len(cls.JWT_SECRET_KEY) < 32:
            errors.append("JWT_SECRET_KEY should be at least 32 characters long")
        
        if cls.ENVIRONMENT == 'production':
            if cls.DEBUG:
                errors.append("DEBUG should be False in production")
            
            if cls.DEFAULT_ADMIN_PASSWORD == 'admin123':
                errors.append("DEFAULT_ADMIN_PASSWORD should be changed in production")
            
            if cls.DEFAULT_VIEWER_PASSWORD == 'viewer123':
                errors.append("DEFAULT_VIEWER_PASSWORD should be changed in production")
        
        return errors
    
    @classmethod
    def get_config_summary(cls):
        """Get a summary of current configuration."""
        return {
            "environment": cls.ENVIRONMENT,
            "debug": cls.DEBUG,
            "frontend_url": cls.FRONTEND_URL,
            "backend_url": cls.BACKEND_URL,
            "database_configured": bool(cls.DATABASE_URL),
            "jwt_configured": cls.JWT_SECRET_KEY != 'CHANGE-THIS-SECRET-KEY',
            "cors_origins": cls.CORS_ORIGINS,
            "rate_limiting": cls.RATE_LIMITING_ENABLED,
            "session_timeout_minutes": cls.SESSION_TIMEOUT.total_seconds() / 60
        }


# Global configuration instance
config = ProductionConfig()

# Validate configuration on import
validation_errors = config.validate_config()
if validation_errors and config.ENVIRONMENT == 'production':
    import logging
    logger = logging.getLogger(__name__)
    logger.warning("Configuration validation errors:")
    for error in validation_errors:
        logger.warning(f"  - {error}")