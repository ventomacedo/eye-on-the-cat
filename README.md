# 🐱 Sistema de Detecção de Gatos com Blur de Placas

Um sistema avançado de vigilância por câmera IP que detecta gatos em tempo real, borra automaticamente placas de veículos para privacidade e integra-se com dispositivos inteligentes Tuya para automação.

## ✨ Funcionalidades Principais

- 🎥 **Captura de vídeo RTSP** - Suporte para múltiplas câmeras IP simultâneas
- 🐱 **Detecção de gatos em tempo real** - Usando YOLO11 com alta precisão
- 📸 **Captura de fotos** - Salva automaticamente quando detecta gatos
- 🎬 **Gravação de vídeos** - Registra eventos de detecção com timestamp
- 🚗 **Detecção e blur de placas** - Borra placas de veículos para privacidade
- 💡 **Controle de luzes inteligentes** - Integração com dispositivos Tuya (acionamento via detecção)
- 🖼️ **Processamento de arquivos locais** - Processa imagens e vídeos salvos localmente
- 🔧 **Configuração flexível** - Todas as opções via arquivo `.env`
- 🖥️ **Suporte multiplataforma** - Funciona em macOS, Linux e Windows

## 📋 Pré-requisitos

- **Python 3.9+**
- **OpenCV** (cv2)
- **YOLO11** (Ultralytics)
- **tinytuya** (para integração Tuya - opcional)
- **python-dotenv**

### Requisitos do Hardware

- **Raspberry Pi 4** ou **GPU CUDA** para processamento eficiente
- **RAM**: Mínimo 4GB, recomendado 8GB+
- **Acesso à rede** para câmeras IP

## 🚀 Instalação

### 1. Clonar o repositório

```bash
git clone https://github.com/ventomacedo/eye-on-the-cat.git
cd eye-on-the-cat
```

### 2. Criar ambiente virtual

```bash
python -m venv venv
source venv/bin/activate  # macOS/Linux
# ou
venv\Scripts\activate  # Windows
```

### 3. Instalar dependências

```bash
pip install -r requirements.txt
```

### 4. Download dos modelos YOLO

Os modelos YOLO serão baixados automaticamente na primeira execução:
- `yolo11l.pt` - Modelo grande para detecção geral (inclui classe gato)
- `license_plates.pt` - Modelo especializado em detecção de placas

## ⚙️ Configuração

### 1. Criar arquivo `.env`

Copie `.env.example` para `.env` e preencha com suas informações:

```bash
cp .env.example .env
```

### 2. Variáveis de Ambiente

#### Câmeras IP

```env
# Credenciais de acesso às câmeras
USERNAME = 'admin'          # Usuário da câmera IP
PASSWORD = 'senha123'       # Senha da câmera IP
PORT = 554                  # Porta RTSP (padrão: 554)

# Lista de câmeras a monitorar (formato JSON)
CAMERAS = '[
  {"name": "Garagem", "ip": "192.168.1.100"},
  {"name": "Jardim", "ip": "192.168.1.101"},
  {"name": "Quintal", "ip": "192.168.1.102"}
]'
```

#### Processamento

```env
# Tipo de dispositivo para processamento
DEVICE_TYPE = 'cpu'         # Opções: 'cpu', 'cuda', 'mps' (Apple Silicon)

# Opções de captura
SHOW_WINDOW = False         # Mostrar janela de visualização
TAKE_PICTURE = True         # Capturar fotos quando detectar gato
TAKE_RECORD = True          # Gravar vídeos quando detectar gato
```

#### Integração Tuya (Opcional)

```env
# Configuração do dispositivo Tuya
TUYA_DEVICE_ID = 'seu-device-id'
TUYA_DEVICE_KEY = 'sua-chave-local'
TUYA_DEVICE_IP = '192.168.1.50'
TUYA_DEVICE_TYPE = 'outlet'  # 'outlet' ou 'bulb'
TUYA_LIGHT_DPS = 1            # DPS para controle de ligar/desligar
TUYA_DEVICE_VERSION = 3.3     # Versão do protocolo Tuya
```

Para acender várias lâmpadas, use `TUYA_LIGHTS` com um objeto para cada dispositivo.
Cada lâmpada precisa do próprio ID, chave local e IP:

```env
TUYA_LIGHTS = '[
  {"id": "id-lampada-1", "key": "chave-lampada-1", "ip": "192.168.1.20", "type": "bulb", "dps": 1, "version": 3.3},
  {"id": "id-lampada-2", "key": "chave-lampada-2", "ip": "192.168.1.21", "type": "bulb", "dps": 1, "version": 3.3}
]'
```

Quando `turn_on_lights()` ou `turn_on_varanda_lights()` for chamado, todos os
dispositivos configurados em `TUYA_LIGHTS` serão acionados. Se `TUYA_LIGHTS` estiver
vazio, o sistema usa as variáveis legadas `TUYA_DEVICE_*` para um único dispositivo.

#### Áudio repelente

```env
CAT_REPELLENT_AUDIO = 'shiiiii.mp3'
```

No Raspberry Pi/Linux, instale um reprodutor de áudio, por exemplo:

```bash
sudo apt install ffmpeg
```

O macOS usa `afplay` automaticamente. O volume do sistema operacional e do
amplificador também precisa estar alto.

## 📁 Estrutura do Projeto

```
eye-on-the-cat/
├── main.py                      # Ponto de entrada da aplicação
├── .env.example                 # Template de variáveis de ambiente
├── requirements.txt             # Dependências do projeto
├── camera/
│   ├── __init__.py
│   ├── rtsp.py                 # Gerenciamento de conexão RTSP
│   └── worker.py               # Worker multiprocesso por câmera
├── detection/
│   ├── __init__.py
│   ├── detector.py             # Motor de detecção (gatos + placas)
│   └── processor.py            # Processador de arquivos locais
├── storage/
│   ├── __init__.py
│   └── capture.py              # Gerenciamento de armazenamento (fotos/vídeos)
├── integrations/
│   └── tuya.py                 # Integração com dispositivos Tuya
├── images/
│   ├── Garagem/                # Fotos capturadas (Garagem)
│   ├── Jardim/                 # Fotos capturadas (Jardim)
│   └── Quintal/                # Fotos capturadas (Quintal)
└── captures/
    ├── Garagem/
    ├── Jardim/
    └── Quintal/
```

## 🎯 Uso

### 1. Monitoramento em Tempo Real

Descomente a seção de câmeras em `main.py`:

```python
# Descomente em main.py
if len(CAMERAS) > 0:
    for cam in CAMERAS:
        # Inicia workers para cada câmera
```

Execute:

```bash
python main.py
```

### 2. Processamento de Arquivo Local

Para processar uma imagem ou vídeo salvos localmente:

```python
from detection import Detector, FileProcessor
from integrations.tuya import TuyaController

# Inicializar
tuya_controller = TuyaController.from_env()
detector = Detector(tuyaController=tuya_controller)
processor = FileProcessor(detector)

# Processar imagem
processor.process_image("entrada.jpg", "saida.jpg")

# Processar vídeo
processor.process_video("entrada.mp4", "saida.mp4")
```

Ou edite `main.py`:

```python
# Em main.py, linha ~65
VIDEO_INPUT = "captures/Jardim/20260812/videos/captura-catito.mp4"
VIDEO_OUTPUT = "captures/Jardim/captura-catito.mp4"
```

### 3. Parar a Aplicação

- **Em tempo real**: Pressione `Q` na janela de visualização
- **Processamento de arquivo**: Aguarde até completar (fecha automaticamente)

## 🔍 Detalhes Técnicos

### Detecção de Gatos

- **Modelo**: YOLO11 Large (`yolo11l.pt`)
- **Classe COCO**: 15 (cat)
- **Tamanho de entrada**: 640x640
- **Confiança mínima**: 0.20 (detecção)
- **Confiança para disparo**: 0.50 (trigger de ações)

### Detecção de Placas

- **Modelo**: `license_plates.pt` (modelo customizado)
- **Confiança mínima**: 0.02
- **Processamento**: Blur Gaussiano com kernel 51x51
- **Privacidade**: Placas são borradas sem desenhar boxes de detecção

### Integração Tuya

Quando um gato é detectado com confiança > 0.50:
1. Aciona a luz da varanda via dispositivo Tuya
2. Registra o evento nos logs
3. Captura foto/vídeo (se habilitado)

## 🛠️ Troubleshooting

### Problema: "RTSP connection timeout"

**Solução**:
- Verifique a conectividade de rede com a câmera
- Confirme que USERNAME, PASSWORD e IP estão corretos
- Teste com ferramentas como `ffmpeg`:
  ```bash
  ffmpeg -rtsp_transport tcp -i "rtsp://user:pass@192.168.1.100:554/onvif1"
  ```

### Problema: "No module named 'cv2'"

**Solução**:
```bash
pip install opencv-python
```

### Problema: "CUDA out of memory"

**Solução**:
```env
DEVICE_TYPE = 'cpu'  # Mude para CPU
```

### Problema: Tuya não conecta

**Solução**:
- Verifique o IP local do dispositivo na rede
- Confirme a chave local (obtida via app Tuya)
- Tente resetar o dispositivo Tuya

## 📊 Saída Esperada

```
🔒 Prevenção de repouso do macOS ativa (caffeinate).
🎥 Iniciando câmera: Jardim
🐱 detectado! id=Jardim label=cat conf=0.75
💡 Luz da varanda acionada via Tuya.
📸 Capturando foto: images/Jardim/20260813_142530.jpg
🎬 Gravando vídeo: captures/Jardim/20260813_142530.mp4
```

## 🔐 Privacidade e Segurança

- ✅ **Blur de placas**: Todas as placas são automaticamente borradas
- ✅ **Variáveis de ambiente**: Credenciais não ficam no código
- ✅ **Sem dados na nuvem**: Processamento local (sem envios remotos)
- ⚠️ **Armazene `.env` com segurança**: Adicione ao `.gitignore`

## 📝 Logs

Todos os eventos são impressos no console:
- `🐱 detectado!` - Detecção de gato
- `💡 Luz... acionada` - Ação Tuya executada
- `📸 Capturando foto` - Captura de imagem
- `Placa detectada!` - Detecção de placa
- `Erro na detecção:` - Exceções capturadas

## 🤝 Contribuições

Melhorias e sugestões são bem-vindas! Principais áreas:

- Melhorar precisão de detecção de gatos em baixa iluminação
- Adicionar suporte a mais plataformas de automação (Home Assistant, etc.)
- Otimizar performance em dispositivos com poucos recursos
- Melhorar interface de visualização

## 🎓 Referências

- [Ultralytics YOLO](https://docs.ultralytics.com/)
- [OpenCV Documentation](https://docs.opencv.org/)
- [COCO Dataset Classes](https://gist.github.com/rcland12/dc48e1963268ff98c8b2c4543e7a9be8)
- [tinytuya Documentation](https://github.com/jasonacox/tinytuya)

---

**Desenvolvido com ❤️ para evitar que as rodas das nossas motos não seja xixizadas**
