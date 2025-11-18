import base64
import json
import os
import sys
import _thread
from kafka import KafkaConsumer, KafkaProducer
# Importamos excepciones específicas para mejor manejo de fallos de conexión
from kafka.errors import NoBrokersAvailable, KafkaTimeoutError 
from .loggs import Loggs


class KafkaBase:
    """
        Base del microservicio que se aplica para
        la comunicacion con kafka
    """
    # Topico de conexion
    __TOPIC = ''
    # Direccion de kafka
    __KAFKAHOSTS = ''
    # Instancia del consumer
    __CONSUMER = None
    # Instancia del producer
    __PRODUCER = None
    # Logs de la aplicacion
    logs = Loggs('Service')

    def __init__(self, topic, kafkaHosts, name=None):
        self.logs.info('Iniciando la conexion los servidores de KAFKA')
        # Asignar el topico de conexion
        self.__TOPIC = topic
        # Asginar el hosts de kafka
        self.__KAFKAHOSTS = kafkaHosts
        
        # Conectar a Kafka Producer
        self.__connectProducer()
        # Conectar a Kafka Consumer
        self.__connectConsumer()
        
        # Si la conexión falló, lo indicamos.
        if self.__PRODUCER is None or self.__CONSUMER is None:
            self.logs.warning("Inicialización de Kafka incompleta. La funcionalidad de mensajería estará deshabilitada si la conexión no se pudo establecer.")


    def __connectConsumer(self):
        """
            Metodo para realizar la conexion al cosumer de kafka.
        """
        topics = [self.__TOPIC, "validateConnection"]
        CONSUMER_GROUP = os.environ.get('CONSUMER_GROUP', self.__TOPIC)

        # Conexion a kafka
        try:
            self.__CONSUMER = KafkaConsumer(
                *topics,
                group_id=CONSUMER_GROUP,
                auto_offset_reset='earliest',
                enable_auto_commit=True,
                bootstrap_servers=self.__KAFKAHOSTS,
                value_deserializer=self.__b64_to_json
            )
        # Manejo seguro: Capturamos fallos de conexión (NoBrokersAvailable, DNS, etc.)
        except (NoBrokersAvailable, KafkaTimeoutError, Exception) as e:
            self.logs.error('Ocurrio un error al conectar con Kafka Consumer (IGNORADO EN CI/CD)')
            self.logs.error(f'Detalle: {e}')
            self.__CONSUMER = None # Asegura que la instancia quede como None
            return # Termina la ejecución del método para evitar errores

        # Notificar que se encuentra conectado
        self.logs.info("Escuchando el topico {} en el Kafka {}".format(
            self.__TOPIC, ','.join(self.__KAFKAHOSTS)))

        # Escuchar todos los posibles eventos
        # Este ciclo for solo se iniciará si self.__CONSUMER no es None
        for msg in self.__CONSUMER:
            try:
                # Solo procesar los mensajes del topico
                if msg.topic == self.__TOPIC:
                    _thread.start_new_thread(self._message, (msg.value,))
                    # self._message(msg.value)
            except Exception as e:
                print(e)

    def _message(self, msg):
        """
            Metodo para el procesamiento de mensajes de
            kafka.
        """
        pass

    def __connectProducer(self):
        """
            Metodo para realizar la conexion con el producer
            de kafka.
        """
        try:
            self.__PRODUCER = KafkaProducer(
                bootstrap_servers=self.__KAFKAHOSTS,
                value_serializer=self.__json_to_b64
            )
            self.logs.info('Conectado a kafka para enviar mensajes')
        # Manejo seguro: Capturamos fallos de conexión
        except (NoBrokersAvailable, KafkaTimeoutError, Exception) as e:
            self.logs.error('Ocurrio un error al conectar con el producer (IGNORADO EN CI/CD)')
            self.logs.error(f'Detalle: {e}')
            self.__PRODUCER = None # Asegura que la instancia quede como None
            
    def __json_to_b64(self, json_in):
        """
            Metodo que pasa un objecto a el formato necesario
            para su comunicacion
        """
        return base64.b64encode(str.encode(json.dumps(json_in)))

    def __b64_to_json(self, encoded):
        """
            Metodo que conviernte un base64 a dict
        """
        decoded = base64.b64decode(encoded)
        return json.loads(decoded.decode('utf-8'))

    def _send(self, topico, msj, idTransaction):
        """
            Metodo para el envio de datos a Kafka
        """
        # Verificación de seguridad: No enviar si el productor no se pudo inicializar
        if self.__PRODUCER is None:
             self.logs.warning("No se puede enviar mensaje. El productor de Kafka no está conectado.")
             return 
             
        try:
            self.__PRODUCER.send(topico, key=str.encode(
                str(idTransaction)), value=msj)
        except Exception as e:
            self.logs.error(f"Error al enviar mensaje a Kafka: {e}")
            # No se llama a sys.exit(-1) aquí
            
    def validateConnection(self):
        # Verificación de seguridad: Checar si ambos objetos existen antes de usarlos
        try:
            if self.__CONSUMER is None or self.__PRODUCER is None:
                 return False
                 
            self.__CONSUMER.topics()
            self.__PRODUCER.send('validateConnection', b'') 
            return True
        except Exception as e:
            return False