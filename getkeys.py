import sys
import warnings
# Desativa os avisos de SSL chatos do Mac no terminal
warnings.filterwarnings("ignore")

try:
    import tinytuya
except ImportError:
    print("Instale o TinyTuya primeiro rodando: pip install tinytuya")
    sys.exit()

print("--- EXTRATOR DE CHAVES NEO AVANT ---")
print("Digite os dados da sua conta do aplicativo Neo Avant do celular.\n")

email = input("Digite o E-mail do app Neo Avant: ")
senha = input("Digite a Senha do app Neo Avant: ")

# Cria a conexão forçando os servidores da nuvem Tuya/Avant nas Américas
try:
    cloud = tinytuya.Cloud(
        apiRegion="us", 
        apiKey="m96987376c663b9b",       # Chave pública global do ecossistema Tuya
        apiSecret="88f34f8c14a549db"    # Secret público global do ecossistema Tuya
    )
    
    # Faz o login simulando o aplicativo
    print("\nConectando aos servidores da Avant...")
    session = cloud.app_login(email, senha, countryCode="55", brand="neoavant")
    
    # Busca a lista de dispositivos atrelados ao seu e-mail
    dispositivos = cloud.getdevices()
    
    print("\n=== SEUS DISPOSITIVOS ENCONTRADOS ===")
    for dev in dispositivos:
        print(f"Nome: {dev.get('name')}")
        print(f"ID: {dev.get('id')}")
        print(f"Chave Local (key): {dev.get('local_key')}")
        print("-" * 40)
        
except Exception as e:
    print(f"\nOcorreu um erro na comunicação: {e}")
    print("Verifique se digitou o e-mail e senha do app do celular corretamente.")
