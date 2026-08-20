import os
import tinytuya


class TuyaController:
    def __init__(
        self,
        device_id: str | None = None,
        device_key: str | None = None,
        device_ip: str | None = None,
        light_dps: int | str = 1,
        device_version: float | str = 3.3,
        device_type: str | None = None,
    ):
        self.device_id = (device_id or os.getenv("TUYA_DEVICE_ID", "") or "").strip()
        self.device_key = (device_key or os.getenv("TUYA_DEVICE_KEY", "") or "").strip()
        self.device_ip = (device_ip or os.getenv("TUYA_DEVICE_IP", "") or "").strip()
        self.light_dps = int(light_dps)
        self.device_version = float(device_version)
        self.device_type = (device_type or os.getenv("TUYA_DEVICE_TYPE", "outlet")).strip().lower()
        self._device = None

    @classmethod
    def from_env(cls):
        return cls(
            device_id=os.getenv("TUYA_DEVICE_ID"),
            device_key=os.getenv("TUYA_DEVICE_KEY"),
            device_ip=os.getenv("TUYA_DEVICE_IP"),
            light_dps=os.getenv("TUYA_LIGHT_DPS", "1"),
            device_version=os.getenv("TUYA_DEVICE_VERSION", "3.3"),
            device_type=os.getenv("TUYA_DEVICE_TYPE", "outlet"),
        )

    def is_configured(self) -> bool:
        return bool(self.device_id and self.device_key and self.device_ip)

    def is_available(self) -> bool:
        return tinytuya is not None

    def _validate(self):
        if not self.is_available():
            raise RuntimeError(
                "Biblioteca tinytuya não encontrada. Instale com: pip install tinytuya"
            )
        if not self.is_configured():
            raise ValueError(
                "Variáveis TUYA_DEVICE_ID, TUYA_DEVICE_KEY e TUYA_DEVICE_IP devem estar configuradas."
            )

    def _device_instance(self):
        if self._device is not None:
            return self._device

        self._validate()
        device_type = self.device_type
        if device_type == "bulb" and hasattr(tinytuya, "BulbDevice"):
            self._device = tinytuya.BulbDevice(self.device_id, self.device_ip, self.device_key)
        else:
            self._device = tinytuya.OutletDevice(self.device_id, self.device_ip, self.device_key)

        if hasattr(self._device, "set_version"):
            self._device.set_version(self.device_version)
        return self._device

    def _set_light_power(self, on: bool) -> bool:
        device = self._device_instance()
        if hasattr(device, "set_status"):
            device.set_status(on)
        elif hasattr(device, "set_dps"):
            device.set_dps(self.light_dps, bool(on))
        elif hasattr(device, "turn_on") and on:
            device.turn_on()
        elif hasattr(device, "turn_off") and not on:
            device.turn_off()
        else:
            raise RuntimeError(
                "Não foi possível enviar comando Tuya: método de controle compatível não encontrado."
            )
        return True

    def turn_on_lights(self) -> bool:
        return self._set_light_power(True)

    def turn_off_lights(self) -> bool:
        return self._set_light_power(False)

    def turn_on_varanda_lights(self) -> bool:
        return self.turn_on_lights()