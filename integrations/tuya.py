import os
import json
import tinytuya


class TuyaController:
    def __init__(self):
        self.devices = {}
        self._loadDevices()


    def _loadDevices(self):
        _devices = os.getenv("TUYA_LIGHTS", "[]")

        if not _devices:
            print("Nenhuma lista de dispositivos Tuya configurada.")
            return

        try: 
            listDevices = json.loads(_devices)
            if not isinstance(listDevices, list):
                print("Error: TUYA_LIGHTS deve ser um array JSON.")
                return

            for _device in listDevices:
                deviceId = _device.get("id")
                if not deviceId or not _device.get("ip") or not _device.get("key"):
                    print("Error: Dispositivo Tuya sem id, ip ou key; ignorando.")
                    continue

                light = tinytuya.BulbDevice(
                    dev_id=deviceId,
                    address=_device.get("ip"),
                    local_key=_device.get("key"),
                    version=float(_device.get("version", 3.3))
                )

                light.set_socketPersistent(True)
                self.devices[deviceId] = light

            print(f"Success: {len(self.devices)} dispositivos foram carregados.")

        except json.JSONDecodeError:
            print("Error: O formato do JSON é inválido.")

    def turnOnLight(self, deviceId: str):
        device = self.devices.get(deviceId)

        if device:
            payload = device.generate_payload(tinytuya.CONTROL, { "1": True, "20": True })
            response = device._send_receive(payload)
            print(f"Dispositivo {deviceId} ligado: {response}")
        else:
            print(f"Dispositivo {deviceId} não encontrado.")

    def turnOffLight(self, deviceId: str):
        device = self.devices.get(deviceId)

        if device:
            payload = device.generate_payload(tinytuya.CONTROL, { "1": False, "20": False })
            response = device._send_receive(payload)
            print(f"Dispositivo {deviceId} desligado: {response}")
        else:
            print(f"Dispositivo {deviceId} não encontrado.")

    def turnOnAllLights(self):
        if not self.devices:
            print("Nenhum dispositivo encontrado.")
            return

        for devices_id in self.devices.keys():
            self.turnOnLight(devices_id)