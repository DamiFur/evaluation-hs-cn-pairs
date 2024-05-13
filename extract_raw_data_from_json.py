from glob import glob
import os

for folder in glob("data/data_json/*"):
    root = folder.split("/")[-1]
    os.mkdir(f"data/data_raw/{root}")
    for file in glob(folder + "/*.json"):
        file_root = file.split("/")[-1].replace(".json", ".txt").replace("_0.", ".")
        with open(file, "r") as f:
            data = f.read()
            hs = data.split("Dado el siguiente discurso de odio:\n")[-1]
            separation = hs.split("Se responde lo siguiente:\n")
            hs = separation[0].replace("\n", "")
            data = separation[-1].replace('"}}', '').replace("\n", "").replace("<SCN> ", "").replace("<ECN>", "").replace("<SCN>", "").replace("pa<unk>s", "país").replace("a<unk>o", "año").replace("estre<unk>idos", "estreñidos").replace("pa<unk>a", "paña").replace("ni<unk>a", "niña").replace("aqu<unk>", "aquí").replace("seg<unk>n", "según").replace("per<unk>", "perú").replace("<unk>nica", "única").replace("<unk>", "")
            with open(f"data/data_raw/{root}/{file_root}", "w") as f:
                f.write(hs)
                f.write("\n")
                f.write(data)
            print("File {} has been extracted.".format(file))