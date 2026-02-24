# NeuroVault Quick Start Guide

## 🚀 Getting Started in 3 Steps

### Step 1: Setup (First time only)
**Windows Users:**
```bash
setup.bat
```

**Linux/Mac Users:**
```bash
python -m venv whisper_env
source whisper_env/bin/activate
pip install -r requirements.txt
```

This takes 5-10 minutes on first run as it downloads ML models (~2GB).

---

### Step 2: Run the Application

**Windows Users:**
```bash
run.bat
```

**Linux/Mac Users:**
```bash
source whisper_env/bin/activate
python neurovault_app.py
```

---

### Step 3: Start Recording

1. Click **▶ Start Recording**
2. Speak clearly into your microphone
3. Click **⏹ Stop & Transcribe**
4. Wait for processing (5-10 seconds)
5. View your transcript with sentiment and speaker analysis!

---

## 📚 Key Features

| Feature | How to Use |
|---------|-----------|
| **Record Speech** | Click "▶ Start Recording" → Speak → "⏹ Stop & Transcribe" |
| **View Past Recordings** | Click "📚 Load Memory" to see all previous transcripts |
| **Search Memories** | Click "🔍 Semantic Search" and type what you're looking for |
| **Save Transcripts** | Click "💾 Save Transcript" to export as text file |
| **Continuous Recording** | Click "🔄 Continuous: OFF" to auto-restart after each recording |

---

## ✨ What Happens Behind the Scenes

When you record:

1. **🎙 Recording** (orange) - Capturing audio from microphone
2. **🧠 Processing** (yellow) - Running AI models:
   - Speech → Text (Whisper)
   - Emotion detection (Sentiment)
   - Speaker identification (Diarization)
   - Creating memory embeddings
3. **✅ Complete** (green) - Ready for next recording

Results include:
- **Transcript** - What was said
- **Sentiment** - Emotion (Positive/Neutral/Negative with certainty)
- **Speakers** - How many people spoke

---

## 🔍 Semantic Search Explained

Traditional search: Finds keywords
**Semantic Search**: Finds meaning

**Example:**
- Record: "I had a terrible meeting with my boss about the budget"
- Later search: "Work conflict"
- Result: ✅ Finds the meeting even though you said "terrible" not "conflict"

Uses AI to understand context, not just keywords.

---

## 🛠️ Troubleshooting

**Problem: "No audio recorded"**
- Check microphone is connected
- Check Windows audio settings
- Run: `python -c "import sounddevice; print(sounddevice.query_devices())"`

**Problem: Models downloading very slowly**
- First run requires 2GB download (Whisper, Transformers, etc)
- Use a faster internet connection
- Models cache after first use

**Problem: Speaker diarization not working**
- This feature is optional and may not work on all systems
- Application still works without it
- Check console for errors

**Problem: Application crashes**
- Make sure you installed all dependencies: `pip install -r requirements.txt`
- Ensure you're using Python 3.11+
- Check you have 4GB+ RAM available

---

## 📦 Building Standalone Executable (Advanced)

Want to distribute as .exe without Python required?

**Windows:**
```bash
build_exe.bat
```

**Linux/Mac:**
```bash
python build_exe.py
```

Result: `dist/NeuroVault.exe` (Windows) or `dist/NeuroVault` (Linux)

---

## 💡 Tips & Tricks

1. **Better transcription**: Minimize background noise
2. **Continuous mode**: Great for conversation logging (turn it ON)
3. **Search quality**: Longer transcripts → Better search results
4. **Memory export**: All data saved in `memory_history.json` (backup it!)
5. **Privacy**: All processing happens locally - no cloud uploads

---

## 🎓 Understanding the Output

### Transcript
```
TRANSCRIPT:
Hello, I am Sai Pavan. I had a great meeting today...

SENTIMENT: 
POSITIVE (87.34%)

SPEAKERS: 
2 speakers detected
```

### Semantic Search Results
```
🔎 TOP SEMANTIC MATCHES FOR: "Work discussion"

#1 - Similarity: 92.45%
[2026-02-24 14:41:43]
Text: Hello, I am Sai Pavan. I had a terrible meeting...
Sentiment: NEGATIVE (78.90%)
```

Similarity score closer to 100% = More related to your search

---

## 📞 Need Help?

1. Check README.md for full documentation
2. Check console output for error messages
3. Ensure all dependencies installed: `pip install -r requirements.txt`
4. Try reinstalling: `pip install --upgrade -r requirements.txt`

---

## 🎯 Quick Reference

| Button | Function |
|--------|----------|
| ▶ Start Recording | Begin capturing audio |
| ⏹ Stop & Transcribe | End recording and process |
| 💾 Save Transcript | Export current text |
| 📚 Load Memory | See all past transcripts |
| 🔍 Semantic Search | Find similar memories |
| 🔄 Continuous | Auto-restart mode |

---

## ✅ You're Ready!

That's it! You now have a personal AI voice memory system.

**Next Steps:**
1. Run `run.bat` to start
2. Record something
3. Try semantic search
4. Enable continuous mode

Enjoy! 🚀

