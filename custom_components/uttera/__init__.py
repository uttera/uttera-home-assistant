"""Uttera para Home Assistant: voz y audio desde Assist.

⚠ SIN DEPENDENCIAS. `requirements` va vacio a proposito: se usa la sesion
  aiohttp que Home Assistant ya tiene montada. Una integracion que arrastra
  paquetes obliga a HA a instalarlos en cada arranque y es la primera causa de
  que una actualizacion del nucleo la rompa.
"""
from __future__ import annotations

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant

from .const import DOMAIN

PLATFORMS: list[Platform] = [Platform.TTS, Platform.STT]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Dar de alta las plataformas de voz."""
    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = dict(entry.data)
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    entry.async_on_unload(entry.add_update_listener(_recargar))
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Retirarlas."""
    ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if ok:
        hass.data[DOMAIN].pop(entry.entry_id, None)
    return ok


async def _recargar(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Al cambiar la configuracion, recargar: si no, la clave nueva no se usa
    hasta reiniciar Home Assistant y parece que no se guardo."""
    await hass.config_entries.async_reload(entry.entry_id)
