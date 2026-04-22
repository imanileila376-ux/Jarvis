import speech_recognition as sr
import pyaudio
import audioop
import time

# ────────────────────────────────────────────────────────────────
# SETTINGS
# ────────────────────────────────────────────────────────────────

CLAP_THRESHOLD = 3000

recognizer = sr.Recognizer()
recognizer.energy_threshold = 300
recognizer.dynamic_energy_threshold = True
recognizer.pause_threshold = 1.0

# ────────────────────────────────────────────────────────────────
# LISTEN ONCE
# ────────────────────────────────────────────────────────────────

def listen() -> str:
    """Listen once and return text"""
    with sr.Microphone() as source:
        print("🎤 Listening...")
        recognizer.adjust_for_ambient_noise(
            source, duration=0.3
        )
        try:
            audio = recognizer.listen(
                source,
                timeout=6,
                phrase_time_limit=20
            )
            print("🔄 Processing...")
            text = recognizer.recognize_google(audio)
            return text
        except sr.WaitTimeoutError:
            return ""
        except sr.UnknownValueError:
            return ""
        except Exception as e:
            print(f"Error: {e}")
            return ""

# ────────────────────────────────────────────────────────────────
# CONTINUOUS LISTEN
# ────────────────────────────────────────────────────────────────

def listen_continuous(
    callback,
    stop_words=None,
    is_speaking_flag=None
):
    """
    Keep listening continuously.
    callback: function called with each text
    stop_words: list of words to stop loop
    is_speaking_flag: [bool] True when Jarvis talking
    """
    if stop_words is None:
        stop_words = ["quit", "exit", "bye"]

    if is_speaking_flag is None:
        is_speaking_flag = [False]

    print("\n🎤 Continuous voice mode active...")
    print("Just talk naturally!\n")

    while True:
        try:
            # Wait if Jarvis is speaking
            while is_speaking_flag[0]:
                time.sleep(0.1)

            with sr.Microphone() as source:
                print("🎤 Your turn...")
                recognizer.adjust_for_ambient_noise(
                    source, duration=0.2
                )

                try:
                    audio = recognizer.listen(
                        source,
                        timeout=8,
                        phrase_time_limit=20
                    )

                    print("🔄 Processing...")
                    text = recognizer.recognize_google(
                        audio
                    )

                    if not text:
                        continue

                    print(f"Bonche: {text}")

                    # Check stop words
                    if any(
                        w in text.lower()
                        for w in stop_words
                    ):
                        return text

                    # Send to callback
                    should_continue = callback(text)

                    if not should_continue:
                        return text

                except sr.WaitTimeoutError:
                    continue

                except sr.UnknownValueError:
                    continue

                except Exception as e:
                    print(f"Listen error: {e}")
                    time.sleep(1)
                    continue

        except KeyboardInterrupt:
            return "quit"

# ────────────────────────────────────────────────────────────────
# CLAP DETECTION
# ────────────────────────────────────────────────────────────────

def wait_for_clap() -> bool:
    """Wait for double clap to wake Jarvis"""
    p = pyaudio.PyAudio()
    stream = p.open(
        format=pyaudio.paInt16,
        channels=1,
        rate=44100,
        input=True,
        frames_per_buffer=1024
    )

    print("👏 Waiting for double clap...")

    clap_count = 0
    last_clap_time = 0
    is_clapping = False

    try:
        while True:
            data = stream.read(
                1024,
                exception_on_overflow=False
            )
            volume = audioop.rms(data, 2)
            current_time = time.time()

            if volume > CLAP_THRESHOLD:
                if not is_clapping:
                    is_clapping = True
                    if (current_time - last_clap_time
                            < 1.5):
                        clap_count += 1
                        print(f"👏 Clap {clap_count}!")
                    else:
                        clap_count = 1
                        print("👏 Clap 1!")
                    last_clap_time = current_time

                    if clap_count >= 2:
                        stream.stop_stream()
                        stream.close()
                        p.terminate()
                        return True
            else:
                is_clapping = False

    except KeyboardInterrupt:
        stream.stop_stream()
        stream.close()
        p.terminate()
        return False