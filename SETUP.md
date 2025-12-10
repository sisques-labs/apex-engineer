# ApexEngineer Setup Guide

## Prerequisites

1. **Python 3.8+** installed
2. **Assetto Corsa** with shared memory enabled
3. **AI Model**: Choose one:
   - **GPT4All** (recommended - no server needed, works out of the box)
   - **Ollama** (alternative - requires server running)
4. **Microphone** (optional but recommended for voice input)

## Installation Steps

### 1. Clone and Install Dependencies

```bash
# Clone the repository
git clone https://github.com/sisques-labs/apex-engineer.git
cd apex-engineer

# Create virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Choose Your AI Model

#### Option A: GPT4All (Recommended - No Server Needed)

GPT4All is included in the requirements and works immediately after installation. The first time you run the app, it will automatically download the model.

**Advantages:**

- No separate server to run
- Works out of the box
- Lower latency (no network calls)
- More privacy (fully local)

**Configuration:**

```yaml
ai:
  model: "gpt4all"
  model_name: "ggml-gpt4all-j-v1.3-groovy.bin" # Default model
  # Available models: ggml-gpt4all-j-v1.3-groovy.bin, mistral-7b-instruct-v0.1.Q4_0.gguf, etc.
  temperature: 0.7
  max_tokens: 150
  n_threads: 4 # Adjust based on your CPU cores
```

**Available GPT4All Models:**

- `ggml-gpt4all-j-v1.3-groovy.bin` (default, ~4GB, fast)
- `mistral-7b-instruct-v0.1.Q4_0.gguf` (better quality, ~4GB)
- `orca-mini-3b-gguf2-q4_0.gguf` (smaller, faster, ~2GB)

#### Option B: Ollama (Alternative)

Download and install Ollama from [https://ollama.ai](https://ollama.ai)

After installation, pull a model:

```bash
ollama pull llama2
# or
ollama pull mistral
```

Start Ollama server:

```bash
ollama serve
```

**Configuration:**

```yaml
ai:
  model: "ollama"
  model_name: "llama2" # Change to your preferred model
  endpoint: "http://localhost:11434"
  temperature: 0.7
  max_tokens: 150
```

### 3. Configure ApexEngineer

Edit `config.yaml` to match your setup:

```yaml
ai:
  model: "gpt4all" # or "ollama"
  model_name: "ggml-gpt4all-j-v1.3-groovy.bin" # For GPT4All: model file name
  # For Ollama: model name like "llama2", "mistral"

voice:
  push_to_talk_key: "SPACE" # Change if needed
  stt_enabled: true
  tts_enabled: false # Set to true for voice responses
```

### 4. Enable Assetto Corsa Shared Memory

In Assetto Corsa:

1. Go to Options → General
2. Enable "Shared Memory" or "Enable shared memory for apps"
3. Save settings

### 5. Run ApexEngineer

**If using GPT4All:**

```bash
python main.py
# First run will download the model automatically (~4GB)
```

**If using Ollama:**

```bash
# Make sure Ollama is running first
ollama serve

# Then run ApexEngineer
python main.py
```

## Troubleshooting

### "Could not connect to Assetto Corsa telemetry"

- Make sure Assetto Corsa is running
- Verify shared memory is enabled in AC settings
- On Windows, ensure you have proper permissions
- The app will run in mock mode for development/testing

### "AI module is not available"

**For GPT4All:**

- Check that GPT4All is installed: `pip install gpt4all`
- First run will download the model automatically (check internet connection)
- Verify the model name in config.yaml matches an available model
- Check available models: Visit [GPT4All Models](https://gpt4all.io/index.html)

**For Ollama:**

- Make sure Ollama is running: `ollama serve`
- Check that the endpoint in config.yaml matches your Ollama setup
- Verify the model name exists: `ollama list`

### Audio/STT Issues

- Install system audio dependencies:
  - **macOS**: `brew install portaudio`
  - **Linux**: `sudo apt-get install portaudio19-dev`
  - **Windows**: Usually included with Python packages
- Check microphone permissions in system settings
- Try specifying `microphone_index` in config.yaml if you have multiple microphones

### Keyboard Issues (Push-to-Talk)

- On Linux, you may need to run with sudo for keyboard access
- Try a different key if SPACE doesn't work
- Check that no other application is capturing the key

## Development Mode

The application includes mock telemetry data for development. You can test the AI interaction without running Assetto Corsa by:

1. Running `python main.py`
2. The app will show a warning about telemetry but continue with mock data
3. You can still test voice interaction and AI responses

## Next Steps

- Customize the AI prompt in `src/ai/ollama_client.py` or `src/ai/gpt4all_client.py`
- Add support for additional racing simulators
- Integrate with steering wheel buttons for push-to-talk
- Enhance telemetry analysis and recommendations
