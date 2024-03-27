from glob import glob

import argparse
from transformers import StoppingCriteria, StoppingCriteriaList
from transformers import AutoModelForCausalLM
from transformers import AutoTokenizer, QuantoConfig
import torch
import argparse
import os

parser = argparse.ArgumentParser(description="Train models for identifying argumentative components inside the ASFOCONG dataset")

parser.add_argument("--human", type=bool, default=False)
parser.add_argument("--model_name", type=str, choices=["google/flan-t5-base", "mistralai/Mixtral-8x7B-Instruct-v0.1", "mistralai/Mistral-7B-Instruct-v0.1", "mistralai/Mistral-7B-Instruct-v0.2", "tiiuae/falcon-7b-instruct"])
parser.add_argument("--collective", type=bool, default=False)
parser.add_argument("--justification", type=bool, default=False)
args = parser.parse_args()

class StoppingCriteriaSub(StoppingCriteria):
    def __init__(self, stops = [], encounters=1):
        super().__init__()
        self.stops = [stop.to("cuda") for stop in stops]

    def __call__(self, input_ids: torch.LongTensor, scores: torch.FloatTensor):
        last_token = input_ids[0][-1]
        for stop in self.stops:
            if tokenizer.decode(stop) == tokenizer.decode(last_token):
                return True
        return False

if not args.human:
    model_name = args.model_name
    quantization_config = QuantoConfig(weights="int4")
    model = AutoModelForCausalLM.from_pretrained(model_name, device_map="cuda:0", quantization_config=quantization_config)
    tokenizer = AutoTokenizer.from_pretrained(model_name)

    if model_name == "tiiuae/falcon-7b-instruct":
        stop_words = [".", "]", "']", "']\n", "\n", "]\n", "\n\n", "']\n\n", "<|endoftext|>"]
    else:
        stop_words = [".", "]", "']", "']\n", "\n", "]\n", "\n\n", "']\n\n", "</s>"]
    stop_words_ids = [tokenizer(stop_word, return_tensors='pt', add_special_tokens=False)['input_ids'].squeeze() for stop_word in stop_words]
    stopping_criteria = StoppingCriteriaList([StoppingCriteriaSub(stops=stop_words_ids)])

def get_prompt(hs, collective="", property="", justification="", conclusion=""):
    if justification != "":
        if model_name == "tiiuae/falcon-7b-instruct":
            return f"Genera una respuesta contraria al racismo y la xenofobia de de odio:\n'¿esto podría explicar el brutismo caribeño y el subsahariano? ¿habrá correlación? extreme heat linked with reduced cognitive performance among young adults in non-air-conditioned buildings' | Justificación del argumento: extreme heat linked with reduced cognitive performance among young adults in non-air-conditioned buildings  | Conclusión: ¿esto podría explicar el brutismo caribeño y el subsahariano ? ¿habrá correlación?' -> Respuesta: 'Es difícil que algo tenga relación con algún estudio de internet completamente descontextualizado...'\n 'llegan 900 venezolanos por día al perú cuantos más tendrán que venir para que ya se ponga coto y fin a esta invasión ? qué ya no es una inmigración a las autoridades peruanas no les da ni la tos por este tema solo reaccionarán cuando esto se desborde' | Justificación del argumento: 'llegan 900 venezolanos por día al perú' y 'qué ya no es una inmigración a las autoridades peruanas no les da ni la tos por este tema' | Conclusión: 'cuantos más tendrán que venir para que ya se ponga coto y fin a esta invasión ?' y 'solo reaccionarán cuando esto se desborde'  -> Respuesta: 'Estás siendo paranoico. No se va a desbordar, y es por eso que no hace falta ponerle coto y fin'\n '{args.hs}' | Justificación del argumento: '{args.justification}' | Conclusión: '{args.conclusion}'  -> Respuesta: "
        return [
            {"role": "user", "content": "Genera una respuesta contraria al racismo y la xenofobia de de odio:\n'¿esto podría explicar el brutismo caribeño y el subsahariano? ¿habrá correlación? extreme heat linked with reduced cognitive performance among young adults in non-air-conditioned buildings' | Justificación del argumento: extreme heat linked with reduced cognitive performance among young adults in non-air-conditioned buildings  | Conclusión: ¿esto podría explicar el brutismo caribeño y el subsahariano ? ¿habrá correlación?"},
            {"role": "assistant", "content": "Es difícil que algo tenga relación con algún estudio de internet completamente descontextualizado..."},
            {"role": "user", "content": "llegan 900 venezolanos por día al perú cuantos más tendrán que venir para que ya se ponga coto y fin a esta invasión ? qué ya no es una inmigración a las autoridades peruanas no les da ni la tos por este tema solo reaccionarán cuando esto se desborde' | Justificación del argumento: 'llegan 900 venezolanos por día al perú' y 'qué ya no es una inmigración a las autoridades peruanas no les da ni la tos por este tema' | Conclusión: 'cuantos más tendrán que venir para que ya se ponga coto y fin a esta invasión ?' y 'solo reaccionarán cuando esto se desborde'"},
            {"role": "assistant", "content": "Estás siendo paranoico. No se va a desbordar, y es por eso que no hace falta ponerle coto y fin"},
            {"role": "user", "content": f"{hs} | Justificación del argumento: {justification} | Conclusión: {conclusion}"}
        ]
    elif collective != "":
        if model_name == "tiiuae/falcon-7b-instruct":
            return f"Genera una respuesta contraria al racismo y la xenofobia de de odio:\n'¿esto podría explicar el brutismo caribeño y el subsahariano? ¿habrá correlación? extreme heat linked with reduced cognitive performance among young adults in non-air-conditioned buildings' | Collectivo contra quien se dirige el odio: 'caribeño y subsahariano' | Propiedad asociada al colectivo: 'brutismo' -> Respuesta: 'No es cierto que los caribeños o subsaharianos sean brutos. Es solo un prejuicio.'\n 'llegan 900 venezolanos por día al perú cuantos más tendrán que venir para que ya se ponga coto y fin a esta invasión ? qué ya no es una inmigración a las autoridades peruanas no les da ni la tos por este tema solo reaccionarán cuando esto se desborde' | Collectivo contra quien se dirige el odio: 'venezolanos' | Propiedad asociada al colectivo: 'invasion' -> Respuesta: 'Lo llamas invasión pero solo te refieres a los venezolanos, y no a los demás inmigrantes. ¿No estás siendo un poco racista?'\n '{hs}' | Collectivo contra quien se dirige el odio: '{collective}' | Propiedad asociada al colectivo: '{property}' -> Respuesta: "
        return [
            {"role": "user", "content": "Genera una respuesta contraria al racismo y la xenofobia de de odio:\n'¿esto podría explicar el brutismo caribeño y el subsahariano? ¿habrá correlación? extreme heat linked with reduced cognitive performance among young adults in non-air-conditioned buildings' | Collectivo contra quien se dirige el odio: 'caribeño y subsahariano' | Propiedad asociada al colectivo: 'brutismo'"},
            {"role": "assistant", "content": "No es cierto que los caribeños o subsaharianos sean brutos. Es solo un prejuicio."},
            {"role": "user", "content": "llegan 900 venezolanos por día al perú cuantos más tendrán que venir para que ya se ponga coto y fin a esta invasión ? qué ya no es una inmigración a las autoridades peruanas no les da ni la tos por este tema solo reaccionarán cuando esto se desborde' | Collectivo contra quien se dirige el odio: 'venezolanos' | Propiedad asociada al colectivo: 'invasion'"},
            {"role": "assistant", "content": "Lo llamas invasión pero solo te refieres a los venezolanos, y no a los demás inmigrantes. ¿No estás siendo un poco racista?"},
            {"role": "user", "content": f"{hs} | Collectivo contra quien se dirige el odio: '{collective}' | Propiedad asociada al colectivo: '{property}'"}
        ]
    else:
        if model_name == "tiiuae/falcon-7b-instruct":
            return f"Genera una respuesta contraria al racismo y la xenofobia de los siguientes mensajes de odio:\n'¿esto podría explicar el brutismo caribeño y el subsahariano? ¿habrá correlación? extreme heat linked with reduced cognitive performance among young adults in non-air-conditioned buildings' -> Respuesta: 'Es difícil que algo tenga relación con algún estudio de internet completamente descontextualizado...'\n 'llegan 900 venezolanos por día al perú cuantos más tendrán que venir para que ya se ponga coto y fin a esta invasión ? qué ya no es una inmigración a las autoridades peruanas no les da ni la tos por este tema solo reaccionarán cuando esto se desborde' -> Respuesta: 'Estás siendo paranoico. No se va a desbordar, y es por eso que no hace falta ponerle coto y fin'\n '{hs}' -> Respuesta: "
        return [
            {"role": "user", "content": "Genera una respuesta contraria al racismo y la xenofobia de de odio:\n'¿esto podría explicar el brutismo caribeño y el subsahariano? ¿habrá correlación? extreme heat linked with reduced cognitive performance among young adults in non-air-conditioned buildings"},
            {"role": "assistant", "content": "Es difícil que algo tenga relación con algún estudio de internet completamente descontextualizado..."},
            {"role": "user", "content": "llegan 900 venezolanos por día al perú cuantos más tendrán que venir para que ya se ponga coto y fin a esta invasión ? qué ya no es una inmigración a las autoridades peruanas no les da ni la tos por este tema solo reaccionarán cuando esto se desborde"},
            {"role": "assistant", "content": "Estás siendo paranoico. No se va a desbordar, y es por eso que no hace falta ponerle coto y fin"},
            {"role": "user", "content": f"{hs}"}
        ]

def generate_answers(prompt, num_samples=1):
  # define some source text and tokenize it
  source_text = prompt
  if model_name == "tiiuae/falcon-7b-instruct":
    source_ids = tokenizer(source_text, return_tensors="pt").input_ids.to("cuda")
  else:
      source_ids = tokenizer.apply_chat_template(prompt, return_tensors="pt").to("cuda")

  gen_outputs = []
  for _ in range(num_samples):
    # generate the output using beam search
    gen_output = model.generate(
        inputs=source_ids,
        # temperature=temperature,
        do_sample=True,
        max_new_tokens=40,
        num_beams=2,
        no_repeat_ngram_size=2,
        num_return_sequences=1, # only show top beams
        # early_stopping=True,
        stopping_criteria=stopping_criteria,
        eos_token_id=tokenizer.eos_token_id,
        pad_token_id=tokenizer.eos_token_id,
    )
    gen_outputs.append(gen_output)

  return gen_outputs

def write_to_file(base_dir, hs, cn, file, idx):
    with open("{}/{}_{}.json".format(base_dir, file.split('/')[-1].split('.')[0], idx), 'w') as w:
        w.write("{\"data\": {\"text\": \"Lea atentamente el siguiente intercambio de tweets:\n\nDado el siguiente discurso de odio:\n\n" + hs.replace('\"', '\\\"') + "\n\nSe responde lo siguiente:\n\n" + cn.replace('\"', '\\\"') + "\"}}")


if not os.path.isdir(f"data/{args.model_name.split('/')[-1]}"):
    os.mkdir(f"data/{args.model_name.split('/')[-1]}")

for file in glob('test_set/*.conll'):
    with open(file, 'r') as f:
        lines = f.readlines()
        noarg = False
        tweet = []
        for line in lines:
            line_split = line.split('\t')
            if len(line_split) < 2 or line_split[1] == 'NoArgumentative':
                noarg = True
                break
            tweet.append(line_split[0])
        if noarg:
            continue
        else:
            if args.human:
                cns = []
                with open(file.replace("conll", "cn")) as cns:
                    cns = cns.readlines()
                for idx, cn in enumerate(cns):
                    write_to_file("data/human_annotated", " ".join(tweet), cn, file, idx)
            else:
                if args.model_name == "":
                    raise ValueError("Model name must be provided")
                prompt = get_prompt(" ".join(tweet))
                answer = generate_answers(prompt)
                decoded_answer = tokenizer.batch_decode(answer[0], skip_special_tokens=True)[0]
                if model_name != "tiiuae/falcon-7b-instruct":
                    decoded_answer = decoded_answer.split("[/INST]")[-1]
                write_to_file(f"data/{args.model_name.split('/')[-1]}", " ".join(tweet), decoded_answer, file, 0)
                
                    

