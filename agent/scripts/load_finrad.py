from datasets import load_dataset
import os

# Créer le dossier s'il n'existe pas
os.makedirs("data/education", exist_ok=True)

print(" Téléchargement de FinRAD...")
ds = load_dataset("sohomghosh/FinRAD_Financial_Readability_Assessment_Dataset")

# Regardons les noms des colonnes pour être sûr
column_names = ds["train"].column_names
print(f"Colonnes trouvées : {column_names}")

# On cherche la colonne qui contient le contenu (souvent 'Sentence' ou 'Description')
# Dans FinRAD, c'est généralement 'Sentence'
target_column = "Sentence" if "Sentence" in column_names else column_names[0]
print(f" Extraction depuis la colonne : {target_column}")

# Extraction des textes avec filtrage

target_column = "definitions" 

# On récupère tout ce qui n'est pas vide
texts = [item[target_column] for item in ds["train"] if item[target_column] is not None]

# Terme + Définition pour que le RAG soit super précis
combined_texts = []
for item in ds["train"]:
    term = item["terms"]
    definition = item["definitions"]
    if term and definition:
        combined_texts.append(f"Concept: {term}\nDéfinition: {definition}")

# Sauvegarde
with open("data/education/finrad_library.txt", "w", encoding="utf-8") as f:
    for t in combined_texts:
        f.write(t + "\n\n")

print(f" Terminé ! {len(combined_texts)} fiches pédagogiques sauvegardées.")