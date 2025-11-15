import sys
from pathlib import Path
try:
    import paho.mqtt.client as mqtt  # type: ignore
except (ImportError, ModuleNotFoundError):
    # Minimal stub to allow editor/linters to resolve the import when paho-mqtt isn't installed.
    class _StubClient:
        class CallbackAPIVersion:
            VERSION2 = 2

        def __init__(self, *args, **kwargs):
            self.on_connect = None
            self.on_message = None

        def connect(self, host, port=1883, keepalive=60, **kwargs):
            print(f"[stub mqtt] connect to {host}:{port}")

        def loop_forever(self):
            print("[stub mqtt] loop_forever called (no-op)")

        def publish(self, topic, payload=None, qos=0, retain=False, **kwargs):
            print(f"[stub mqtt] publish to {topic}: {payload}")

        def subscribe(self, topic, qos=0):
            print(f"[stub mqtt] subscribe to {topic}")

    class _MqttModule:
        CallbackAPIVersion = _StubClient.CallbackAPIVersion
        Client = _StubClient

    mqtt = _MqttModule()
import json
from typing import Dict, Any

# Ensure project root is on sys.path so 'src' can be imported when running this module directly.
PROJECT_ROOT = Path(__file__).resolve().parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.application.edge_processor import EdgeProcessor

class MqttGateway:
    """
    Adaptador de infraestructura para MQTT.
    Gestiona la conexión, suscripción y publicación de mensajes.
    Delega la lógica de negocio al EdgeProcessor.
    """
    def __init__(self, broker_address: str, processor: EdgeProcessor):
        self._processor = processor
        self._broker_address = broker_address
        self._client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
        self._client.on_connect = self._on_connect
        self._client.on_message = self._on_message

    def _on_connect(self, client, userdata, flags, rc, properties):
        if rc == 0:
            print("🔌 Conectado exitosamente al Broker MQTT!")
            client.subscribe("aurum/telemetry/+/raw")
            print("📡 Suscrito a 'aurum/telemetry/+/raw'")
        else:
            print(f"❌ Fallo al conectar, código de retorno {rc}\n")

    def _on_message(self, client, userdata, msg):
        """
        Callback que se activa al recibir un mensaje.
        Su única responsabilidad es decodificar, delegar y publicar el resultado.
        """
        try:
            payload = json.loads(msg.payload.decode())
            machine_id = payload.get("machine_id")

            if not machine_id:
                return

            # Delega el procesamiento a la capa de aplicación
            enriched_payload = self._processor.process_telemetry(payload)

            if enriched_payload:
                # Publica el resultado si el procesador devolvió algo
                topic = f"aurum/edge/{machine_id}/features"
                client.publish(topic, json.dumps(enriched_payload, default=str))
                print(f"✨ Features calculadas y publicadas para {machine_id} en el topic {topic}")

        except (json.JSONDecodeError, KeyError) as e:
            print(f"🚨 Error procesando mensaje MQTT: {e}")

    def start(self):
        """Inicia la conexión y el bucle de escucha."""
        self._client.connect(self._broker_address, 1883, 60)
        self._client.loop_forever()