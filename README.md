# RAG 

l'objectif c'est de faire une petite "application" pour avoir une IA en local capable de réexpliquer des thèmes (voir exemple)  tout en citant ses documents sources


# installation 

recomendé: python 3.12

```bash

python3.12 -m venv <nom de l'env>

# linux 
source ./venv/bin/activate

#windows

.\venv\Scripts\activate

# installation des requierements

pip3 install -r requierement.txt

```

# utilisation 

lancer [[GUI.py]] puis posez ça question
pour l'instant il pour upload des documents il faut lancer custom_ragV2_choix_similarity.py
avec la liste de fichier a upload (ne marche que sur des pdf pour l'instant)

![exemple](docs/exemple.png)


# todo 

- [X] ajoute rune interface pour posez des questions
- [] GUI pour upload les documents dans la bdd local du RAG
- [] ajouter un historique des questions prix en compte dans le RAG
- [] upload plus detype de documents (txt/.md , .odt, .docx, .xlsx, .pptx)