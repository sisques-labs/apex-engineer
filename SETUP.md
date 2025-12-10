# ApexEngineer Setup Guide

## Prerequisites

1. **Python 3.8+** installed
2. **Assetto Corsa** with shared memory enabled
3. **AI Model**: GPT4All (included - no server needed, works out of the box)
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

### 2. GPT4All Configuration

GPT4All is included in the requirements and works immediately after installation. The first time you run the app, it will automatically download the model.

**Advantages:**

- No separate server to run
- Works out of the box
- Lower latency (no network calls)
- More privacy (fully local)
- Completely autonomous - everything runs in your program

**Configuration:**

```yaml
ai:
  model_name: "mistral-7b-instruct-v0.1.Q4_0.gguf" # Recommended model
  model_path: null # Optional: custom path for GPT4All models
  temperature: 0.7
  max_tokens: 150
  n_threads: 4 # Adjust based on your CPU cores
```

**Available GPT4All Models:**

- `mistral-7b-instruct-v0.1.Q4_0.gguf` (recommended, ~4GB, best quality)
- `orca-mini-3b-gguf2-q4_0.gguf` (smaller, faster, ~2GB)
- `llama-2-7b-chat.Q4_0.gguf` (~4GB)

Check all available models at: [GPT4All Models](https://gpt4all.io/index.html)

### 3. Configure ApexEngineer

Edit `config.yaml` to match your setup:

```yaml
ai:
  model_name: "mistral-7b-instruct-v0.1.Q4_0.gguf" # GPT4All model file name
  model_path: null # Optional: custom path for GPT4All models
  temperature: 0.7
  max_tokens: 150
  n_threads: 4

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

```bash
python main.py
# First run will download the model automatically (~4GB)
# This may take a few minutes depending on your internet connection
```

## Troubleshooting

### "Could not connect to Assetto Corsa telemetry"

- Make sure Assetto Corsa is running
- Verify shared memory is enabled in AC settings
- On Windows, ensure you have proper permissions
- The app will run in mock mode for development/testing

### "AI module is not available"

- Check that GPT4All is installed: `pip install gpt4all`
- First run will download the model automatically (check internet connection)
- Verify the model name in config.yaml matches an available model
- Check available models: Visit [GPT4All Models](https://gpt4all.io/index.html)
- If a model fails to download (404 error), try a different model name from the list above

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

- Customize the AI prompt in `src/ai/gpt4all_client.py`
- Add support for additional racing simulators
- Integrate with steering wheel buttons for push-to-talk
- Enhance telemetry analysis and recommendations
