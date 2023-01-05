import pandas as pd


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


def main():
    text_prompt = "The Beatles"
    check_database_for_input(text_prompt)