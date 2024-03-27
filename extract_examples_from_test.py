from glob import glob

import argparse
from transformers import StoppingCriteria, StoppingCriteriaList
from transformers import AutoModelForCausalLM
from transformers import AutoTokenizer
import torch
import argparse

parser = argparse.ArgumentParser(description="Train models for identifying argumentative components inside the ASFOCONG dataset")

parser.add_argument("--human", type=bool, default=False)
parser.add_argument("--model_name", type=str, choices=["google/flan-t5-base", "mistralai/Mixtral-8x7B-Instruct-v0.1", "mistralai/Mistral-7B-Instruct-v0.1", "tiiuae/falcon-7b-instruct"])
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
    model = AutoModelForCausalLM.from_pretrained(model_name)
    tokenizer = AutoTokenizer.from_pretrained(model_name)

    if model_name == "tiiuae/falcon-7b-instruct":
        stop_words = [".", "]", "']", "']\n", "\n", "]\n", "\n\n", "']\n\n", "<|endoftext|>"]
    else:
        stop_words = [".", "]", "']", "']\n", "\n", "]\n", "\n\n", "']\n\n", "</s>"]
    stop_words_ids = [tokenizer(stop_word, return_tensors='pt', add_special_tokens=False)['input_ids'].squeeze() for stop_word in stop_words]
    stopping_criteria = StoppingCriteriaList([StoppingCriteriaSub(stops=stop_words_ids)])

    if model_name == "tiiuae/falcon-7b-instruct":
        prompt_noinfo = f"Genera una respuesta contraria al racismo y la xenofobia de los siguientes mensajes de odio:\n'¿esto podría explicar el brutismo caribeño y el subsahariano? ¿habrá correlación? extreme heat linked with reduced cognitive performance among young adults in non-air-conditioned buildings' -> Respuesta: 'Es difícil que algo tenga relación con algún estudio de internet completamente descontextualizado...'\n 'llegan 900 venezolanos por día al perú cuantos más tendrán que venir para que ya se ponga coto y fin a esta invasión ? qué ya no es una inmigración a las autoridades peruanas no les da ni la tos por este tema solo reaccionarán cuando esto se desborde' -> Respuesta: 'Estás siendo paranoico. No se va a desbordar, y es por eso que no hace falta ponerle coto y fin'\n '{args.hs}' -> Respuesta: "
        prompt_collective = f"Genera una respuesta contraria al racismo y la xenofobia de de odio:\n'¿esto podría explicar el brutismo caribeño y el subsahariano? ¿habrá correlación? extreme heat linked with reduced cognitive performance among young adults in non-air-conditioned buildings' | Collectivo contra quien se dirige el odio: 'caribeño y subsahariano' | Propiedad asociada al colectivo: 'brutismo' -> Respuesta: 'No es cierto que los caribeños o subsaharianos sean brutos. Es solo un prejuicio.'\n 'llegan 900 venezolanos por día al perú cuantos más tendrán que venir para que ya se ponga coto y fin a esta invasión ? qué ya no es una inmigración a las autoridades peruanas no les da ni la tos por este tema solo reaccionarán cuando esto se desborde' | Collectivo contra quien se dirige el odio: 'venezolanos' | Propiedad asociada al colectivo: 'invasion' -> Respuesta: 'Lo llamas invasión pero solo te refieres a los venezolanos, y no a los demás inmigrantes. ¿No estás siendo un poco racista?'\n '{args.hs}' | Collectivo contra quien se dirige el odio: '{args.collective}' | Propiedad asociada al colectivo: '{args.property}' -> Respuesta: "
        prompt_premises = f"Genera una respuesta contraria al racismo y la xenofobia de de odio:\n'¿esto podría explicar el brutismo caribeño y el subsahariano? ¿habrá correlación? extreme heat linked with reduced cognitive performance among young adults in non-air-conditioned buildings' | Justificación del argumento: extreme heat linked with reduced cognitive performance among young adults in non-air-conditioned buildings  | Conclusión: ¿esto podría explicar el brutismo caribeño y el subsahariano ? ¿habrá correlación?' -> Respuesta: 'Es difícil que algo tenga relación con algún estudio de internet completamente descontextualizado...'\n 'llegan 900 venezolanos por día al perú cuantos más tendrán que venir para que ya se ponga coto y fin a esta invasión ? qué ya no es una inmigración a las autoridades peruanas no les da ni la tos por este tema solo reaccionarán cuando esto se desborde' | Justificación del argumento: 'llegan 900 venezolanos por día al perú' y 'qué ya no es una inmigración a las autoridades peruanas no les da ni la tos por este tema' | Conclusión: 'cuantos más tendrán que venir para que ya se ponga coto y fin a esta invasión ?' y 'solo reaccionarán cuando esto se desborde'  -> Respuesta: 'Estás siendo paranoico. No se va a desbordar, y es por eso que no hace falta ponerle coto y fin'\n '{args.hs}' | Justificación del argumento: '{args.justification}' | Conclusión: '{args.conclusion}'  -> Respuesta: "
    else:
        prompt_noinfo = [
            {"role": "user", "content": "Genera una respuesta contraria al racismo y la xenofobia de de odio:\n'¿esto podría explicar el brutismo caribeño y el subsahariano? ¿habrá correlación? extreme heat linked with reduced cognitive performance among young adults in non-air-conditioned buildings"},
            {"role": "assistant", "content": "Es difícil que algo tenga relación con algún estudio de internet completamente descontextualizado..."},
            {"role": "user", "content": "llegan 900 venezolanos por día al perú cuantos más tendrán que venir para que ya se ponga coto y fin a esta invasión ? qué ya no es una inmigración a las autoridades peruanas no les da ni la tos por este tema solo reaccionarán cuando esto se desborde"},
            {"role": "assistant", "content": "Estás siendo paranoico. No se va a desbordar, y es por eso que no hace falta ponerle coto y fin"},
            {"role": "user", "content": f"{args.hs}"}
        ]
        prompt_collective = [
            {"role": "user", "content": "Genera una respuesta contraria al racismo y la xenofobia de de odio:\n'¿esto podría explicar el brutismo caribeño y el subsahariano? ¿habrá correlación? extreme heat linked with reduced cognitive performance among young adults in non-air-conditioned buildings' | Collectivo contra quien se dirige el odio: 'caribeño y subsahariano' | Propiedad asociada al colectivo: 'brutismo'"},
            {"role": "assistant", "content": "No es cierto que los caribeños o subsaharianos sean brutos. Es solo un prejuicio."},
            {"role": "user", "content": "llegan 900 venezolanos por día al perú cuantos más tendrán que venir para que ya se ponga coto y fin a esta invasión ? qué ya no es una inmigración a las autoridades peruanas no les da ni la tos por este tema solo reaccionarán cuando esto se desborde' | Collectivo contra quien se dirige el odio: 'venezolanos' | Propiedad asociada al colectivo: 'invasion'"},
            {"role": "assistant", "content": "Lo llamas invasión pero solo te refieres a los venezolanos, y no a los demás inmigrantes. ¿No estás siendo un poco racista?"},
            {"role": "user", "content": f"{args.hs} | Collectivo contra quien se dirige el odio: '{args.collective}' | Propiedad asociada al colectivo: '{args.property}'"}
        ]
        prompt_premises = [
            {"role": "user", "content": "Genera una respuesta contraria al racismo y la xenofobia de de odio:\n'¿esto podría explicar el brutismo caribeño y el subsahariano? ¿habrá correlación? extreme heat linked with reduced cognitive performance among young adults in non-air-conditioned buildings' | Justificación del argumento: extreme heat linked with reduced cognitive performance among young adults in non-air-conditioned buildings  | Conclusión: ¿esto podría explicar el brutismo caribeño y el subsahariano ? ¿habrá correlación?"},
            {"role": "assistant", "content": "Es difícil que algo tenga relación con algún estudio de internet completamente descontextualizado..."},
            {"role": "user", "content": "llegan 900 venezolanos por día al perú cuantos más tendrán que venir para que ya se ponga coto y fin a esta invasión ? qué ya no es una inmigración a las autoridades peruanas no les da ni la tos por este tema solo reaccionarán cuando esto se desborde' | Justificación del argumento: 'llegan 900 venezolanos por día al perú' y 'qué ya no es una inmigración a las autoridades peruanas no les da ni la tos por este tema' | Conclusión: 'cuantos más tendrán que venir para que ya se ponga coto y fin a esta invasión ?' y 'solo reaccionarán cuando esto se desborde'"},
            {"role": "assistant", "content": "Estás siendo paranoico. No se va a desbordar, y es por eso que no hace falta ponerle coto y fin"},
            {"role": "user", "content": f"{args.hs} | Justificación del argumento: {args.justification} | Conclusión: {args.conclusion}"}
        ]

def generate_answers(prompt, num_samples=10):
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
        num_beams=4,
        no_repeat_ngram_size=2,
        num_return_sequences=1, # only show top beams
        # early_stopping=True,
        stopping_criteria=stopping_criteria,
        eos_token_id=tokenizer.eos_token_id,
        pad_token_id=tokenizer.eos_token_id,
    )
    gen_outputs.append(gen_output)

  return gen_outputs

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
        print(file)
        if noarg:
            continue
        else:
            if args.human:
                cns = []
                with open(file.replace("conll", "cn")) as cns:
                    cns = cns.readlines()
                for idx, cn in enumerate(cns):
                    with open("data/human_annotated/{}_{}.json".format(file.split('/')[-1].split('.')[0], idx), 'w') as f:
                        f.write("{\"data\": {\"text\": \"Lea atentamente el siguiente intercambio de tweets:\n\nDado el siguiente discurso de odio:\n\n" + " ".join(tweet).replace('\"', '\\\"') + "\n\nSe responde lo siguiente:\n\n" + cn.replace('\"', '\\\"') + "\"}}")
            else:
                if args.model_name == "":
                    raise ValueError("Model name must be provided")
                answer = generate_answers(prompt_noinfo)
                print(tokenizer.batch_decode(answer[0], skip_special_tokens=True))
                    
