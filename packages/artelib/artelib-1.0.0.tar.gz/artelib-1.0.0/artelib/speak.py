import pyttsx3
engine = pyttsx3.init()

def say(text: str, speed: int = 180):
    """
    Saying text with speed\n
    text - required\n
    speed - default 180
    """

    engine.setProperty('rate', speed)

    engine.say(text)
    engine.runAndWait()