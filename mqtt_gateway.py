import json
import paho.mqtt.client as mqtt
from paho.mqtt.enums import CallbackAPIVersion

class MqttGateway:
    """
    Adaptador de infraestructura para MQTT.
    Gestiona la conexión, suscripción y publicación de mensajes.
    Delega la lógica de negocio al EdgeProcessor.
    """

    def __init__(self, broker_address: str, processor):
        self._processor = processor
        self._broker_address = broker_address
        self._client = mqtt.Client(callback_api_version=CallbackAPIVersion.VERSION2)
        self._client.on_connect = self._on_connect
        self._client.on_message = self._on_message

    def _on_connect(self, client, userdata, flags, rc):
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