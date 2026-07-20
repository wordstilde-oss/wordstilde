import os
import json
import unicodedata
from collections import Counter


# ============================================
# UTILIDADES
# ============================================

def word_length(word):
    """
    La longitud considera las tildes
    como una sola letra.
    """

    return len(word)


def has_accent(word):
    """
    Detecta si contiene una vocal con tilde.
    """

    accents = "áéíóúÁÉÍÓÚ"

    return any(
        c in accents
        for c in word
    )


def remove_accents(text):
    """
    Elimina únicamente las tildes de las vocales.
    La ñ se conserva.
    """

    replacements = {
        "á": "a",
        "é": "e",
        "í": "i",
        "ó": "o",
        "ú": "u",
        "Á": "A",
        "É": "E",
        "Í": "I",
        "Ó": "O",
        "Ú": "U",
    }

    return "".join(
        replacements.get(c, c)
        for c in text
    )

# ============================================
# CARGAR DICCIONARIOS
# ============================================

def load_dictionary(path):

    with open(
        path,
        "r",
        encoding="utf-8"
    ) as file:

        return [
            line.strip().lower()
            for line in file
            if line.strip()
        ]


def load_frequencies(path):

    if not os.path.exists(path):
        return {}

    with open(
        path,
        "r",
        encoding="utf-8"
    ) as file:

        return json.load(file)
    
# ============================================
# ALGORITMO WORDLE
# ============================================

def evaluate_attempt(
    candidate,
    attempt,
    accent_filter="all"
):
    """
    Comprueba si una palabra candidata
    es compatible con un intento.

    Si accent_filter == "all",
    las tildes se ignoran.

    Si accent_filter == "accent",
    las tildes cuentan como letras distintas.
    """

    guess = attempt["word"].lower()
    colors = attempt["colors"]

    # ====================================
    # NORMALIZAR (ignorar tildes)
    # ====================================

    if accent_filter == "all":

        candidate_cmp = remove_accents(candidate)
        guess_cmp = remove_accents(guess)

    else:

        candidate_cmp = candidate
        guess_cmp = guess

    candidate_letters = Counter(candidate_cmp)

    required_letters = Counter()
    forbidden_letters = Counter()

    # ====================================
    # VERDES
    # ====================================

    for i, color in enumerate(colors):

        if color == "green":

            if candidate_cmp[i] != guess_cmp[i]:
                return False

            required_letters[guess_cmp[i]] += 1

            candidate_letters[guess_cmp[i]] -= 1

    # ====================================
    # AMARILLOS
    # ====================================

    for i, color in enumerate(colors):

        if color == "yellow":

            letra = guess_cmp[i]

            if candidate_cmp[i] == letra:
                return False

            if candidate_letters[letra] <= 0:
                return False

            required_letters[letra] += 1
            candidate_letters[letra] -= 1

    # ====================================
    # GRISES
    # ====================================

    for i, color in enumerate(colors):

        if color == "gray":

            letra = guess_cmp[i]

            if candidate_letters[letra] > 0:

                return False

    return True


# ============================================
# FILTRO PRINCIPAL
# ============================================

def filter_words(
    words,
    attempts,
    length,
    accent_filter="all"
):

    result = []

    for word in words:

        # Longitud

        if len(word) != length:
            continue

        # Solo cuando el usuario elige
        # "Con tilde"

        if accent_filter == "accent":

            if not has_accent(word):
                continue

        valid = True

        for attempt in attempts:

            if not evaluate_attempt(
                word,
                attempt,
                accent_filter
            ):

                valid = False
                break

        if valid:

            result.append(word)

    # ====================================
    # ELIMINAR DUPLICADOS POR TILDES
    # ====================================

    if accent_filter == "all":

        unicas = {}

        for word in result:

            palabra_sin_tilde = remove_accents(word)

            if palabra_sin_tilde not in unicas:

                unicas[palabra_sin_tilde] = palabra_sin_tilde

        result = list(unicas.values())

    return result


# ============================================
# RANKING
# ============================================

def score_word(
    word,
    frequencies=None
):

    """
    Puntúa candidatos.

    Primero usa frecuencia real
    si existe.

    Si no existe:
    usa frecuencia de letras.
    """

    word = remove_accents(word)

    if frequencies:

        if word in frequencies:

            return frequencies[word]



    letter_score = {

        "a":12,
        "e":13,
        "o":9,
        "s":8,
        "n":7,
        "r":7,
        "i":6,
        "d":5,
        "l":5,
        "c":4,
        "t":4

    }


    score = 0


    for letter in word:

        score += (
            letter_score
            .get(letter,1)
        )


    # Premiar letras distintas

    score += len(
        set(word)
    )


    return score




def rank_candidates(
    words,
    frequencies=None
):


    ranked = []


    for word in words:

        ranked.append(
            {
                "word":word,

                "score":
                score_word(
                    word,
                    frequencies
                ),

                "accent":
                has_accent(word)
            }
        )



    ranked.sort(
        key=lambda x:x["score"],
        reverse=True
    )


    return ranked