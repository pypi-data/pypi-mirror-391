from cryptography.fernet import Fernet
from upss import client
from upss.models import Package, Types
from upss.security import cryptographer

key = Fernet.generate_key()

data = {
    "msg": cryptographer.encrypt_data("Hi", "utf-8", key)
}

for connection in client.connect("upss://localhost:1234", encoding="utf-8", key=key):
    connection.send(Package("/", Types.SEND, data))
    print(connection.get())
    # data = {"audio": }
    # connection.send()
