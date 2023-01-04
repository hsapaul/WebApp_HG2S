from transformers import AutoTokenizer, AutoModelForTokenClassification, pipeline
from transformers import pipeline
import time
import pandas as pd

tonic = [' c ', ' c# ', ' cb', ' d ', ' d# ', ' db ', ' e ', ' eb', ' f ', ' f# ', ' fb', ' g ', ' g# ', ' gb', ' a ', ' a# ', ' ab', ' b ', ' bb']
mode = ['major', 'minor', 'dorian', 'phrygian', 'lydian', 'mixolydian', 'aeolian', 'locrian']


def check_database_for_input(text_prompt):
    # Check for artists
    for index in range(1, 5):
        list_path = fr"C:\Users\franz\Desktop\WebApp (Werkstück)\Music Gallery (Database)\1. Natural Language Processing\artists\10000-MTV-Music-Artists-page-{index}.csv"
        df = pd.read_csv(list_path)
        namen = df["name"].tolist()
        for name in namen:
            if str(name).strip().lower() in text_prompt.lower():
                print(f"Found artist: {name}")
                #return name
    return "Not found"


# Filter musical information out of the text prompt
def check_for_key_and_bpm(text_prompt):

    song_info = {}

    # Check for musical key: Tonic (Grundton) and Mode (Tonart)
    for word in text_prompt.split():
        if f" {word.lower()} " in tonic:
            song_info["Tonic"] = word
            text_prompt = text_prompt.replace(f" {word} ", " ")
        if word.lower() in mode:
            song_info["Mode"] = word
            text_prompt = text_prompt.replace(word, "")

    # Check for BPM (Beats per Minute)
    bpm = [s for s in text_prompt.split() if s.isdigit() and int(s) in range(30, 300)]
    if len(bpm) > 0:
        bpm = bpm[0]
        song_info["BPM"] = bpm
        text_prompt = text_prompt.replace(bpm, "").replace("BPM", "")

    return text_prompt, song_info


# NLP - TOKEN CLASSIFICATION
def get_key_words(filtered_text):

    model_name = "vblagoje/bert-english-uncased-finetuned-pos"
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModelForTokenClassification.from_pretrained(model_name)

    ner = pipeline(
        task='ner',
        model=model_name,
        tokenizer=tokenizer,
        aggregation_strategy="simple"
    )
    result = ner(filtered_text)
    # Filtere alle Namen und Nomen aus dem Text
    keywords = [word['word'] for word in result if word["entity_group"] == "PROPN" or word["entity_group"] == "NOUN"]
    return keywords


# NLP - ZERO SHOT CLASSIFICATION
def word_categories(keywords):
    classifier = pipeline("zero-shot-classification",
                          model="facebook/bart-large-mnli")

    candidate_labels = ['Band', 'Singer', 'Vocalist', 'Rock Band', 'Composer', 'Pianist', 'Musician', 'DJ', 'Record Producer', 'Guitarist', 'Drummer', 'Artist', 'Songwriter',  # Artists
                        'Musical Instrument', 'Instrument', 'Keyboard instrument', 'string instrument', 'Percussion Instrument', 'Fretted Instrument',  # Instruments
                        'Genre', 'musical style',  # Categories
                        'Decade', 'year', 'era',  # Time
                        'city', 'country', 'continent', 'culture',  # Locations
                        'Musical Key', 'Musical Mode', 'BPM', 'Time Signature']  # Musical Terms

    classified_word_dict = {}
    for entity in keywords:
        classes = classifier(entity, candidate_labels)
        classified_word_dict[entity] = classes['labels'][0:3]#[0]

    return classified_word_dict


def main(text_prompt):
    return {"test": "asdf"}, {"test": "asdf"}, 1
    start_time = time.time()
    # Check if input is part of database
    # list = check_database_for_input(text_prompt)
    print(list)
    print("--- %s seconds ---" % round(time.time() - start_time, 2))
    # Timer Start
    start_time = time.time()
    filtered_text_prompt, song_info = check_for_key_and_bpm(text_prompt)
    print(time.time() - start_time)
    print(song_info)
    key_words = get_key_words(filtered_text_prompt)
    print(time.time() - start_time)
    classified_word_dict = word_categories(key_words)
    print(time.time() - start_time)
    print(classified_word_dict)
    end_time = time.time() - start_time
    # return classified_word_dict, song_info, int(end_time)
    # return {"test":"asdf"}, {"test":"asdf"}, 1


if __name__ == "__main__":
    main("Rihanna playing the Flute in b Minor with the beatles in the 80s")


