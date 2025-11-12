#pymqttusb-tk

Permet la connexion d'un microprocesseur branché sur un port usb vers un serveur MQTT.<br />

L'affichage graphique permet de configurer le broker <br />
Contenu du fichier "arduino_mqtt_data.json" :<br />

-----------<br />

Le topic de réception sera : salle/KEY/out<br />

Le topic d'envoi sera : salle/KEY/in<br />

Les protocoles possibles sont "wss" websockets sécurisés avec login et mot de passe ( pas de certificat)
ou "tcp" pour ssl avec login et mot de passe ( pas de certificats client) <br />

Lancement du programme :<br />

	py -m pymqttusb-tk.main <br />

<br />

