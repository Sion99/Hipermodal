# Hipermodal
**Hipermodal** is a Natural User Interface (NUI) that allows users to control Windows and macOS through gestures and voice commands.

## 📖 Overview
Hipermodal was developed to control the Hiperwall video wall controller.

### Key Features
- **Easy Setup**: Operates with just an RGB camera (e.g., webcam) and microphone input, without any additional devices.
- **Offline Operation**: Equipped with Mediapipe and OpenAI Whisper, allowing real-time operation without an internet connection.
- **Fast Response Time**: Ensures fast response times using multi-threading.

## 🚀 Installation and Execution
### Windows
- **Recommended**: Windows 10 or higher

**1. Clone the repository**:
```bash
git clone https://github.com/Sion99/Hipermodal.git hipermodal
cd hipermodal
```
**2. Create and activate a virtual environment**:
```bash
python -m venv .venv
.venv\Scripts\activate
```
**3. Install the required libraries**:
```bash
pip install -r requirements.txt
```
If your dependecies have conflict problems, use requirements-win.txt instead.

**4. Start the Python script**
```bash
python main.py
```

### macOS
- **Recommended**: macOS 10.15 or higher

For macOS, you can easily install it by copy and paste the following command in the terminal:
```bash
bash -c "$(curl -fsSL https://raw.githubusercontent.com/Sion99/Hipermodal/master/install.sh)" && cd hipermodal
```
After the installation, execute run.sh to start the program.
```bash
./run.sh
```
