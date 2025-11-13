from urllib.parse import urlparse
from base import BaseTransformer

class URLNormalizer(BaseTransformer):
    """Standardizes and validates URL fields."""

    def transform(self, df):
        def _normalize(url: str):
            if not url:
                return None
            if "@" in url or url.upper() == "EGVP":
                return None
            if not url.lower().startswith(("http://", "https://")):
                url = "https://" + url
            url = url.replace("http.//", "http://").replace("wwww.", "www.")
            parsed = urlparse(url)
            netloc = parsed.netloc.lower().removeprefix("www.")
            return f"https://{netloc}{parsed.path}"

        df = df.copy()
        df["url"] = df["url"].apply(_normalize)
        return df
