import speech_recognition as sr
from g2p_en import G2p
import numpy as np

# Initialize g2p for phoneme conversion
g2p = G2p()


def record_audio():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print("Please say the phrase...")
        audio = recognizer.listen(source)

    try:
        print("Recognizing...")
        text = recognizer.recognize_google(audio)
        print(f"You said: {text}")
        return text
    except sr.UnknownValueError:
        print("Could not understand the audio.")
        return None
    except sr.RequestError:
        print("Could not request results from the service.")
        return None


def text_to_phonemes(text):
    phonemes = g2p(text)
    return phonemes


def compare_phonemes(user_phonemes, target_phonemes):
    min_len = min(len(user_phonemes), len(target_phonemes))
    matches = sum(1 for i in range(min_len) if user_phonemes[i] == target_phonemes[i])
    return matches / max(len(user_phonemes), len(target_phonemes))


def evaluate_pronunciation(target_text, user_text):
    target_phonemes = text_to_phonemes(target_text)
    user_phonemes = text_to_phonemes(user_text)

    score = compare_phonemes(user_phonemes, target_phonemes)
    return score


def provide_feedback(score):
    if score > 0.8:
        print("Great job! Your pronunciation is excellent.")
    elif score > 0.5:
        print("Good effort! But you can improve on some words.")
    else:
        print("Keep practicing! Focus on pronouncing each word clearly.")


# Example usage
target_phrase = "I would like some coffee"
user_text = record_audio()

if user_text:
    score = evaluate_pronunciation(target_phrase, user_text)
    print(f"Pronunciation score: {score * 100:.2f}%")
    provide_feedback(score)
