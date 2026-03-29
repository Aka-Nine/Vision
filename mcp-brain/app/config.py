from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    api_keys: str = ""
    database_url: str = ""
    storage_credentials: str = ""
    feature_flags: str = ""
    
    # Market Intelligence API Keys
    market_data_provider: str = "free" # 'free' or 'paid'
    gemini_api_key: str = ""
    apify_api_key: str = "" # For future paid Dribbble scraping
    serpapi_api_key: str = "" # For future paid demand estimation
    
    # Pinterest specific configuration
    pinterest_email: str = ""
    pinterest_password: str = ""

    # Reddit API Credentials
    reddit_client_id: str = ""
    reddit_client_secret: str = ""
    reddit_user_agent: str = "python:mcp-brain:v1.0 (by /u/mcp-bot)"
    reddit_username: str = ""
    reddit_password: str = ""

    # screenshot-to-code integration
    s2c_backend_ws_url: str = "ws://127.0.0.1:7001/generate-code"
    s2c_stack: str = "html_tailwind"  # one of: html_tailwind, html_css, react_tailwind, bootstrap, vue_tailwind, ionic_tailwind
    s2c_openai_api_key: str = ""
    s2c_openai_base_url: str = ""
    s2c_anthropic_api_key: str = ""
    s2c_gemini_api_key: str = ""



    class Config:
        env_file = ".env"
        extra = "ignore"

    def validate_environment(self):
        import logging
        if self.market_data_provider == "paid":
            if not self.serpapi_api_key or not self.apify_api_key:
                logging.warning("Market data provider is 'paid' but missing SerpAPI or Apify keys!")
        
        if not self.gemini_api_key:
            logging.warning("Gemini API key is missing. AI brief generation will fallback to mock data.")

        if not (self.s2c_openai_api_key or self.s2c_anthropic_api_key or self.s2c_gemini_api_key):
            logging.warning("screenshot-to-code keys missing. Screenshot-to-code integration will be unavailable.")
            
settings = Settings()
settings.validate_environment()
