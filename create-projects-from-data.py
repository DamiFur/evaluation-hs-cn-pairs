import os
from glob import glob
import requests
import json
import shutil

ENDPOINT = "http://localhost:8080/"
ACCESS_TOKEN = "65aa5ec1f1d822b1fecada16c311d59e21b5250a"
TEMPLATE = """<View>
  <Text name="text" value="$text"/>
  <View style="box-shadow: 2px 2px 5px #999;
               padding: 20px; margin-top: 2em;
               border-radius: 5px;">
    <Header value="La contranarrativa propuesta ¿se opone al discurso de odio contra inmigrantes?
"/>
    <Choices name="stance" toName="text"
             choice="single" showInLine="true">
      <Choice value="Está a favor del discurso de odio"/>
      <Choice value="No es claro / es ambiguo"/>
      <Choice value="Se opone al discurso de odio"/>
    </Choices>
  </View>
  <View style="box-shadow: 2px 2px 5px #999;
               padding: 20px; margin-top: 2em;
               border-radius: 5px;">
    <Header value="¿Es ofensiva contra el colectivo objetivo del mensaje de odio o contra cualquier otro colectivo o individuo?"/>
    <Choices name="ofensive" toName="text"
             choice="single" showInLine="true">
      <Choice value="Es ofensiva"/>
      <Choice value="No es clara / es ambigua"/>
      <Choice value="No es ofensiva"/>
    </Choices>
  </View>
    <View style="box-shadow: 2px 2px 5px #999;
               padding: 20px; margin-top: 2em;
               border-radius: 5px;">
    <Header value="La respuesta generada ¿aporta información *relevante* respecto al mensaje de odio que está respondiendo?"/>
    <Choices name="relevance" toName="text"
             choice="single" showInLine="true">
      <Choice value="Repite el mensaje original y/o cambia de tema respecto al mensaje original"/>
      <Choice value="Elabora contenido relevante pero también contenido que no es relevante o cambia de tema"/>
      <Choice value="Todo el contenido de la respuesta es relevante respecto al mensaje original"/>
    </Choices>
  </View>
      <View style="box-shadow: 2px 2px 5px #999;
               padding: 20px; margin-top: 2em;
               border-radius: 5px;">
    <Header value="La respuesta generada ¿elabora contenido *nuevo y específico* respecto al mensaje de odio?"/>
    <Choices name="specificity" toName="text"
             choice="single" showInLine="true">
      <Choice value="No elabora argumentos o información nueva, es una respuesta genérica"/>
      <Choice value="No elabora argumentos o información nueva pero es específica porque repite parte del mensaje tomando posición"/>
      <Choice value="Es una respuesta específica que elabora contenido nuevo a partir del contenido del mensaje de odio que responde"/>
    </Choices>
  </View>
  <View style="box-shadow: 2px 2px 5px #999;
               padding: 20px; margin-top: 2em;
               border-radius: 5px;">
    <Header value="La respuesta generada ¿aporta datos puntuales constatables creibles o verdaderos? Los datos puntuales constatables pueden ser citas, estadísticas, referencias, datos históricos o culturales o cualquier otra afirmación que pueda ser constatada con datos públicos"/>
    <Choices name="constatability" toName="text"
             choice="single" showInLine="true">
      <Choice value="No aporta datos constatables puntuales"/>
      <Choice value="Aporta datos puntuales contradictorios, sin sentido o evidentemente falsos"/>
      <Choice value="Aporta datos puntuales creibles que uno podría constatar con mayor o menor esfuerzo utilizando información pública"/>
    </Choices>
  </View>
  <View style="box-shadow: 2px 2px 5px #999;
             padding: 20px; margin-top: 2em;
             border-radius: 5px;">
  <Header value="La respuesta ¿se entiende fácilmente?"/>
  <Choices name="inteligibility" toName="text"
           choice="single" showInLine="true">
    <Choice value="No se entiende lo que quiere decir"/>
    <Choice value="Se entiende el sentido pero parece poco natural o poco humano"/>
    <Choice value="Se entiende el sentido, es fácil de entender y fluye bien"/>
  </Choices>
  </View>
  <View style="box-shadow: 2px 2px 5px #999;
             padding: 20px; margin-top: 2em;
             border-radius: 5px;">
  <Header value="Esta respuesta, ¿te parece que recurre a la emoción para tratar de convencer?"/>
  <Choices name="emotion" toName="text"
           choice="single" showInLine="true">
    <Choice value="Recurre a una o más emociones para tratar de convencer y las menciona explicitamente"/>
    <Choice value="Evoca a emociones implicitamente sin mencionarlas"/>
    <Choice value="No evoca a ninguna emoción"/>
  </Choices>
  </View>
  <View style="box-shadow: 2px 2px 5px #999;
             padding: 20px; margin-top: 2em;
             border-radius: 5px;">
  <Text name="comparison_text_complete" value="$comparison_text_complete"/>
  </View>
  <View style="box-shadow: 2px 2px 5px #999;
             padding: 20px; margin-top: 2em;
             border-radius: 5px;">
  <Header value="Esta nueva respuesta, ¿te parece mejor o peor que la anterior?"/>
  <Choices name="comparison" toName="text"
           choice="single" showInLine="true">
    <Choice value="Mejor"/>
    <Choice value="Está al mismo nivel"/>
    <Choice value="Peor"/>
  </Choices>
  </View>
  <View style="box-shadow: 2px 2px 5px #999;
             padding: 20px; margin-top: 2em;
             border-radius: 5px;">
  <Header value="Proponga una mejor respuesta en sus propias palabras:"/>
  <TextArea name="answer" toName="text"
            showSubmitButton="true" maxSubmissions="1" editable="true"
            required="true" />
  </View>
</View>

<!-- {
  "data": {"text": "Lea atentamente el siguiente intercambio de tweets:\n\nDado el siguiente discurso de odio:\n\nespaña está siendo invadida por los subsaharianos y aquí don tonto jugando al corro la patata desde la moncloa hashtag caminodevenezuela hashtag señorllevamépronto\n\nSe responde lo siguiente:\n\ny que en un país estén tomando a una postura antiinmigranción no significa que acogarlos sería un error"}
} -->
"""

filenames= []
for folders in glob('data/data_json_with_comparison/*'):
    for filename in glob(folders + '/*.json'):
        filenames.append(filename)

filenames = sorted(filenames, key=lambda x: x.split('/')[-1])

os.mkdir("projects")
current_project = 0
for i in range(len(filenames)//20):
    for j in range(4):
        new_block_1 = [filenames[i*20 + j*5 + l] for l in range(5)]
        for k in range(j+1, 4):
            print(i*20 + k*5)
            new_block_2 = [filenames[i*20 + k*5 + l] for l in range(5)]
            os.mkdir('projects/' + str(current_project))
            print(new_block_1 + new_block_2)
            for filename in (new_block_1 + new_block_2):
                os.system('cp ' + filename + ' projects/' + str(current_project) + "/" + filename.replace("/", "-"))
            response = requests.post(ENDPOINT + 'api/projects', headers={'Authorization': f'Token {ACCESS_TOKEN}', 'Content-Type': 'application/json'}, json={"label_config": TEMPLATE, "title": f"Block {current_project}"})
            decoded_response = json.loads(response.content.decode('utf-8'))
            project_id = decoded_response["id"]
            for filename in (new_block_1 + new_block_2):
                requests.post(ENDPOINT + f"api/projects/{project_id}/import", headers={'Authorization': f'Token {ACCESS_TOKEN}'}, files={"upload_file": open(filename, 'rb')})
            current_project += 1
shutil.rmtree("projects", ignore_errors=True)
