import shap
import transformers
import matplotlib.pyplot as plt

# 1. Charger le modèle et le tokenizer
model = transformers.AutoModelForCausalLM.from_pretrained("gpt2")
tokenizer = transformers.AutoTokenizer.from_pretrained("gpt2")

# 2. Créer l'explainer SHAP dédié au texte
explainer = shap.Explainer(model, tokenizer)

# 3. Calculer les valeurs SHAP pour un prompt
prompt = ["how many r in strawberry?"]
shap_values = explainer(prompt)

import matplotlib.pyplot as plt

import numpy as np

# On crée un nouvel objet SHAP qui est la moyenne des impacts sur tous les mots générés
mean_shap_values = shap_values[0]
mean_shap_values.values = np.mean(shap_values[0].values, axis=1)
# Encoder le prompt
inputs = tokenizer(prompt[0], return_tensors="pt")

# Générer la suite (ex: 10 mots de plus)
outputs = model.generate(**inputs, max_new_tokens=10)

# Décoder pour lire le texte
generated_text = tokenizer.decode(outputs[0], skip_special_tokens=True)
print(f"Prédiction complète : {generated_text}")
# On affiche le bar plot de l'importance moyenne
shap.plots.bar(mean_shap_values)
plt.show()