from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
      app_name: str = "NexoScribe API"
      api_v1_prefix: str = "/api/v1"
      debug: bool = True
      database_url: str
      jwt_secret_key: str
      jwt_algorithm: str = "HS256"
      access_token_expire_minutes: int = 30
      refresh_token_expire_days: int = 7
      cookie_secure: bool = True
      frontend_url: str = "http://localhost:3000"
      smtp_host: str
      smtp_port: int
      smtp_username: str
      smtp_password: str
      smtp_from_email: str
      smtp_from_name: str
      gcs_bucket_name: str
      google_application_credentials: str | None = None
      profile_image_signed_url_expire_minutes: int = 30

      model_config = SettingsConfigDict(
          env_file=".env",
          env_file_encoding="utf-8",
      )

settings = Settings()
