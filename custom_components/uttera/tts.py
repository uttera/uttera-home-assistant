"""Uttera como voz de Assist."""
from __future__ import annotations

from typing import Any

from homeassistant.components.tts import TextToSpeechEntity, TtsAudioType
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import CONF_API_KEY, CONF_BASE_URL, DEFAULT_VOICE, DOMAIN, TIMEOUT

#: Los idiomas que admite la sintesis. Se declaran a mano y no se piden al
#: arrancar: Home Assistant necesita la lista ANTES de que la integracion
#: pueda hablar con nadie, y un arranque sin red dejaria a Assist sin voz.
IDIOMAS = [
    "es", "en", "fr", "de", "it", "pt", "nl", "pl", "ru", "ja", "zh", "ko",
    "ar", "hi", "tr", "sv", "da", "no", "fi", "cs", "el", "he", "id", "uk",
]


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    async_add_entities([UtteraTTS(entry)])


class UtteraTTS(TextToSpeechEntity):
    """Texto a voz."""

    _attr_has_entity_name = True
    _attr_name = None

    def __init__(self, entry: ConfigEntry) -> None:
        self._entry = entry
        self._attr_unique_id = f"{entry.entry_id}-tts"

    @property
    def default_language(self) -> str:
        return "es"

    @property
    def supported_languages(self) -> list[str]:
        return IDIOMAS

    @property
    def supported_options(self) -> list[str]:
        return ["voice"]

    async def async_get_tts_audio(
        self, message: str, language: str, options: dict[str, Any]
    ) -> TtsAudioType:
        datos = self._entry.data
        base = datos[CONF_BASE_URL]
        sesion = async_get_clientsession(self.hass)
        # ⚠ Los saltos de linea se quitan: cada uno mete una pausa de 1,3 s Y
        #   SE COBRA. Assist manda a menudo texto con saltos, asi que dejarlos
        #   sale caro y suena peor.
        texto = " ".join(message.split())
        try:
            async with sesion.post(
                f"{base}/v1/audio/speech",
                headers={"Authorization": f"Bearer {datos[CONF_API_KEY]}"},
                json={
                    "model": "tts-1",
                    "input": texto,
                    "voice": options.get("voice") or DEFAULT_VOICE,
                    "language": language,
                    "response_format": "mp3",
                },
                timeout=TIMEOUT,
            ) as r:
                if r.status != 200:
                    raise HomeAssistantError(
                        f"Uttera returned {r.status}: {(await r.text())[:200]}"
                    )
                return "mp3", await r.read()
        except HomeAssistantError:
            raise
        except Exception as err:  # noqa: BLE001
            raise HomeAssistantError(f"Uttera is not reachable: {err}") from err
