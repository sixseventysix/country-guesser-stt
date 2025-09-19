import asyncio
import logging
from collections import deque
import numpy as np
import websockets
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
from faster_whisper import WhisperModel
import ahocorasick

# --- Configuration ---
logging.basicConfig(level=logging.INFO)

# --- Model Setup ---
MODEL_SIZE = "small.en"
try:
    model = WhisperModel(MODEL_SIZE, device="cpu", compute_type="int8")
    logging.info("Model loaded successfully.")
except Exception as e:
    logging.error(f"Fatal error loading model: {e}", exc_info=True)
    exit(1)

# --- NEW: Function to parse the structured country file ---
def load_and_build_automaton(filename="countries.txt"):
    """
    Parses a structured text file for countries and alternates,
    then builds and returns a configured Aho-Corasick automaton.
    """
    country_names = set()
    alternates = {}
    
    try:
        with open(filename, "r", encoding="utf-8") as f:
            current_section = None
            for line in f:
                line = line.strip()
                if not line:
                    continue
                if line == "[COUNTRIES]":
                    current_section = "countries"
                elif line == "[ALTERNATES]":
                    current_section = "alternates"
                else:
                    if current_section == "countries":
                        country_names.add(line)
                    elif current_section == "alternates":
                        if "->" in line:
                            abbr, full_name = [part.strip() for part in line.split("->", 1)]
                            alternates[abbr] = full_name
        
        logging.info(f"Loaded {len(country_names)} countries and {len(alternates)} alternates.")

    except FileNotFoundError:
        logging.error(f"FATAL: Country file '{filename}' not found. Please run the generator script first.")
        exit(1)

    # --- Build the Automaton ---
    A = ahocorasick.Automaton()
    # Add all official country names. When matched, they return themselves.
    for name in country_names:
        A.add_word(name, name)
    # Add all alternates. When matched, they return the official full name.
    for abbr, full_name in alternates.items():
        A.add_word(abbr, full_name)
    
    A.make_automaton()
    return A, country_names

# --- Load data and build the automaton at startup ---
A, COUNTRY_NAMES = load_and_build_automaton()


# --- FastAPI App ---
app = FastAPI()

@app.get("/")
async def get():
    with open("index.html", "r") as f:
        return HTMLResponse(f.read())

# ... The rest of the websocket and transcription logic remains exactly the same ...

async def matcher_loop(websocket: WebSocket, word_stream: deque, guessed_countries: set):
    """
    Continuously processes the word_stream using the Aho-Corasick automaton.
    """
    while True:
        try:
            text_to_search = " ".join(word_stream)
            last_match_end_index = 0

            # The `canonical_name` will be the official country name, whether an
            # abbreviation or the full name was spoken.
            for end_index, canonical_name in A.iter(text_to_search):
                if canonical_name not in guessed_countries:
                    guessed_countries.add(canonical_name)
                    logging.info(f"Correct guess: {canonical_name}")
                    await websocket.send_json({"type": "guess", "country": canonical_name})
                
                last_match_end_index = end_index + 1

            if last_match_end_index > 0:
                num_words_to_remove = text_to_search[:last_match_end_index].count(' ') + 1
                for _ in range(num_words_to_remove):
                    if word_stream:
                        word_stream.popleft()
            
            await asyncio.sleep(0.5)

        except (websockets.exceptions.ConnectionClosed, WebSocketDisconnect):
            logging.info("Matcher loop stopping due to client disconnect.")
            break
        except Exception as e:
            logging.error(f"Matcher loop error: {e}", exc_info=True)
            break


async def transcription_loop(audio_buffer: bytearray, word_stream: deque):
    """
    Transcribes audio and adds new words to the word_stream.
    """
    while True:
        try:
            await asyncio.sleep(1.0)
            if not audio_buffer:
                continue

            audio_np = np.frombuffer(audio_buffer, dtype=np.int16).astype(np.float32) / 32768.0
            audio_buffer.clear()

            segments, _ = model.transcribe(audio_np, beam_size=5)
            
            for segment in segments:
                clean_text = segment.text.lower().strip(" .?!,")
                if clean_text:
                    new_words = clean_text.split()
                    word_stream.extend(new_words)
                    logging.info(f"Added to stream: {new_words}. Current stream size: {len(word_stream)}")
        
        except asyncio.CancelledError:
            logging.info("Transcription loop cancelled.")
            break
        except Exception as e:
            logging.error(f"Transcription loop error: {e}", exc_info=True)
            break


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    
    audio_buffer = bytearray()
    guessed_countries = set()
    word_stream = deque(maxlen=500)

    transcription_task = asyncio.create_task(transcription_loop(audio_buffer, word_stream))
    matcher_task = asyncio.create_task(matcher_loop(websocket, word_stream, guessed_countries))
    
    try:
        while True:
            data = await websocket.receive_bytes()
            audio_buffer.extend(data)
    except (WebSocketDisconnect, websockets.exceptions.ConnectionClosedError):
        logging.info("Client disconnected.")
    finally:
        transcription_task.cancel()
        matcher_task.cancel()
        await asyncio.gather(transcription_task, matcher_task, return_exceptions=True)
        logging.info("WebSocket connection and tasks closed.")
