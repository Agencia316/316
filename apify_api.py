import os
from dotenv import load_dotenv
from apify_client import ApifyClient

load_dotenv()

APIFY_API_TOKEN = os.getenv("APIFY_API_TOKEN")


def init_apify():
    client = ApifyClient(APIFY_API_TOKEN)
    return client


def test_connection(client):
    user = client.user("me").get()
    return user


if __name__ == "__main__":
    client = init_apify()
    print("Conectando a API do Apify...")

    user = test_connection(client)
    print(f"Conectado com sucesso!")
    print(f"Usuario: {user.get('username', 'N/A')}")
    print(f"Email: {user.get('email', 'N/A')}")
    print(f"Plano: {user.get('plan', {}).get('id', 'N/A')}")
