from glob import glob

for file in glob("data/data_json/*.json"):
    with open(file, "r") as f:
        data = f.read()
        data = data.split("Se responde lo siguiente:\n")
        data = data.replace("{", "").replace("}", "")
        with open("data/data_raw/{}.json".format(file.replace(".json", ".txt")), "w") as f:
            f.write(data)
        print("File {} has been extracted.".format(file))