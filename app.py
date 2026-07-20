from flask import (
    Flask,
    render_template,
    request,
    jsonify
)

from wordlee_solver import (
    load_dictionary,
    load_frequencies,
    filter_words,
    rank_candidates
)


import os



# ============================================
# CONFIGURACIÓN
# ============================================

app = Flask(__name__)



# ============================================
# CARGAR DICCIONARIOS
# ============================================


WORDLE_DICTIONARY_PATH = (
    "dictionary/palabras_wordle.txt"
)


FREQUENCY_PATH = (
    "dictionary/frecuencias.json"
)



# Diccionarios cargados en memoria



WORDLE_WORDS = []


FREQUENCIES = {}



def initialize():

    global WORDLE_WORDS
    global FREQUENCIES




    if os.path.exists(
        WORDLE_DICTIONARY_PATH
    ):

        WORDLE_WORDS = load_dictionary(
            WORDLE_DICTIONARY_PATH
        )



    FREQUENCIES = load_frequencies(
        FREQUENCY_PATH
    )



initialize()




# ============================================
# PÁGINA PRINCIPAL
# ============================================

@app.route("/")
def index():

    return render_template(
        "index.html"
    )

from flask import send_from_directory

@app.route("/robots.txt")
def robots():
    return send_from_directory(".", "robots.txt")


@app.route("/sitemap.xml")
def sitemap():
    return send_from_directory(".", "sitemap.xml")


# ============================================
# API SOLVER
# ============================================

@app.route(
    "/solve",
    methods=["POST"]
)

def solve():



    data = request.json



    length = int(
        data.get(
            "length",
            7
        )
    )



    attempts = data.get(
        "attempts",
        []
    )



    accent_filter = data.get(
        "accent",
        "all"
    )




    # ====================================
    # SELECCIONAR DICCIONARIO
    # ====================================


    words = WORDLE_WORDS




    # ====================================
    # FILTRAR
    # ====================================


    candidates = filter_words(
        words,
        attempts,
        length,
        accent_filter
    )



    # ====================================
    # ORDENAR
    # ====================================


    ranked = rank_candidates(
        candidates,
        FREQUENCIES
    )



    # ====================================
    # ESTADÍSTICAS
    # ====================================


    initial_amount = len(
        [
            w
            for w in words
            if len(w)==length
        ]
    )



    reduction = 0



    if initial_amount:

        reduction = round(
            (
                1 -
                len(ranked)
                /
                initial_amount
            )
            *
            100,
            2
        )




    return jsonify({

        "count":
            len(ranked),


        "reduction":
            reduction,


        "words":
            ranked[:500]

    })





# ============================================
# EJECUTAR
# ============================================

if __name__ == "__main__":

    app.run(
        debug=True
    )