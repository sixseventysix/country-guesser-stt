# 🌍 Country Guesser with Speech Recognition

A fun speech-to-text game that challenges you to name as many countries as possible using your voice! Optimized for Apple Silicon (M4) with local Whisper inference.

## Features

- 🎤 **Real-time speech recognition** using OpenAI Whisper
- 🚀 **M4 Neural Engine optimization** for fast inference
- 🌍 **195 UN-recognized countries** to guess
- ⏱️ **Customizable timer** (1, 3, 5, or 10 minutes)
- 🗺️ **Visual country tracking** with real-time updates
- 📱 **Responsive design** for desktop and mobile

## Quick Setup

### 1. Install Dependencies

```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On macOS/Linux

# Install requirements
pip install -r requirements.txt

# Install FFmpeg (required for Whisper audio processing)
brew install ffmpeg  # On macOS with Homebrew
```

### 2. Create Project Structure

```bash
mkdir country-guesser
cd country-guesser

# Create the main Python file
# Copy the FastAPI backend code into main.py

# Create static directory and HTML file
mkdir static
# Copy the HTML frontend code into static/index.html

# Copy requirements.txt
```

### 3. Run the Application

```bash
python main.py
```

The server will start on `http://localhost:8000`

## How to Play

1. **Click "Start Game"** and allow microphone access
2. **Choose your duration** (1, 3, 5, or 10 minutes)
3. **Say country names aloud** clearly into your microphone
4. **Watch countries light up** as you guess them correctly
5. **Try to beat your high score!**

## Performance Optimization

### M4 Neural Engine Usage
The app automatically detects and uses your M4's Neural Engine through PyTorch's MPS backend:
- **Whisper model**: Uses `base` model for optimal speed/accuracy balance
- **Device detection**: Automatically uses MPS when available
- **Real-time processing**: 2-second audio chunks for continuous recognition

### Troubleshooting

**Microphone not working?**
- Ensure browser has microphone permissions
- Check System Preferences > Security & Privacy > Microphone

**Slow performance?**
- The first inference may be slow (model loading)
- Subsequent predictions should be much faster on M4
- Consider using `tiny` model for even faster inference (edit line in main.py)

**Countries not recognized?**
- Speak clearly and at moderate pace
- The app supports many country name variations (USA, America, UK, Britain, etc.)
- Check the transcription box to see what's being heard

## Customization

### Change Whisper Model
In `main.py`, modify the model size:
```python
model = whisper.load_model("base", device=device)  # Options: tiny, base, small, medium, large
```

### Add More Country Aliases
Edit the `COUNTRY_ALIASES` dictionary in `main.py` to add more alternative names.

### Modify Game Duration
Default durations can be changed in the HTML frontend dropdown.

## Technical Details

- **Backend**: FastAPI with WebSocket support
- **Speech Recognition**: OpenAI Whisper (local inference)
- **Frontend**: Vanilla JavaScript with modern CSS
- **Audio Processing**: Web Audio API with WebRTC
- **Real-time Communication**: WebSocket for low-latency audio streaming

## Requirements

- **Python 3.8+**
- **macOS** (for M4 optimization, but works on other platforms)
- **Modern browser** with microphone support
- **FFmpeg** for audio processing

## License

MIT License - Feel free to modify and distribute!

---

**Pro Tips:**
- Practice with common country pronunciations
- Use full country names for better recognition
- The app recognizes partial matches (e.g., "Korea" matches both North and South Korea)
- Try different accents - Whisper is quite robust!