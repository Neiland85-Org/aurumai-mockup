
try:
    import paho.mqtt.client as mqtt  # type: ignore
except (ImportError, ModuleNotFoundError):
    class mqtt:
        @staticmethod
        def Client(*args, **kwargs):
            class Stub:
                def __setattr__(self, name, value):
                    object.__setattr__(self, name, value)
                def connect(self, host, port=1883, keepalive=60, **kwargs):
                    print(f"[stub mqtt] connect to {host}:{port}")
                def loop_forever(self):
                    print("[stub mqtt] loop_forever called (no-op)")
                def publish(self, topic, payload=None, qos=0, retain=False, **kwargs):
                    print(f"[stub mqtt] publish to {topic}: {payload}")
                def subscribe(self, topic, qos=0):
                    print(f"[stub mqtt] subscribe to {topic}")
            return Stub()

import json

# Asegura que el root del proyecto esté en sys.path para importar correctamente 'src' si es necesario.


EdgeProcessor = None


class MqttGateway:
    """
    Adaptador de infraestructura para MQTT.
    Gestiona la conexión, suscripción y publicación de mensajes.
    Delega la lógica de negocio al EdgeProcessor.
    """

    def __init__(self, broker_address: str, processor):
        self._processor = processor
        self._broker_address = broker_address
        # Inicializar con CallbackAPIVersion.VERSION2 si existe, si no sin argumento
        # Inicializar el cliente MQTT correctamente indentado y sin argumentos extra
        self._client = mqtt.Client()
        try:
            self._client.on_connect = self._on_connect
            self._client.on_message = self._on_message
        except Exception:
            pass

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
            if self._processor:
                enriched_payload = self._processor.process_telemetry(payload)
            else:
                enriched_payload = None

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