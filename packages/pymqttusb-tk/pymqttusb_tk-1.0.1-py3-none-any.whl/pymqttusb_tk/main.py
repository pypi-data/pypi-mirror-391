import tkinter as tk
from tkinter import ttk, scrolledtext
import threading, time, ssl, random, string
import paho.mqtt.client as mqtt
import serial
import serial.tools.list_ports


def randomword(length):
    lettresEtChiffres = string.ascii_letters + string.digits
    return ''.join(random.choice(lettresEtChiffres) for i in range(length))


class MQTTSerialBridgeApp:
    def __init__(self, master):
        self.master = master
        self.master.title("FABLAB UniCA - Publication MQTT")
        self.master.geometry("800x740")

        # --- Titre principal ---
        title_label = tk.Label(
            master,
            text="FABLAB UniCA - Publication MQTT",
            font=("Helvetica", 18, "bold"),
            fg="blue"
        )
        title_label.pack(pady=5)

        # --- Frame Configuration ---
        frame_conf = ttk.LabelFrame(master, text="Configuration")
        frame_conf.pack(fill="x", padx=10, pady=5)

        # Ligne 1 : Port série + Baudrate
        ttk.Label(frame_conf, text="Port série :").grid(row=0, column=0, sticky="w", padx=2, pady=2)
        self.port_box = ttk.Combobox(frame_conf, width=20, values=self.list_serial_ports())
        self.port_box.grid(row=0, column=1, sticky="w")  # ← aligné à gauche
        if self.port_box["values"]:
            self.port_box.set(self.port_box["values"][0])
        else:
            self.port_box.set("Aucun port trouvé")

        # Styles personnalisés pour les boutons
        style = ttk.Style()
        style.theme_use("clam")  # <-- permet de colorer le fond

        style.configure("Connect.TButton",# vert clair
                background="#b3ffb3",
                foreground="black",
                relief="raised")
        style.map("Connect.TButton",
          background=[('active', '#99ff99')])

        style.map("Connect.TButton", background=[('active', '#99ff99')])

        style.configure("Disconnect.TButton",
                background="#ffb3b3",
                foreground="black",
                relief="raised")
        style.map("Disconnect.TButton",
          background=[('active', '#ff9999')])


       # Bouton Actualiser
        ttk.Button(frame_conf, text="🔄 Actualiser", command=self.refresh_ports).grid(row=0, column=2, sticky="w", padx=(5, 2))

        # Sous-frame pour Baudrate (collé au bouton)
        baud_frame = ttk.Frame(frame_conf)
        baud_frame.grid(row=0, column=3, sticky="w", padx=(0, 0))

        ttk.Label(baud_frame, text="Baudrate :").pack(side="left", padx=(6, 3))
        self.baud_entry = ttk.Entry(baud_frame, width=10)
        self.baud_entry.insert(0, "9600")
        self.baud_entry.pack(side="left")

        # Ligne 2 : Broker + Port MQTT
        ttk.Label(frame_conf, text="Broker MQTT :").grid(row=1, column=0, sticky="w", padx=2)
        self.broker_entry = ttk.Entry(frame_conf, width=25)
        self.broker_entry.insert(0, "mqtt.univ-cotedazur.fr")
        self.broker_entry.grid(row=1, column=1, columnspan=2, sticky="w")  # ← aligné à gauche

        # Sous-frame pour Port (collé au broker)
        port_frame = ttk.Frame(frame_conf)
        port_frame.grid(row=1, column=3, sticky="w", padx=(5, 0))
        ttk.Label(port_frame, text="Port :").pack(side="left", padx=(2, 4))
        self.mqtt_port_entry = ttk.Entry(port_frame, width=8)
        self.mqtt_port_entry.insert(0, "443")
        self.mqtt_port_entry.pack(side="left")
        
        """  ttk.Label(frame_conf, text="Port :").grid(row=1, column=3, sticky="w", padx=2)
        self.mqtt_port_entry = ttk.Entry(frame_conf, width=8)
        self.mqtt_port_entry.insert(0, "443")
        self.mqtt_port_entry.grid(row=1, column=4, sticky="w")  # ← aligné à gauche """

        # Ligne 3 : Salle / KEY
        ttk.Label(frame_conf, text="Salle :").grid(row=2, column=0, sticky="w", padx=2)
        self.salle_entry = ttk.Entry(frame_conf, width=15)
        self.salle_entry.insert(0, "FABLAB_21_22")
        self.salle_entry.grid(row=2, column=1, sticky="w")   # aligné à gauche

        ttk.Label(frame_conf, text="Clé (KEY) :").grid(row=2, column=2, sticky="w", padx=2)
        self.key_entry = ttk.Entry(frame_conf, width=30)
        self.key_entry.insert(0, "TEST")
        self.key_entry.grid(row=2, column=3, sticky="w")     # aligné à gauche


        # Ligne 4 : Identifiants MQTT
        ttk.Label(frame_conf, text="Utilisateur MQTT :").grid(row=3, column=0, sticky="w", padx=2)
        self.user_entry = ttk.Entry(frame_conf, width=15)
        self.user_entry.insert(0, "fablab2122")
        self.user_entry.grid(row=3, column=1, sticky="w")    # aligné à gauche

        ttk.Label(frame_conf, text="Mot de passe :").grid(row=3, column=2, sticky="w", padx=2)
        self.pwd_entry = ttk.Entry(frame_conf, width=30, show="*")  # largeur augmentée pour alignement
        self.pwd_entry.grid(row=3, column=3, sticky="w")            # aligné à gauche

        # Ligne 5 : Protocole
        ttk.Label(frame_conf, text="Protocole :").grid(row=4, column=0, sticky="w", padx=2)
        self.proto_box = ttk.Combobox(frame_conf, values=["mqtt", "mqtts", "ws", "wss"], width=10)
        self.proto_box.set("wss")
        self.proto_box.grid(row=4, column=1, sticky="w")

        #Button
        ttk.Button(frame_conf, text="Connecter", style="Connect.TButton", command=self.start_connection).grid(row=4, column=3, padx=5)
        ttk.Button(frame_conf, text="Déconnecter", style="Disconnect.TButton", command=self.stop_connection).grid(row=4, column=4, padx=5)

        # --- Frame Publication manuelle ---
        frame_pub = ttk.LabelFrame(master, text="Publication manuelle MQTT")
        frame_pub.pack(fill="x", padx=10, pady=5)

        ttk.Label(frame_pub, text="Topic :").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        self.manual_topic = ttk.Entry(frame_pub, width=40)
        self.manual_topic.insert(0, "FABLAB_21_22/TEST/out/")
        self.manual_topic.grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(frame_pub, text="Données :").grid(row=1, column=0, sticky="w", padx=5, pady=5)
        self.manual_msg = ttk.Entry(frame_pub, width=60)
        self.manual_msg.grid(row=1, column=1, padx=5, pady=5)

        ttk.Button(frame_pub, text="📤 Publier", command=self.publish_manual).grid(row=0, column=2, rowspan=2, padx=10)

        # --- Zone de Logs ---
        frame_log = ttk.LabelFrame(master, text="Console / Journal")
        frame_log.pack(fill="both", expand=True, padx=10, pady=10)

        ttk.Button(frame_log, text="🧹 Effacer le journal", command=self.clear_log).pack(anchor="e", padx=5, pady=3)

        self.log_area = scrolledtext.ScrolledText(frame_log, height=20, state='disabled', wrap=tk.WORD)
        self.log_area.pack(fill="both", expand=True, padx=5, pady=5)

        # --- Variables internes ---
        self.client = None
        self.ser = None
        self.running = False
        self.thread_serial = None

    # --- Détection des ports disponibles ---
    def list_serial_ports(self):
        ports = serial.tools.list_ports.comports()
        return [p.device for p in ports]

    def refresh_ports(self):
        ports = self.list_serial_ports()
        self.port_box["values"] = ports if ports else ["Aucun port trouvé"]
        if ports:
            self.port_box.set(ports[0])
            self.log(f"🔄 Ports détectés : {', '.join(ports)}")
        else:
            self.port_box.set("Aucun port trouvé")
            self.log("⚠️ Aucun port série détecté.")

    # --- Connexion principale ---
    def start_connection(self):
        if self.running:
            self.log("⚠️ Déjà connecté.")
            return

        broker = self.broker_entry.get()
        port = int(self.mqtt_port_entry.get())
        salle = self.salle_entry.get()
        key = self.key_entry.get()
        username = self.user_entry.get()
        password = self.pwd_entry.get()
        proto = self.proto_box.get()
        serial_port = self.port_box.get()
        baud = int(self.baud_entry.get())

        if not password.strip():
            self.log("❌ Indiquez le mot de passe pour la connexion MQTT !")
            return

        if serial_port == "Aucun port trouvé" or not serial_port.strip():
            self.log("❌ Vérifier la connexion de votre port série !")
            return

        self.topic_in = f"{salle}/{key}/in/"
        self.topic_out = f"{salle}/{key}/out/"
        protocol = "websockets" if proto in ["ws", "wss"] else "tcp"

        # Configuration MQTT
        self.client = mqtt.Client(client_id=randomword(8),
                                  clean_session=True,
                                  protocol=mqtt.MQTTv311,
                                  transport=protocol)
        self.client.username_pw_set(username, password)
        if proto in ["mqtts", "wss"]:
            self.client.tls_set(tls_version=ssl.PROTOCOL_TLSv1_2)

        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        self.client.connected_flag = False

        try:
            self.ser = serial.Serial(serial_port, baud, timeout=1)
            self.log(f"✅ Port série {serial_port} ouvert ({baud} bauds)")
        except Exception:
            self.log("❌ Vérifier la connexion de votre port série !")
            return

        self.running = True
        threading.Thread(target=self.serial_loop, daemon=True).start()
        threading.Thread(target=self.mqtt_loop, args=(broker, port), daemon=True).start()

    # --- Boucles principales ---
    def mqtt_loop(self, broker, port):
        try:
            self.client.connect(broker, port, 60)
            self.client.loop_forever()
        except Exception as e:
            self.log(f"❌ Erreur MQTT : {e}")

    def serial_loop(self):
        while self.running:
            try:
                data = self.ser.readline().decode().strip()
                if data and self.client.connected_flag:
                    self.client.publish(self.topic_out, data)
                    self.log(f"📤 Envoi MQTT → {self.topic_out} : {data}")
            except Exception as e:
                self.log(f"⚠️ Erreur lecture série : {e}")
            time.sleep(0.1)

    # --- Publication manuelle ---
    def publish_manual(self):
        if not self.client or not self.client.connected_flag:
            self.log("⚠️ Client MQTT non connecté.")
            return

        topic = self.manual_topic.get().strip()
        msg = self.manual_msg.get().strip()

        if not topic or not msg:
            self.log("⚠️ Indiquez un topic et un message avant de publier.")
            return

        self.client.publish(topic, msg)
        self.log(f"✉️ Publication manuelle → {topic} : {msg}")

        # Efface le champ message après envoi
        self.manual_msg.delete(0, tk.END)

    # --- Callbacks MQTT ---
    def on_connect(self, client, userdata, flags, rc):
        if rc == 0:
            client.connected_flag = True
            client.subscribe(self.topic_in)
            self.log(f"🔗 Connecté au broker et abonné à {self.topic_in}")
        else:
            self.log(f"❌ Erreur connexion MQTT : code {rc}")

    def on_message(self, client, userdata, msg):
        data = msg.payload.decode()
        self.log(f"📥 Réception MQTT ← {msg.topic} : {data}")
        try:
            self.ser.write((data + "\n").encode())
        except:
            self.log("⚠️ Erreur écriture vers série")

    def stop_connection(self):
        self.running = False
        try:
            if self.client:
                self.client.disconnect()
                self.log("🔌 Déconnexion MQTT")
            if self.ser and self.ser.is_open:
                self.ser.close()
                self.log("🛑 Port série fermé")
        except Exception as e:
            self.log(f"⚠️ Erreur arrêt : {e}")

    def log(self, msg):
        self.log_area.config(state='normal')
        self.log_area.insert(tk.END, msg + "\n")
        self.log_area.yview(tk.END)
        self.log_area.config(state='disabled')

    def clear_log(self):
        self.log_area.config(state='normal')
        self.log_area.delete("1.0", tk.END)
        self.log_area.config(state='disabled')
        self.log("🧹 Journal effacé.")


# --- Exécution ---
if __name__ == "__main__":
    root = tk.Tk()
    app = MQTTSerialBridgeApp(root)
    root.mainloop()

