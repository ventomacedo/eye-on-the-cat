# 🐱 Sistema de Detecção de Gatos com Blur de Placas

Um sistema avançado de vigilância por câmera IP que detecta gatos em tempo real, borra automaticamente placas de veículos para privacidade e integra-se com dispositivos inteligentes Tuya para automação.

## ✨ Funcionalidades Principais

- 🎥 **Captura de vídeo RTSP** - Suporte para múltiplas câmeras IP simultâneas
- 🐱 **Detecção de gatos em tempo real** - Usando YOLO11 com alta precisão
- 📸 **Captura de fotos** - Salva automaticamente quando detecta gatos
- 🎬 **Gravação de vídeos** - Registra eventos de detecção com timestamp
- 🚗 **Detecção e blur de placas** - Borra placas de veículos para privacidade
- 💡 **Controle de luzes inteligentes** - Integração com dispositivos Tuya (acionamento via detecção)
- 🔊 **Áudio repelente** - Toca som ao detectar gato, com cooldown entre disparos
- 🖼️ **Processamento de arquivos locais** - Processa imagens e vídeos salvos localmente
- 🔧 **Configuração flexível** - Todas as opções via arquivo `.env`
- 🖥️ **Suporte multiplataforma** - Funciona em macOS, Linux e Windows (previne sleep no macOS via `caffeinate`)

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

Todos os dispositivos Tuya (lâmpadas) são configurados via `TUYA_LIGHTS`, um array JSON.
Cada dispositivo precisa de `id`, `key` (chave local) e `ip`; `version` é opcional (padrão `3.3`):

```env
TUYA_LIGHTS = '[
  {"id": "id-lampada-1", "key": "chave-lampada-1", "ip": "192.168.1.20", "version": 3.3},
  {"id": "id-lampada-2", "key": "chave-lampada-2", "ip": "192.168.1.21", "version": 3.3}
]'
```

Quando um gato é detectado com confiança suficiente, `turnOnAllLights()` aciona
todos os dispositivos carregados de `TUYA_LIGHTS`.

#### Áudio repelente

```env
CAT_REPELLENT_AUDIO = 'shiii.mp3'  # Padrão: shiiiii.mp3
```

Tocado a cada detecção de gato (confiança > 0.50), independente de haver
`TuyaController` configurado. Reprodução com cooldown de 15s entre disparos
(volume 2.0). Player usado por plataforma:
- **macOS**: `afplay` (já vem no sistema)
- **Linux/Windows**: `ffplay`, `mpg123` ou `mpv` (primeiro disponível), ex.:

```bash
sudo apt install ffmpeg   # fornece ffplay
```

Se nenhum player compatível for encontrado, ou o arquivo de áudio não existir,
o sistema registra um aviso no console e segue sem tocar o som.

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
│   └── processor.py            # Processador de arquivos locais (blur, imagem, vídeo)
├── storage/
│   ├── __init__.py
│   └── capture.py              # Gerenciamento de armazenamento (fotos/vídeos)
├── integrations/
│   ├── __init__.py
│   ├── tuya.py                 # Integração com dispositivos Tuya
│   └── audio.py                # Áudio repelente (CatRepellentAudio)
└── captures/
    └── <camera>/<AAAAMMDD>/
        ├── images/              # Fotos capturadas
        └── videos/              # Vídeos gravados
```

## 🎯 Uso

### 1. Monitoramento em Tempo Real

Com `CAMERAS` preenchido em `.env`, basta executar:

```bash
python main.py
```

Cada câmera roda em processo próprio (`CameraWorker`), com seu `Detector` e
`TuyaController` inicializados internamente. No macOS, `avoidSleep()` chama
`caffeinate` automaticamente para impedir o sistema de dormir enquanto a
aplicação está ativa.

### 2. Processamento de Arquivo Local

Para processar uma imagem ou vídeo salvos localmente:

```python
from detection import Detector, FileProcessor
from integrations.tuya import TuyaController

# Inicializar
tuya_controller = TuyaController()
detector = Detector(tuyaController=tuya_controller)
processor = FileProcessor(detector)

# Processar imagem
processor.processImage("entrada.jpg", "saida.jpg")

# Processar vídeo
processor.processVideo("entrada.mp4", "saida.mp4")
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
1. Se `TuyaController` estiver configurado, aciona todas as luzes de `TUYA_LIGHTS` via `turnOnAllLights()`
2. Toca o áudio repelente (respeitando cooldown de 15s), independente do Tuya estar configurado
3. Registra o evento nos logs
4. Captura foto/vídeo (se habilitado)

### Captura RTSP

- Leitura de frames roda em thread própria (`_grab_loop`), sempre mantendo o frame mais recente disponível para `read()`
- Após 10 falhas de leitura consecutivas, reconecta automaticamente ao stream
- Transporte RTSP fixo em UDP, com buffers ajustados para reduzir latência

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
Success: 2 dispositivos foram carregados.
🐱 detectado! id=Jardim label=cat conf=0.75
💡 Luzes acionadas via Tuya.
Áudio repelente reproduzido: shiii.mp3
Movimento detectado, salvando...
🐱 Gato detectado! Gravando 10 segundos em: captures/Jardim/20260827/videos/142530.mp4
✅ Vídeo salvo em: captures/Jardim/20260827/videos/142530.mp4. Próxima gravação disponível em 15s.
```

## 🔐 Privacidade e Segurança

- ✅ **Blur de placas**: Todas as placas são automaticamente borradas
- ✅ **Variáveis de ambiente**: Credenciais não ficam no código
- ✅ **Sem dados na nuvem**: Processamento local (sem envios remotos)
- ⚠️ **Armazene `.env` com segurança**: Adicione ao `.gitignore`

## 📝 Logs

Todos os eventos são impressos no console:
- `🐱 detectado!` - Detecção de gato
- `💡 Luzes acionadas via Tuya.` - Ação Tuya executada
- `Áudio repelente reproduzido:` - Som repelente tocado
- `Movimento detectado, salvando...` - Captura de imagem
- `🐱 Gato detectado! Gravando...` / `✅ Vídeo salvo em:` - Gravação de vídeo
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
