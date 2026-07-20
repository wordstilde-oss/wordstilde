import os
import json
import re

from wordfreq import iter_wordlist
from wordfreq import zipf_frequency



os.makedirs(
    "dictionary",
    exist_ok=True
)



palabras = set()



# =====================================
# CARGAR WORDLIST DE WORDFREQ
# =====================================


print("Cargando wordfreq...")


for palabra in iter_wordlist("es"):


    palabra = palabra.lower().strip()


    if re.fullmatch(
        r"[a-záéíóúüñ]+",
        palabra
    ):

        palabras.add(
            palabra
        )



print(
    "Palabras wordfreq:",
    len(palabras)
)




# =====================================
# CARGAR LIBREOFFICE
# =====================================


print(
    "Cargando LibreOffice..."
)


url = (
    "https://raw.githubusercontent.com/"
    "LibreOffice/dictionaries/master/es/es_ES.dic"
)


import requests


respuesta = requests.get(url)



for linea in respuesta.text.splitlines():


    palabra = linea.split("/")[0]


    palabra = palabra.lower().strip()



    if re.fullmatch(
        r"[a-záéíóúüñ]+",
        palabra
    ):


        palabras.add(
            palabra
        )




print(
    "Total combinado:",
    len(palabras)
)




# =====================================
# CREAR DICCIONARIO WORDLE
# =====================================


wordle = [

    p for p in palabras

    if len(p) in [3,4,5,6,7]

]




with open(
    "dictionary/palabras_wordle.txt",
    "w",
    encoding="utf-8"
) as archivo:


    for palabra in sorted(wordle):

        archivo.write(
            palabra+"\n"
        )






# =====================================
# FRECUENCIAS
# =====================================

frecuencias = {}

for palabra in wordle:

    # Frecuencia Zipf (0 a ~8)
    score = zipf_frequency(
        palabra,
        "es"
    )

    # Penalizaciones
    if len(set(palabra)) == 1:
        score -= 5

    if any(
        palabra.count(letra) >= len(palabra) - 1
        for letra in set(palabra)
    ):
        score -= 2

    if sum(
        letra in "aeiouáéíóú"
        for letra in palabra
    ) == 0:
        score -= 3

    frecuencias[palabra] = round(score, 2)


with open(
    "dictionary/frecuencias.json",
    "w",
    encoding="utf-8"
) as archivo:

    json.dump(
        frecuencias,
        archivo,
        ensure_ascii=False
    )





print("==============================")
print("DICCIONARIO TERMINADO")
print("==============================")

print(
    "Total palabras:",
    len(palabras)
)


print(
    "Palabras Wordle:",
    len(wordle)
)
