"""Constantes de la integracion de Uttera."""

DOMAIN = "uttera"

CONF_API_KEY = "api_key"
CONF_BASE_URL = "base_url"
CONF_VOICE = "voice"

DEFAULT_BASE_URL = "https://api.uttera.ai"
DEFAULT_VOICE = "nova"

#: Tiempo de espera. Una grabacion larga tarda en subir y en procesarse; el
#: valor por defecto de aiohttp corta trabajos que iban perfectamente.
TIMEOUT = 600
