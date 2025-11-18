# pure_scraper/config.py
from dataclasses import dataclass

@dataclass
class ScraperConfig:
    user_agent: str = "PureScraper/1.3"
    timeout: int = 12
    use_cache: bool = True
    cache_expiry_hours: int = 24
    prettify_indent: int = 2
    show_logs: bool = True
    rate_limit_seconds: float = 0.5   # pause between requests when enabled
    respect_robots_txt: bool = True
    max_redirects: int = 5
    max_retries: int = 3

config = ScraperConfig()
