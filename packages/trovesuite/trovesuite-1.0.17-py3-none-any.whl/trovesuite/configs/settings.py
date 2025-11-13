import os
class Settings:

    # Database URL
    DATABASE_URL: str = os.getenv("DATABASE_URL")

    DB_USER: str = os.getenv("DB_USER")
    DB_HOST: str = os.getenv("DB_HOST")
    DB_NAME: str = os.getenv("DB_NAME")
    DB_PORT: str = os.getenv("DB_PORT")
    DB_PASSWORD: str = os.getenv("DB_PASSWORD")
    
    # Application settings
    DEBUG: bool = os.getenv("DEBUG", "True").lower() in ("true",1)
    APP_NAME: str = os.getenv("APP_NAME", "Python Template API")
    APP_VERSION: str = os.getenv("APP_VERSION", "1.0.0")
    
    # Logging settings
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    LOG_FORMAT: str = os.getenv("LOG_FORMAT", "detailed")  # detailed, json, simple
    LOG_TO_FILE: bool = os.getenv("LOG_TO_FILE", "False").lower() in ("true", 1)
    LOG_MAX_SIZE: int = int(os.getenv("LOG_MAX_SIZE", "10485760"))  # 10MB
    LOG_BACKUP_COUNT: int = int(os.getenv("LOG_BACKUP_COUNT", "5"))
    LOG_DIR: str = os.getenv("LOG_DIR", "logs")
        
   # Security settings
    ALGORITHM: str = os.getenv("ALGORITHM")
    SECRET_KEY: str = os.getenv("SECRET_KEY")
    ENVIRONMENT: str = os.getenv("ENVIRONMENT")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "120"))
    
    # =============================================================================
    # SHARED TABLES (main schema)
    # =============================================================================
    MAIN_TENANTS_TABLE = os.getenv("MAIN_TENANTS_TABLE", "main.tenants")
    MAIN_TENANT_RESOURCE_ID_TABLE = os.getenv("MAIN_TENANT_RESOURCE_ID_TABLE", "main.tenant_resource_ids")
    MAIN_SUBSCRIPTIONS_TABLE = os.getenv("MAIN_SUBSCRIPTIONS_TABLE", "main.subscriptions")
    MAIN_APPS_TABLE = os.getenv("MAIN_APPS_TABLE", "main.apps")
    MAIN_USERS_TABLE = os.getenv("MAIN_USERS_TABLE", "main.users")
    MAIN_RESOURCE_TYPES_TABLE = os.getenv("MAIN_RESOURCE_TYPES_TABLE", "main.resource_types")
    MAIN_RESOURCE_ID_TABLE = os.getenv("MAIN_RESOURCE_ID_TABLE", "main.resource_ids")
    MAIN_RESOURCES_TABLE = os.getenv("MAIN_RESOURCES_TABLE", "main.resources")
    MAIN_PERMISSIONS_TABLE = os.getenv("MAIN_PERMISSIONS_TABLE", "main.permissions")
    MAIN_ROLES_TABLE = os.getenv("MAIN_ROLES_TABLE", "main.roles")
    MAIN_ROLE_PERMISSIONS_TABLE = os.getenv("MAIN_ROLE_PERMISSIONS_TABLE", "main.role_permissions")
    MAIN_USER_SUBSCRIPTIONS_TABLE = os.getenv("MAIN_USER_SUBSCRIPTIONS_TABLE", "main.user_subscriptions")
    MAIN_USER_SUBSCRIPTION_HISTORY_TABLE = os.getenv("MAIN_USER_SUBSCRIPTION_HISTORY_TABLE", "main.user_subscription_history")
    MAIN_OTP = os.getenv("MAIN_OTP", "main.otps")
    MAIN_PASSWORD_POLICY = os.getenv("MAIN_PASSWORD_POLICY", "main.password_policies")
    MAIN_MULTI_FACTOR_SETTINGS = os.getenv("MAIN_MULTI_FACTOR_SETTINGS", "main.multi_factor_settings")
    MAIN_USER_LOGIN_TRACKING = os.getenv("MAIN_USER_LOGIN_TRACKING", "main.user_login_tracking")
    MAIN_ENTERPRISE_SUBSCRIPTIONS_TABLE = os.getenv("MAIN_ENTERPRISE_SUBSCRIPTIONS_TABLE", "main.enterprise_subscriptions")
    MAIN_CHANGE_PASSWORD_POLICY_TABLE = os.getenv("MAIN_CHANGE_PASSWORD_POLICY_TABLE", "main.change_password_policy")

    # System-level tables
    MAIN_SYSTEM_GROUPS_TABLE = os.getenv("MAIN_SYSTEM_GROUPS_TABLE", "main.system_groups")
    MAIN_SYSTEM_USER_GROUPS_TABLE = os.getenv("MAIN_SYSTEM_USER_GROUPS_TABLE", "main.system_user_groups")
    MAIN_SYSTEM_ASSIGN_ROLES_TABLE = os.getenv("MAIN_SYSTEM_ASSIGN_ROLES_TABLE", "main.system_assign_roles")
    
    # =============================================================================
    # TENANT-SPECIFIC TABLES (tenant schemas)
    # =============================================================================
    TENANT_SUBSCRIPTIONS_TABLE = os.getenv("TENANT_SUBSCRIPTIONS_TABLE")
    TENANT_GROUPS_TABLE = os.getenv("TENANT_GROUPS_TABLE")
    TENANT_LOGIN_SETTINGS_TABLE = os.getenv("TENANT_LOGIN_SETTINGS_TABLE")
    TENANT_RESOURCES_TABLE = os.getenv("TENANT_RESOURCES_TABLE")
    TENANT_ASSIGN_ROLES_TABLE = os.getenv("TENANT_ASSIGN_ROLES_TABLE")
    TENANT_RESOURCE_ID_TABLE = os.getenv("TENANT_RESOURCE_ID_TABLE")
    TENANT_SUBSCRIPTION_HISTORY_TABLE = os.getenv("TENANT_SUBSCRIPTION_HISTORY_TABLE")
    TENANT_RESOURCE_DELETION_CHAT_HISTORY_TABLE = os.getenv("TENANT_RESOURCE_DELETION_CHAT_HISTORY_TABLE")
    TENANT_USER_GROUPS_TABLE = os.getenv("TENANT_USER_GROUPS_TABLE")
    TENANT_ACTIVITY_LOGS_TABLE = os.getenv("TENANT_ACTIVITY_LOGS_TABLE")
    TENANT_ORGANIZATIONS_TABLE = os.getenv("TENANT_ORGANIZATIONS_TABLE", "organizations")
    TENANT_BUSINESSES_TABLE = os.getenv("TENANT_BUSINESSES_TABLE", "businesses")
    TENANT_BUSINESS_APPS_TABLE = os.getenv("TENANT_BUSINESS_APPS_TABLE", "business_apps")
    TENANT_LOCATIONS_TABLE = os.getenv("TENANT_LOCATIONS_TABLE", "locations")
    TENANT_ASSIGN_LOCATIONS_TABLE = os.getenv("TENANT_ASSIGN_LOCATIONS_TABLE", "assign_locations")
    TENANT_UNIT_OF_MEASURE_TABLE = os.getenv("TENANT_UNIT_OF_MEASURE_TABLE")
    TENANT_CURRENCY=os.getenv("TENANT_CURRENCY")

    # Mail Configurations
    MAIL_SENDER_EMAIL=os.getenv("MAIL_SENDER_EMAIL")
    MAIL_SENDER_PWD=os.getenv("MAIL_SENDER_PWD")

    # Application Configurations
    APP_URL=os.getenv("APP_URL", "https://trovesuite.com")
    USER_ASSIGNED_MANAGED_IDENTITY=os.getenv("USER_ASSIGNED_MANAGED_IDENTITY")

    @property
    def database_url(self) -> str:
        if self.DATABASE_URL:
            return self.DATABASE_URL

        port = int(self.DB_PORT) if self.DB_PORT else 5432
        return f"postgresql://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{port}/{self.DB_NAME}"

# Global settings instance
db_settings = Settings()