# ============================================================
# PROJETO VOZES DE ÁGUA NEGRA
# Arquivo: app.py
#
# Este programa:
# 1. abre as páginas do site;
# 2. consulta os temas no banco;
# 3. apresenta e corrige o quiz;
# 4. registra a reflexão do visitante;
# 5. mostra os votos no painel.
# ============================================================


# sqlite3 permite acessar o banco SQLite.
import sqlite3

# Path ajuda a encontrar o banco na mesma pasta deste arquivo.
from pathlib import Path

# Recursos utilizados para criar o site com Flask.
from flask import Flask
from flask import render_template
from flask import request
from flask import redirect
from flask import url_for


# Cria a aplicação.
app = Flask(__name__)


# Descobre a pasta onde app.py está salvo.
PASTA_PROJETO = Path(__file__).resolve().parent

# Monta o caminho completo do banco.
# Assim, o programa encontrará torto_arado.db
# mesmo se o terminal estiver em outra pasta.
CAMINHO_BANCO = PASTA_PROJETO / "torto_arado.db"


def conectar():
    """
    Abre uma conexão com o banco de dados.

    sqlite3.Row permite acessar os dados pelo nome da coluna.

    Exemplo:
        tema["nome"]
    """

    # Se o banco não existir, avisa claramente.
    # Sem esta verificação, o SQLite poderia criar
    # um banco vazio por engano.
    if not CAMINHO_BANCO.exists():
        raise FileNotFoundError(
            "O arquivo torto_arado.db não foi encontrado. "
            "Verifique se ele está na mesma pasta de app.py. "
            "Se ainda não foi criado, execute criar_banco.py uma vez."
        )

    conexao = sqlite3.connect(CAMINHO_BANCO)

    # Permite utilizar chaves estrangeiras nesta conexão.
    conexao.execute("PRAGMA foreign_keys = ON")

    # Permite acessar as colunas pelo nome.
    conexao.row_factory = sqlite3.Row

    return conexao


# ============================================================
# PÁGINA INICIAL
# Endereço: /
# ============================================================

@app.route("/")
def inicio():
    """
    Busca os seis temas cadastrados no banco
    e envia esses dados para inicio.html.
    """

    conexao = conectar()

    temas = conexao.execute("""
        SELECT id, nome, texto
        FROM tema
        ORDER BY id
    """).fetchall()

    conexao.close()

    return render_template(
        "inicio.html",
        temas=temas
    )


# ============================================================
# QUIZ
# Endereço: /quiz
# ============================================================

@app.route("/quiz", methods=["GET", "POST"])
def quiz():
    """
    GET: abre a página com as perguntas.

    POST: recebe as respostas, compara com o gabarito
    e apresenta o resultado.
    """

    conexao = conectar()

    questoes = conexao.execute("""
        SELECT
            id,
            enunciado,
            alternativa_a,
            alternativa_b,
            alternativa_c,
            alternativa_d,
            correta,
            explicacao
        FROM questao
        ORDER BY id
    """).fetchall()

    # POST significa que o visitante enviou o formulário.
    if request.method == "POST":

        pontos = 0

        # Aqui serão guardadas as correções
        # que aparecerão em resultado.html.
        correcoes = []

        # Percorre todas as questões do banco.
        for questao in questoes:

            numero = questao["id"]

            # No HTML, as respostas têm nomes:
            # q1, q2, q3, q4, q5 e q6.
            resposta = request.form.get(
                f"q{numero}",
                ""
            )

            # Compara a letra escolhida com o gabarito.
            acertou = resposta == questao["correta"]

            if acertou:
                pontos += 1

            correcoes.append({
                "numero": numero,
                "acertou": acertou,
                "correta": questao["correta"],
                "explicacao": questao["explicacao"]
            })

        conexao.close()

        return render_template(
            "resultado.html",
            pontos=pontos,
            total=len(questoes),
            correcoes=correcoes
        )

    # Se ninguém enviou respostas, mostra o quiz.
    conexao.close()

    return render_template(
        "quiz.html",
        questoes=questoes
    )


# ============================================================
# PARTICIPAÇÃO DO VISITANTE
# Endereço: /participar
# ============================================================

@app.route("/participar", methods=["GET", "POST"])
def participar():
    """
    GET: mostra o formulário.

    POST: recebe o tema escolhido e a reflexão,
    grava os dados e abre o painel.
    """

    conexao = conectar()

    temas = conexao.execute("""
        SELECT id, nome
        FROM tema
        ORDER BY id
    """).fetchall()

    if request.method == "POST":

        # Recebe os dados preenchidos no HTML.
        tema_id = request.form.get(
            "tema_id",
            ""
        ).strip()

        reflexao = request.form.get(
            "reflexao",
            ""
        ).strip()

        # Confere se os dois campos foram preenchidos.
        if not tema_id or not reflexao:

            conexao.close()

            return render_template(
                "participar.html",
                temas=temas,
                erro="Escolha um tema e escreva uma reflexão."
            )

        # Confere se o tema realmente existe no banco.
        # O formulário mostra somente temas válidos,
        # mas o Python também deve fazer essa verificação.
        tema_valido = conexao.execute("""
            SELECT id
            FROM tema
            WHERE id = ?
        """, (tema_id,)).fetchone()

        if tema_valido is None:

            conexao.close()

            return render_template(
                "participar.html",
                temas=temas,
                erro="Escolha um dos temas apresentados."
            )

        # O HTML limita a 240 caracteres.
        # Esta verificação garante o mesmo limite no Python.
        if len(reflexao) > 240:

            conexao.close()

            return render_template(
                "participar.html",
                temas=temas,
                erro="A reflexão deve ter até 240 caracteres."
            )

        # Grava a escolha e a reflexão no banco.
        conexao.execute("""
            INSERT INTO voto (tema_id, reflexao)
            VALUES (?, ?)
        """, (tema_id, reflexao))

        # Confirma a gravação.
        conexao.commit()

        conexao.close()

        # Após gravar, abre o painel.
        return redirect(
            url_for("painel")
        )

    conexao.close()

    return render_template(
        "participar.html",
        temas=temas
    )


# ============================================================
# PAINEL DE RESULTADOS
# Endereço: /painel
# ============================================================

@app.route("/painel")
def painel():
    """
    Conta os votos de cada tema e mostra
    as oito reflexões mais recentes.
    """

    conexao = conectar()

    # LEFT JOIN mantém no painel até temas com zero votos.
    # COUNT(voto.id) conta apenas os votos existentes.
    contagem = conexao.execute("""
        SELECT
            tema.nome,
            COUNT(voto.id) AS total
        FROM tema
        LEFT JOIN voto
            ON voto.tema_id = tema.id
        GROUP BY
            tema.id,
            tema.nome
        ORDER BY
            total DESC,
            tema.nome
    """).fetchall()

    # Busca as oito reflexões cadastradas mais recentemente.
    reflexoes = conexao.execute("""
        SELECT
            tema.nome,
            voto.reflexao
        FROM voto
        JOIN tema
            ON tema.id = voto.tema_id
        ORDER BY voto.id DESC
        LIMIT 8
    """).fetchall()

    conexao.close()

    # Encontra o maior número de votos.
    # O HTML usa esse número para calcular
    # o comprimento das barras do painel.
    maior = max(
        (item["total"] for item in contagem),
        default=0
    )

    return render_template(
        "painel.html",
        contagem=contagem,
        reflexoes=reflexoes,
        maior=maior
    )


# ============================================================
# INÍCIO DO SERVIDOR
# ============================================================

if __name__ == "__main__":

    # Inicia o sistema no computador local.
    # debug=True facilita identificar erros durante as aulas.
    app.run(debug=True)