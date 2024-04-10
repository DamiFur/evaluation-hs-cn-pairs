# Create LabelStudio projects and populate them with LLM's generated counter-narratives

This repo contains the code needed to populate a Labelstudio labelling web interface with counter-narratives to specific hate tweets contained on the "data" folder. There is also a script for generating new data using a LLM from Huggingface that automatically stores the output of the model in the same format needed to be uplodaded to labelstudio.

Labelstudio must be already running in localhost (see labelstudio.io)

To create projects populated with data and ready to be labeled by annotators you must first retrieve your access token from a labelstudio user with access to the organization you want to use.
Assign that access token to the variable ACCESS_TOKEN on the top of each script. Then run

```
python create-projects-from-data.py
```

To delete all the projects and annotations you can run

```
python delete-all-projects.py
```
BEWARE! This will delete all your data in the project so make sure you make a copy first

To automatically export all anotations to an output folder run
```
python export-data.py
```
