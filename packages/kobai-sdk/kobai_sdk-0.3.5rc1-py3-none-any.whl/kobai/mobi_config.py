from pydantic_settings import BaseSettings

class MobiSettings(BaseSettings):

    #Application Specific Settings
    domain_extraction: dict = {}

    #Mobi Server Settings
    mobi_api_url: str = "https://localhost:8443/mobirest"
    mobi_username: str = "admin"
    mobi_password: str = "admin"
    cookies: str = ""
    use_cookies: bool = False
    verify_ssl = False

    catalog_name: str = "http://mobi.com/catalog-local"
    default_tenant_id: str = "00000000-0000-0000-0000-000000000000"

#settings = MobiSettings()