"""El alta desde la interfaz: la clave se pega aqui, no en un YAML."""
from __future__ import annotations

from typing import Any

import voluptuous as vol

from homeassistant.config_entries import ConfigFlow, ConfigFlowResult
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .const import CONF_API_KEY, CONF_BASE_URL, DEFAULT_BASE_URL, DOMAIN, TIMEOUT


class UtteraConfigFlow(ConfigFlow, domain=DOMAIN):
    """Pide la clave y COMPRUEBA que sirve antes de guardarla."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        errors: dict[str, str] = {}
        if user_input is not None:
            base = user_input.get(CONF_BASE_URL, DEFAULT_BASE_URL).rstrip("/")
            clave = user_input[CONF_API_KEY].strip()
            # ⚠ Se valida CONTRA EL SERVICIO antes de guardar. Aceptar una clave
            #   mala y fallar luego en cada frase que alguien le diga a Assist
            #   es la peor forma de descubrirlo.
            sesion = async_get_clientsession(self.hass)
            try:
                async with sesion.get(
                    f"{base}/v1/models",
                    headers={"Authorization": f"Bearer {clave}"},
                    timeout=30,
                ) as r:
                    if r.status == 401:
                        errors["base"] = "invalid_auth"
                    elif r.status >= 400:
                        errors["base"] = "cannot_connect"
            except Exception:  # noqa: BLE001
                errors["base"] = "cannot_connect"

            if not errors:
                await self.async_set_unique_id(f"{base}")
                self._abort_if_unique_id_configured()
                return self.async_create_entry(
                    title="Uttera", data={CONF_API_KEY: clave, CONF_BASE_URL: base}
                )

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_API_KEY): str,
                    vol.Optional(CONF_BASE_URL, default=DEFAULT_BASE_URL): str,
                }
            ),
            errors=errors,
        )
