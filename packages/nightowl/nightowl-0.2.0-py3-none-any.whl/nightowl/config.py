import os
from typing import Optional

class BaseMetricsConfig:
    """
    Base configuration for all services.
    Every service inherits these patterns.
    """
    
    def __init__(self, project: Optional[str] = None, app_name: Optional[str] = None, stage: Optional[str] = None):
        self.stage = stage or os.getenv("STAGE", "unknown") # e.g. prod, staging, dev
        self.project = project or os.getenv("PROJECT", "unknown") # e.g. proplay
        self.app_name = app_name or os.getenv("APP_NAME", "unknown") # e.g. gateway
        
    def get_common_labels(self) -> dict:
        """Standard labels for all metrics"""
        return {
            "project": self.project,
            "app": self.app_name,
            "stage": self.stage
        }


class DbMetricsConfig(BaseMetricsConfig):
    """
    Configuration for services with database metrics.
    Extends base config with db_name.
    """

    def __init__(self, project: Optional[str] = None, app_name: Optional[str] = None, 
                 stage: Optional[str] = None, db_name: Optional[str] = None):
        super().__init__(project, app_name, stage)
        self.db_name = db_name or os.getenv("DB_NAME") or os.getenv("POSTGRES_DB") or "unknown"
