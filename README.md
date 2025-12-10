# ApexEngineer

> Real-time AI race engineer for sim racing enthusiasts

[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/)

ApexEngineer is an innovative real-time AI race engineer designed for sim racing enthusiasts and professional drivers who want an immersive, data-driven racing experience. The core idea is to create a virtual engineer that communicates directly with the player, providing actionable insights about car performance, strategy, and telemetry during gameplay—just like a real Formula 1 engineer would in a race.

## 🎯 Core Concept

In modern motorsport, engineers monitor vast amounts of telemetry data in real time: lap times, tire temperature, fuel levels, gear selection, speed, and sector performance. ApexEngineer brings this same capability into sim racing by reading telemetry directly from games like Assetto Corsa, processing it through an AI model, and communicating with the driver via push-to-talk voice commands.

The virtual engineer can:

- **Monitor lap performance and sector times**
- **Alert the driver about tire wear, fuel status, and optimal shifts**
- **Recommend strategy changes based on real-time race conditions**
- **Provide contextual tips on braking, cornering, and acceleration**
- **Answer driver questions dynamically, creating a realistic team interaction**

## ✨ Key Features

### Real-Time Telemetry Analysis

ApexEngineer connects to Assetto Corsa's shared memory to retrieve live telemetry. It captures essential metrics such as speed, RPM, gear, tire temperatures, lap times, deltas, and fuel, and processes them instantly to provide meaningful feedback.

### Push-to-Talk Voice Interface

Players can interact with the AI engineer by holding a button (keyboard or wheel). While the button is pressed, the system records audio, converts it to text (STT), and sends it to the AI model. Upon release, the AI generates a response and delivers it back to the driver, optionally via text-to-speech.

### Local AI Model Support

To minimize latency and maximize privacy, ApexEngineer uses GPT4All, a lightweight local AI model that runs entirely within the application. Responses can be generated in under 200 milliseconds, ensuring instant feedback during high-speed gameplay without relying on cloud services or external servers.

### Dynamic Race Advice

The AI can interpret telemetry contextually and provide strategic recommendations, such as when to push, conserve fuel, pit strategies, and ideal lap targets. It can also track performance over time, comparing the current lap to the best lap and highlighting areas for improvement.

### Modular and Extensible Design

ApexEngineer is designed with modularity in mind. New telemetry sources, games, AI models, or TTS engines can be integrated easily, allowing the system to evolve and adapt to new technologies and racing simulations.

## 🏗️ Architecture Overview

The system is divided into clear modules:

- **Telemetry Reader**: Connects to Assetto Corsa shared memory to read live car data
- **Context Engine**: Processes telemetry, computes deltas, summaries, and prepares context for the AI model
- **AI Module**: A local LLM processes driver queries in real time, using telemetry context to generate precise, actionable advice
- **TTS Engine** (optional): Converts AI responses into spoken audio, enhancing immersion
- **Push-to-Talk Interface**: Captures driver input via keyboard or wheel buttons and triggers the AI communication cycle

```
Assetto Corsa Shared Memory
        ↓
Telemetry Reader (Python)
        ↓
Context Engine
        ↓
Local LLM (GPT4All)
        ↓
Optional TTS Engine
        ↓
Audio feedback to driver
```

## 🚀 Use Cases

- **Sim racing enthusiasts**: Get real-time coaching and performance feedback while racing in Assetto Corsa
- **Streamers and content creators**: Provide live AI commentary or tips during races for an engaging audience experience
- **Developers and AI researchers**: Experiment with low-latency AI interaction using live game data and local LLMs
- **Professional driver training**: Simulate real F1 engineering interaction for practice or virtual testing

## 📋 Requirements

- Python 3.8 or higher
- Assetto Corsa (with shared memory enabled)
- GPT4All (automatically installed and configured)
- Microphone for voice input (optional but recommended)

## 🔧 Installation

```bash
# Clone the repository
git clone https://github.com/sisques-labs/apex-engineer.git
cd apex-engineer

# Install dependencies
pip install -r requirements.txt

# Configure your local AI model
# See configuration section for details
```

## ⚙️ Configuration

Configure ApexEngineer by editing the configuration file:

```yaml
# config.yaml
ai:
  model_name: "mistral-7b-instruct-v0.1.Q4_0.gguf" # GPT4All model file name
  model_path: null # Optional: custom path for GPT4All models
  temperature: 0.7
  max_tokens: 150
  n_threads: 4 # Number of CPU threads for inference

telemetry:
  game: "assetto_corsa"
  update_rate: 10 # Hz

voice:
  push_to_talk_key: "SPACE" # Keyboard key or wheel button
  stt_enabled: true
  tts_enabled: false # Set to true for voice responses
```

## 🎮 Usage

1. **First run**: GPT4All will automatically download the model (~4GB) on first launch. This may take a few minutes.

2. **Launch Assetto Corsa** and start a session

3. **Run ApexEngineer**:

   ```bash
   python main.py
   ```

4. **During gameplay**:
   - Hold the push-to-talk button (SPACE by default) to ask questions
   - Release to receive AI feedback
   - Monitor telemetry analysis in real-time

## 🔮 Future Plans

ApexEngineer is a living project with ambitious growth potential:

- ✅ Support for additional racing simulators like Assetto Corsa Competizione, F1 2025, and iRacing
- ✅ Fully integrated TTS with realistic F1 radio effects
- ✅ Advanced strategy recommendations based on tire degradation, fuel stints, and race dynamics
- ✅ Integration with real steering wheels and controllers for authentic push-to-talk interaction
- ✅ Optional cloud AI for deep reasoning, while maintaining a local fallback for minimal latency

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request. For major changes, please open an issue first to discuss what you would like to change.

1. Fork the project
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Assetto Corsa community for shared memory documentation
- GPT4All team for local AI model support
- The sim racing community for inspiration and feedback

## 💬 Why ApexEngineer?

ApexEngineer bridges the gap between simulation and real-world motorsport engineering, bringing professional race engineering insights to the virtual cockpit. It combines AI, real-time telemetry, voice interfaces, and modular design to deliver a unique, immersive, and educational racing experience. Whether you want to improve lap times, optimize strategy, or simply enjoy the feeling of having your own F1 engineer in the car, ApexEngineer makes it possible.

---

**Made with ❤️ for the sim racing community**
