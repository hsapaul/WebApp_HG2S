from transformers import AutoTokenizer, AutoModelForTokenClassification, pipeline
from transformers import pipeline
import time
import pandas as pd

tonic = [' c ', ' c# ', ' cb', ' d ', ' d# ', ' db ', ' e ', ' eb', ' f ', ' f# ', ' fb', ' g ', ' g# ', ' gb', ' a ',
         ' a# ', ' ab', ' b ', ' bb']
mode = ['major', 'minor', 'dorian', 'phrygian', 'lydian', 'mixolydian', 'aeolian', 'locrian']
decades_year_era = ['1920s', '1930s', '1940s', '1950s', '1960s', '1970s', '1980s', '1990s', '2000s', '2010s', '2020s',
                    '20s', '30s', '40s', '50s', '60s', '70s', '80s', '90s',
                    "30's", "40's", "50's", "60's", "70's", "80's", "90's", "00's", "10's", "20's",
                    '18th century', '19th century', '20th century', '21st century',
                    'Anno Dominini', 'Before Christ', 'BC', 'AD', 'CE', 'BCE']


def check_for_artists(text_input):
    text_prompt = text_input
    # Check for artists
    found_artists = []
    for index in range(1, 5):
        list_path = fr"C:\Users\franz\Desktop\WebApp (Werkstück)\Music Gallery (Database)\1. Natural Language Processing\artists\10000-MTV-Music-Artists-page-{index}.csv"
        df = pd.read_csv(list_path)
        namen = df["name"].tolist()
        for name in namen:
            if str(name).strip().lower() in text_prompt.lower():
                found_artists.append(str(name).strip())
    found_artists = list(set([x.lower() for x in found_artists]))
    found_artists = [str(artist).capitalize() for artist in found_artists]
    return found_artists


def check_for_instruments(text_input):
    text_prompt = text_input
    # Check for instruments
    found_instruments = []
    list_path = fr"C:\Users\franz\Desktop\WebApp (Werkstück)\Music Gallery (Database)\1. Natural Language Processing\instruments\top100instruments.csv"
    # Read the csv file without pandas
    with open(list_path, 'r', encoding='utf-8') as f:
        for line in f:
            if line.strip().lower() in text_prompt.lower():
                found_instruments.append(line.strip())
                text_prompt = text_prompt.replace(line.strip().lower(), "")
    return text_prompt, found_instruments


def check_for_genres(text_input):
    text_prompt = text_input
    found_genres = []
    list_path = fr"C:\Users\franz\Desktop\WebApp (Werkstück)\Music Gallery (Database)\1. Natural Language Processing\genres\top75genres.csv"
    # Read the csv file without pandas
    with open(list_path, 'r', encoding='utf-8') as f:
        for line in f:
            if line.strip().lower() in text_prompt.lower():
                found_genres.append(line.strip())
                text_prompt = text_prompt.replace(line.strip().lower(), "")
    return text_prompt, found_genres


def check_for_time_information(text_prompt):
    # Check for time information
    found_time_information = []
    for decade in decades_year_era:
        if decade.lower() in text_prompt.lower():
            found_time_information.append(decade)
    return found_time_information


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
    keywords = [word['word'] for word in result if word["entity_group"] == "PROPN" or word["entity_group"] == "NOUN" or word["entity_group"] == "DET"]
    return " ".join(keywords)


# NLP - ZERO SHOT CLASSIFICATION
def word_categories(keywords):
    classifier = pipeline("zero-shot-classification",
                          model="facebook/bart-large-mnli")

    candidate_labels = ['Band', 'Singer', 'Vocalist', 'Rock Band', 'Composer', 'Pianist', 'Musician', 'DJ',
                        'Record Producer', 'Guitarist', 'Drummer', 'Artist', 'Songwriter',  # Artists
                        'Musical Instrument', 'Instrument', 'Keyboard instrument', 'string instrument',
                        'Percussion Instrument', 'Fretted Instrument',  # Instruments
                        'Genre', 'musical style',  # Categories
                        'Decade', 'year', 'era',  # Time
                        'city', 'country', 'continent', 'culture',  # Locations
                        'Musical Key', 'Musical Mode', 'BPM', 'Time Signature']  # Musical Terms

    classified_word_dict = {}
    for entity in keywords:
        classes = classifier(entity, candidate_labels)
        classified_word_dict[entity] = classes['labels'][0:3]  # [0]

    return classified_word_dict


def main(text_prompt):
    start_time = time.time()
    filtered_text, found_genres = check_for_genres(text_prompt)
    print(filtered_text)
    filtered_text, found_instruments = check_for_instruments(filtered_text)
    found_time = check_for_time_information(filtered_text)
    # filtered_text = get_key_words(filtered_text)
    found_artists = check_for_artists(filtered_text)
    print("Found Instruments: ", found_instruments)
    print("Found Artists: ", found_artists)
    print("Found Genres: ", found_genres)
    print("Found Time: ", found_time)
    filtered_text_prompt, key_and_bpm = check_for_key_and_bpm(text_prompt)
    print("Found Key and BPM: ", key_and_bpm)
    end_time = round(time.time() - start_time, 2)
    return found_artists, found_instruments, found_genres, found_time, key_and_bpm, end_time
    # print(list)
    # print("--- %s seconds ---" % round(time.time() - start_time, 2))
    # # Timer Start
    # start_time = time.time()
    # filtered_text_prompt, song_info = check_for_key_and_bpm(text_prompt)
    # print(time.time() - start_time)
    # print(song_info)
    # key_words = get_key_words(filtered_text_prompt)
    # print(time.time() - start_time)
    # classified_word_dict = word_categories(key_words)
    # print(time.time() - start_time)
    # print(classified_word_dict)
    # end_time = time.time() - start_time
    # return classified_word_dict, song_info, int(end_time)
    # return {"test":"asdf"}, {"test":"asdf"}, 1


if __name__ == "__main__":
    main("b major 140 bpm")
