import asyncio
import edge_tts
import pygame
import threading
import os
import uuid
import time

# ────────────────────────────────────────────────────────────────
# SETTINGS
# ────────────────────────────────────────────────────────────────

if not os.path.exists("temp"):
    os.makedirs("temp")

VOICE = "en-US-AndrewNeural"
RATE = "+15%"
PITCH = "-2Hz"

# Initialize pygame once at startup
try:
    pygame.mixer.pre_init(
        frequency=44100,
        size=-16,
        channels=2,
        buffer=512
    )
    pygame.mixer.init()
    pygame.init()
    print("🔊 Audio system ready")
except Exception as e:
    print(f"Audio init warning: {e}")

# ────────────────────────────────────────────────────────────────
# SPEAK
# ────────────────────────────────────────────────────────────────

def speak(text: str):
    """Make Jarvis speak"""
    clean = text.replace("*", "")
    clean = clean.replace("#", "")
    clean = clean.replace("-", "")
    clean = clean.replace("_", "")
    clean = clean.replace("=", "")
    clean = clean.replace("|", "")
    clean = clean.replace("✅", "done.")
    clean = clean.replace("🔧", "")
    clean = clean.replace("🚀", "")
    clean = clean.replace("👏", "")
    clean = clean.replace("🎤", "")
    clean = clean.replace("⏰", "")
    clean = clean.replace("🧠", "")
    clean = clean.replace("🎯", "")
    clean = clean.replace("💰", "")

    if len(clean) > 500:
        clean = clean[:500] + "... check screen for more."

    def run():
        asyncio.run(_speak_async(clean))

    thread = threading.Thread(target=run)
    thread.daemon = True
    thread.start()

async def _speak_async(text: str):
    unique_id = str(uuid.uuid4())[:8]
    output = f"temp/jarvis_{unique_id}.mp3"

    try:
        # Generate voice file
        communicate = edge_tts.Communicate(
            text,
            VOICE,
            rate=RATE,
            pitch=PITCH
        )
        await communicate.save(output)

        # Wait for file to be ready
        await asyncio.sleep(0.1)

        # Make sure mixer is ready
        if not pygame.mixer.get_init():
            pygame.mixer.init(
                frequency=44100,
                size=-16,
                channels=2,
                buffer=512
            )

        # Stop any currently playing audio
        if pygame.mixer.music.get_busy():
            pygame.mixer.music.stop()
            await asyncio.sleep(0.1)

        # Play audio
        pygame.mixer.music.load(output)
        pygame.mixer.music.play()

        # Wait for it to finish
        while pygame.mixer.music.get_busy():
            await asyncio.sleep(0.1)

        # Small pause after
        await asyncio.sleep(0.2)

    except Exception as e:
        print(f"Voice error: {e}")

    finally:
        # Clean up file
        try:
            if os.path.exists(output):
                os.remove(output)
        except:
            pass

# ────────────────────────────────────────────────────────────────
# CLEANUP
# ────────────────────────────────────────────────────────────────

def cleanup_temp():
    """Remove leftover audio files"""
    try:
        for f in os.listdir("temp"):
            if f.endswith(".mp3"):
                try:
                    os.remove(f"temp/{f}")
                except:
                    pass
    except:
        pass

# ────────────────────────────────────────────────────────────────
# VOICE CONTROLS
# ────────────────────────────────────────────────────────────────

def set_voice(voice_name: str):
    global VOICE
    VOICE = voice_name
    print(f"Voice changed to: {voice_name}")

def set_rate(rate: str):
    global RATE
    RATE = rate
    print(f"Speed: {rate}")

def set_pitch(pitch: str):
    global PITCH
    PITCH = pitch
    print(f"Pitch: {pitch}")

def list_voices():
    print("""
====================================
AVAILABLE MALE VOICES
====================================
American Male:
  en-US-AndrewNeural       Deep clear
  en-US-GuyNeural          Friendly
  en-US-ChristopherNeural  Professional
  en-US-EricNeural         Warm
  en-US-RogerNeural        Confident

British Male:
  en-GB-ThomasNeural       Smooth
  en-GB-RyanNeural         Deep

African Male:
  en-KE-ChilembaNeural     Kenyan
  en-NG-AbeoNeural         Nigerian
  en-ZA-LukeNeural         South African

Australian Male:
  en-AU-WilliamNeural      Aussie

HOW TO CHANGE:
  setvoice en-US-AndrewNeural
  setvoice en-KE-ChilembaNeural
  setvoice en-NG-AbeoNeural

SPEED:
  setrate +0%    Normal
  setrate +15%   Faster
  setrate -10%   Slower

PITCH:
  setpitch +0Hz   Normal
  setpitch -2Hz   Slightly deep
  setpitch -10Hz  Very deep
====================================
    """)