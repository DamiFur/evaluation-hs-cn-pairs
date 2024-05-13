from glob import glob
import random
import os
import json

models_list = os.listdir("data/data_raw")

comparisson_reference = models_list.copy()
def text_template(hs, cn):
    return "Lea atentamente el siguiente intercambio de tweets:\n\nDado el siguiente discurso de odio:\n\n" + hs.replace('\"', '\\\"') + "\n\nSe responde lo siguiente:\n\n" + cn.replace('\"', '\\\"')
random.Random(41).shuffle(models_list)
random.Random(42).shuffle(comparisson_reference)

for idx, folder in enumerate(models_list):
    comparison_folder = comparisson_reference[idx]
    for file in glob(f"data/data_raw/{folder}/*.txt"):
        filename = file.split("/")[-1]
        if len(filename.split("_")) > 4:
            filename = filename.replace("_1.txt", ".txt").replace("_2.txt", ".txt")
        if not os.path.exists(f"data/data_raw/{comparison_folder}/{filename}"):
            new_comparison_folder = comparison_folder
            print(folder)
            print(filename)
            print(new_comparison_folder)
            new_idx = idx
            while not os.path.exists(f"data/data_raw/{new_comparison_folder}/{filename}"):
                new_idx = (new_idx + 1) % len(comparisson_reference)
                new_comparison_folder = comparisson_reference[new_idx]
                print(new_comparison_folder)
            comparison_file = open(f"data/data_raw/{new_comparison_folder}/{filename}", 'r')
        else:
            comparison_file = open(f"data/data_raw/{comparison_folder}/{filename}", 'r')
        comparison_data = comparison_file.read()
        comparison_data = comparison_data.split("\n")
        comparison_data = [line for line in comparison_data if line != ""]
        with open(file, "r") as f:
            data = f.read()
            data = data.split("\n")
            data = [line for line in data if line != ""]
            json_data = {}
            hs_num = file.split("/")[-1].replace("hate_tweet_spanish_", "").replace(".txt", "")
            json_data["data"] = {"text": text_template(data[0], data[1]), "number": hs_num,"hs": data[0], "cn": data[1], "model": folder, "comparison_text": comparison_data[1], "comparison_model": comparison_folder, "comparison_text_complete": f"Evalue la siguiente respuesta alternativa al mismo mensaje de odio:\n\n{comparison_data[1]}"}
            if not os.path.exists(f"data/data_json_with_comparison/{folder}"):
                os.makedirs(f"data/data_json_with_comparison/{folder}")
            with open(f"data/data_json_with_comparison/{folder}/hate_tweet_spanish_{hs_num}.json", "w") as w:
                json.dump(json_data, w, indent=4, ensure_ascii=False)