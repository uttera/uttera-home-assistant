"""Uttera como oido de Assist."""
from __future__ import annotations

from collections.abc import AsyncIterable

from homeassistant.components.stt import (
    AudioBitRates,
    AudioChannels,
    AudioCodecs,
    AudioFormats,
    AudioSampleRates,
    SpeechMetadata,
    SpeechResult,
    SpeechResultState,
    SpeechToTextEntity,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import CONF_API_KEY, CONF_BASE_URL, TIMEOUT
from .tts import IDIOMAS


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    async_add_entities([UtteraSTT(entry)])


class UtteraSTT(SpeechToTextEntity):
    """Voz a texto."""

    _attr_has_entity_name = True
    _attr_name = None

    def __init__(self, entry: ConfigEntry) -> None:
        self._entry = entry
        self._attr_unique_id = f"{entry.entry_id}-stt"

    @property
    def supported_languages(self) -> list[str]:
        return IDIOMAS

    @property
    def supported_formats(self) -> list[AudioFormats]:
        return [AudioFormats.WAV]

    @property
    def supported_codecs(self) -> list[AudioCodecs]:
        return [AudioCodecs.PCM]

    @property
    def supported_bit_rates(self) -> list[AudioBitRates]:
        return [AudioBitRates.BITRATE_16]

    @property
    def supported_sample_rates(self) -> list[AudioSampleRates]:
        return [AudioSampleRates.SAMPLERATE_16000]

    @property
    def supported_channels(self) -> list[AudioChannels]:
        return [AudioChannels.CHANNEL_MONO]

    async def async_process_audio_stream(
        self, metadata: SpeechMetadata, stream: AsyncIterable[bytes]
    ) -> SpeechResult:
        # ⚠ Assist entrega PCM en crudo, sin cabecera. Mandarlo tal cual hace
        #   que el motor no sepa el ritmo ni los canales y devuelva ruido: hay
        #   que ponerle una cabecera WAV. Se construye a mano para no arrastrar
        #   ninguna dependencia por 44 bytes.
        crudo = b"".join([trozo async for trozo in stream])
        if not crudo:
            return SpeechResult(None, SpeechResultState.ERROR)
        wav = _cabecera_wav(len(crudo), 16000, 1, 16) + crudo

        datos = self._entry.data
        sesion = async_get_clientsession(self.hass)
        import aiohttp

        formulario = aiohttp.FormData()
        formulario.add_field("file", wav, filename="audio.wav",
                             content_type="audio/wav")
        formulario.add_field("model", "whisper-1")
        if metadata.language:
            formulario.add_field("language", metadata.language.split("-")[0])
        try:
            async with sesion.post(
                f"{datos[CONF_BASE_URL]}/v1/audio/transcriptions",
                headers={"Authorization": f"Bearer {datos[CONF_API_KEY]}"},
                data=formulario,
                timeout=TIMEOUT,
            ) as r:
                if r.status != 200:
                    return SpeechResult(None, SpeechResultState.ERROR)
                cuerpo = await r.json()
        except Exception:  # noqa: BLE001
            return SpeechResult(None, SpeechResultState.ERROR)

        return SpeechResult(cuerpo.get("text", ""), SpeechResultState.SUCCESS)


def _cabecera_wav(n: int, ritmo: int, canales: int, bits: int) -> bytes:
    """Los 44 bytes de cabecera WAV, a mano.

    Se escribe aqui en vez de traer una biblioteca: son cuatro campos y evita
    que la integracion declare dependencias, que es lo que mas la expone a
    romperse con una actualizacion de Home Assistant."""
    import struct

    bloque = canales * bits // 8
    return (
        b"RIFF"
        + struct.pack("<I", 36 + n)
        + b"WAVEfmt "
        + struct.pack("<IHHIIHH", 16, 1, canales, ritmo, ritmo * bloque, bloque, bits)
        + b"data"
        + struct.pack("<I", n)
    )
