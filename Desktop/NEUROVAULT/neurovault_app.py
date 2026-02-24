import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import sounddevice as sd
import numpy as np
from scipy.io.wavfile import write
from faster_whisper import WhisperModel
from transformers import pipeline
from sentence_transformers import SentenceTransformer
import faiss
import os
import datetime
import threading
import json
import queue
import time

# Try to import pyannote for speaker diarization
try:
    import torch
    from pyannote.audio import Pipeline
    DIARIZATION_AVAILABLE = True
except:
    DIARIZATION_AVAILABLE = False

# ---------------- SETTINGS ----------------
sample_rate = 16000
recording = False
continuous_mode = False
audio_data = []
history_file = "memory_history.json"
faiss_index_file = "faiss_index.bin"
transcription_queue = queue.Queue()

# Initialize models
print("Initializing Whisper model...")
whisper_model = WhisperModel("base", device="cpu", compute_type="int8")

print("Initializing Sentiment Analysis model...")
sentiment_pipeline = pipeline("sentiment-analysis", model="distilbert-base-uncased-finetuned-sst-2-english")

print("Initializing Sentence Transformer model...")
embedding_model = SentenceTransformer('all-MiniLM-L6-v2')

# Initialize FAISS index
embedding_dim = 384  # all-MiniLM-L6-v2 output dimension
faiss_index = faiss.IndexFlatL2(embedding_dim)
faiss_data = []  # Store metadata alongside FAISS

if os.path.exists(faiss_index_file):
    try:
        faiss_index = faiss.read_index(faiss_index_file)
    except:
        faiss_index = faiss.IndexFlatL2(embedding_dim)

# Load existing FAISS data
if os.path.exists(history_file):
    try:
        with open(history_file, "r", encoding="utf-8") as f:
            faiss_data = json.load(f)
    except:
        faiss_data = []

# Initialize speaker diarization if available
diarization_pipeline = None
if DIARIZATION_AVAILABLE:
    try:
        print("Initializing Speaker Diarization model...")
        diarization_pipeline = Pipeline.from_pretrained("pyannote/speaker-diarization-3.0", use_auth_token=False)
    except:
        print("Warning: Speaker diarization model not available")
        DIARIZATION_AVAILABLE = False

# ---------------- DARK THEME ----------------
BG_COLOR = "#121212"
BTN_COLOR = "#1f1f1f"
TEXT_COLOR = "#00ffcc"
ACCENT_COLOR = "#00ff88"
STATUS_RECORDING = "#ff9500"
STATUS_PROCESSING = "#ffcc00"
STATUS_COMPLETE = "#00ff00"

# ---------------- AUDIO CALLBACK ----------------
def audio_callback(indata, frames, time, status):
    if recording:
        audio_data.append(indata.copy())

# ---------------- LIVE TRANSCRIPTION THREAD ----------------
def live_transcription_worker():
    """Process audio in chunks and perform live transcription"""
    global recording, audio_data
    
    chunk_duration = 4  # seconds
    chunk_samples = chunk_duration * sample_rate
    last_transcribed = 0
    
    while recording:
        if len(audio_data) > 0:
            total_samples = sum(len(chunk) for chunk in audio_data)
            
            if total_samples - last_transcribed >= chunk_samples:
                try:
                    # Get audio up to now
                    audio_array = np.concatenate(audio_data, axis=0)
                    
                    # Save temporary WAV for transcription
                    temp_filename = "_temp_chunk.wav"
                    write(temp_filename, sample_rate, audio_array.astype(np.float32))
                    
                    # Transcribe
                    segments, _ = whisper_model.transcribe(temp_filename)
                    transcript = ""
                    for segment in segments:
                        transcript += segment.text + " "
                    
                    if transcript.strip():
                        transcription_queue.put(("live", transcript.strip()))
                    
                    # Clean up
                    if os.path.exists(temp_filename):
                        os.remove(temp_filename)
                    
                    last_transcribed = total_samples
                except Exception as e:
                    print(f"Live transcription error: {e}")
        
        time.sleep(1)

# ---------------- SPEAKER DIARIZATION ----------------
def apply_speaker_diarization(audio_array, filename):
    """Apply speaker diarization to audio"""
    if not DIARIZATION_AVAILABLE or diarization_pipeline is None:
        print("Speaker diarization not available")
        return None
    
    try:
        # Run diarization
        diarization = diarization_pipeline(filename)
        
        # Convert diarization to speaker labels
        speakers = {}
        for turn, _, speaker in diarization.itertracks(yield_label=True):
            start_time = turn.start
            end_time = turn.end
            speakers[(start_time, end_time)] = speaker
        
        return speakers
    except Exception as e:
        print(f"Diarization error: {e}")
        return None

# ---------------- SENTIMENT ANALYSIS ----------------
def get_sentiment(text):
    """Analyze sentiment of text"""
    try:
        result = sentiment_pipeline(text[:512])  # Limit to 512 chars
        if result:
            label = result[0]['label']
            score = result[0]['score']
            return f"{label} ({score*100:.2f}%)"
        return "NEUTRAL"
    except Exception as e:
        print(f"Sentiment analysis error: {e}")
        return "UNKNOWN"

# ---------------- EMBEDDING GENERATION ----------------
def generate_embedding(text):
    """Generate embedding for text using sentence-transformers"""
    try:
        embedding = embedding_model.encode(text, convert_to_numpy=True)
        return embedding.astype('float32')
    except Exception as e:
        print(f"Embedding error: {e}")
        return np.zeros(embedding_dim, dtype='float32')

# ---------------- START RECORDING ----------------
def start_recording():
    global recording, audio_data, stream, live_thread
    transcript_box.delete(1.0, tk.END)
    audio_data = []
    recording = True

    stream = sd.InputStream(
        samplerate=sample_rate,
        channels=1,
        callback=audio_callback
    )
    stream.start()

    # Start live transcription thread
    live_thread = threading.Thread(target=live_transcription_worker, daemon=True)
    live_thread.start()

    status_label.config(text="🎙 Recording...", fg=STATUS_RECORDING)
    update_ui_from_queue()

# ---------------- STOP RECORDING & PROCESS ----------------
def stop_recording():
    global recording, stream
    
    if not recording:
        return
    
    recording = False
    stream.stop()
    stream.close()
    
    if len(audio_data) == 0:
        status_label.config(text="No audio recorded!", fg="red")
        return
    
    status_label.config(text="🧠 Processing...", fg=STATUS_PROCESSING)
    root.update()
    
    # Start processing in background thread
    process_thread = threading.Thread(target=process_recording, daemon=True)
    process_thread.start()

def process_recording():
    """Process the recorded audio in background"""
    global audio_data
    
    try:
        # Concatenate audio data
        audio_array = np.concatenate(audio_data, axis=0)
        filename = "recorded.wav"
        write(filename, sample_rate, audio_array.astype(np.float32))
        
        # Transcribe full audio
        status_label.config(text="📝 Transcribing...", fg=STATUS_PROCESSING)
        root.update()
        
        segments, info = whisper_model.transcribe(filename)
        
        transcript = ""
        for segment in segments:
            transcript += segment.text + " "
        
        transcript = transcript.strip()
        
        # Get sentiment
        status_label.config(text="😊 Analyzing Sentiment...", fg=STATUS_PROCESSING)
        root.update()
        
        sentiment = get_sentiment(transcript)
        
        # Speaker diarization (optional)
        speakers_info = "N/A"
        if DIARIZATION_AVAILABLE:
            status_label.config(text="👥 Identifying Speakers...", fg=STATUS_PROCESSING)
            root.update()
            speaker_dict = apply_speaker_diarization(audio_array, filename)
            if speaker_dict:
                speakers_info = f"{len(set(speaker_dict.values()))} speakers detected"
        
        # Generate embedding
        embedding = generate_embedding(transcript)
        
        # Update UI
        transcript_box.delete(1.0, tk.END)
        transcript_box.insert(tk.END, f"TRANSCRIPT:\n{transcript}\n\n")
        transcript_box.insert(tk.END, f"SENTIMENT: {sentiment}\n")
        transcript_box.insert(tk.END, f"SPEAKERS: {speakers_info}\n")
        
        # Save to memory
        save_to_memory(transcript, sentiment, speakers_info, embedding)
        
        status_label.config(text="✅ Complete", fg=STATUS_COMPLETE)
        
        # Cleanup
        if os.path.exists(filename):
            os.remove(filename)
        
        # Handle continuous mode
        if continuous_mode:
            root.after(1000, start_recording)
    
    except Exception as e:
        status_label.config(text=f"❌ Error: {str(e)[:30]}", fg="red")
        print(f"Processing error: {e}")

# ---------------- UPDATE UI FROM QUEUE ----------------
def update_ui_from_queue():
    """Check transcription queue and update UI"""
    try:
        while True:
            msg_type, content = transcription_queue.get_nowait()
            if msg_type == "live":
                transcript_box.delete(1.0, tk.END)
                transcript_box.insert(tk.END, f"LIVE: {content}")
    except queue.Empty:
        pass
    
    if recording:
        root.after(100, update_ui_from_queue)

# ---------------- SAVE TRANSCRIPT ----------------
def save_transcript_to_file():
    text = transcript_box.get("1.0", tk.END).strip()
    if not text:
        messagebox.showwarning("Warning", "No transcript to save.")
        return

    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"transcript_{timestamp}.txt"

    with open(filename, "w", encoding="utf-8") as f:
        f.write(text)

    messagebox.showinfo("Saved", f"Transcript saved as {filename}")

# ---------------- MEMORY STORAGE ----------------
def save_to_memory(text, sentiment="NEUTRAL", speakers="N/A", embedding=None):
    """Save transcript with metadata to memory"""
    global faiss_index, faiss_data
    
    entry = {
        "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "text": text,
        "sentiment": sentiment,
        "speakers": speakers
    }
    
    # Load existing data
    if os.path.exists(history_file):
        try:
            with open(history_file, "r", encoding="utf-8") as f:
                data = json.load(f)
        except:
            data = []
    else:
        data = []
    
    data.append(entry)
    
    # Save to JSON
    with open(history_file, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)
    
    # Add to FAISS index
    if embedding is None:
        embedding = generate_embedding(text)
    
    faiss_data.append({
        "timestamp": entry["timestamp"],
        "text": text,
        "sentiment": sentiment,
        "speakers": speakers
    })
    
    faiss_index.add(np.array([embedding]))
    
    # Save FAISS index
    try:
        faiss.write_index(faiss_index, faiss_index_file)
    except:
        pass

def load_memory():
    """Load and display memory history"""
    if not os.path.exists(history_file):
        messagebox.showinfo("Memory", "No history found.")
        return

    try:
        with open(history_file, "r", encoding="utf-8") as f:
            data = json.load(f)
    except:
        messagebox.showerror("Error", "Failed to load memory.")
        return

    transcript_box.delete(1.0, tk.END)
    
    transcript_box.insert(tk.END, "=== MEMORY HISTORY ===\n\n")
    
    for entry in reversed(data):  # Show newest first
        transcript_box.insert(tk.END, f"[{entry['timestamp']}]\n")
        transcript_box.insert(tk.END, f"Text: {entry.get('text', 'N/A')}\n")
        transcript_box.insert(tk.END, f"Sentiment: {entry.get('sentiment', 'N/A')}\n")
        transcript_box.insert(tk.END, f"Speakers: {entry.get('speakers', 'N/A')}\n")
        transcript_box.insert(tk.END, "-" * 60 + "\n\n")

# ---------------- SEMANTIC SEARCH ----------------
def semantic_search_window():
    """Open semantic search dialog"""
    search_window = tk.Toplevel(root)
    search_window.title("Semantic Memory Search")
    search_window.geometry("800x500")
    search_window.configure(bg=BG_COLOR)
    
    tk.Label(search_window, text="Enter search query:", fg=TEXT_COLOR, bg=BG_COLOR).pack(pady=10)
    
    query_entry = tk.Entry(search_window, width=80, bg="#1f1f1f", fg=TEXT_COLOR, insertbackground="white")
    query_entry.pack(pady=10, padx=20)
    
    results_box = scrolledtext.ScrolledText(
        search_window,
        wrap=tk.WORD,
        width=95,
        height=20,
        bg="#1e1e1e",
        fg=TEXT_COLOR,
        insertbackground="white"
    )
    results_box.pack(padx=20, pady=10)
    
    def perform_search():
        query = query_entry.get().strip()
        if not query:
            messagebox.showwarning("Warning", "Please enter a search query.")
            return
        
        if len(faiss_data) == 0:
            messagebox.showinfo("Info", "No memories to search.")
            return
        
        # Generate query embedding
        query_embedding = generate_embedding(query)
        
        # Search
        distances, indices = faiss_index.search(np.array([query_embedding]), min(3, len(faiss_data)))
        
        results_box.delete(1.0, tk.END)
        results_box.insert(tk.END, f"🔎 TOP SEMANTIC MATCHES FOR: \"{query}\"\n\n")
        
        for i, idx in enumerate(indices[0]):
            if idx < len(faiss_data):
                result = faiss_data[idx]
                similarity = 1 / (1 + distances[0][i])  # Convert L2 distance to similarity
                
                results_box.insert(tk.END, f"#{i+1} - Similarity: {similarity*100:.2f}%\n")
                results_box.insert(tk.END, f"[{result['timestamp']}]\n")
                results_box.insert(tk.END, f"Text: {result['text'][:200]}...\n")
                results_box.insert(tk.END, f"Sentiment: {result['sentiment']}\n")
                results_box.insert(tk.END, "=" * 75 + "\n\n")
    
    def copy_results():
        """Copy search results to clipboard"""
        content = results_box.get(1.0, tk.END)
        root.clipboard_clear()
        root.clipboard_append(content)
        messagebox.showinfo("Success", "Results copied to clipboard!")
    
    button_frame = tk.Frame(search_window, bg=BG_COLOR)
    button_frame.pack(pady=10)
    
    tk.Button(button_frame, text="Search", command=perform_search, bg=BTN_COLOR, fg=TEXT_COLOR).pack(side=tk.LEFT, padx=5)
    tk.Button(button_frame, text="Copy Results", command=copy_results, bg=BTN_COLOR, fg=TEXT_COLOR).pack(side=tk.LEFT, padx=5)
    
    query_entry.focus()

# -------- CONTINUOUS MODE -------- 
def toggle_continuous():
    global continuous_mode
    continuous_mode = not continuous_mode

    if continuous_mode:
        continuous_button.config(text="🔄 Continuous: ON", fg=ACCENT_COLOR)
    else:
        continuous_button.config(text="🔄 Continuous: OFF", fg=TEXT_COLOR)

# ---------------- UI ----------------
root = tk.Tk()
root.title("🧠 NeuroVault Voice Intelligence System")
root.geometry("1000x700")
root.configure(bg=BG_COLOR)

# Title
title = tk.Label(root, text="🧠 NeuroVault Voice Intelligence System", 
                 font=("Arial", 20, "bold"), fg=ACCENT_COLOR, bg=BG_COLOR)
title.pack(pady=15)

# Button frame 1 - Recording controls
button_frame1 = tk.Frame(root, bg=BG_COLOR)
button_frame1.pack(pady=5)

start_btn = tk.Button(button_frame1, text="▶ Start Recording", 
                      command=start_recording, bg=BTN_COLOR, fg=TEXT_COLOR, 
                      font=("Arial", 10), padx=10, pady=5)
start_btn.grid(row=0, column=0, padx=8)

stop_btn = tk.Button(button_frame1, text="⏹ Stop & Transcribe", 
                     command=stop_recording, bg=BTN_COLOR, fg=TEXT_COLOR,
                     font=("Arial", 10), padx=10, pady=5)
stop_btn.grid(row=0, column=1, padx=8)

save_btn = tk.Button(button_frame1, text="💾 Save Transcript", 
                     command=save_transcript_to_file, bg=BTN_COLOR, fg=TEXT_COLOR,
                     font=("Arial", 10), padx=10, pady=5)
save_btn.grid(row=0, column=2, padx=8)

memory_btn = tk.Button(button_frame1, text="📚 Load Memory", 
                       command=load_memory, bg=BTN_COLOR, fg=TEXT_COLOR,
                       font=("Arial", 10), padx=10, pady=5)
memory_btn.grid(row=0, column=3, padx=8)

search_btn = tk.Button(button_frame1, text="🔍 Semantic Search", 
                       command=semantic_search_window, bg=BTN_COLOR, fg=TEXT_COLOR,
                       font=("Arial", 10), padx=10, pady=5)
search_btn.grid(row=0, column=4, padx=8)

# Button frame 2 - Mode controls
button_frame2 = tk.Frame(root, bg=BG_COLOR)
button_frame2.pack(pady=5)

continuous_button = tk.Button(button_frame2, text="🔄 Continuous: OFF", 
                               command=toggle_continuous, bg=BTN_COLOR, fg=TEXT_COLOR,
                               font=("Arial", 10), padx=10, pady=5)
continuous_button.pack(side=tk.LEFT, padx=8)

status_label = tk.Label(root, text="🟢 Ready", fg=STATUS_COMPLETE, bg=BG_COLOR, font=("Arial", 11, "bold"))
status_label.pack(pady=5)

# Transcript display
label = tk.Label(root, text="📝 Transcript & Analysis", fg=ACCENT_COLOR, bg=BG_COLOR, font=("Arial", 10, "bold"))
label.pack()

transcript_box = scrolledtext.ScrolledText(
    root,
    wrap=tk.WORD,
    width=110,
    height=22,
    bg="#1e1e1e",
    fg=TEXT_COLOR,
    insertbackground="white",
    font=("Courier", 9)
)
transcript_box.pack(padx=20, pady=10, fill=tk.BOTH, expand=True)

root.mainloop()