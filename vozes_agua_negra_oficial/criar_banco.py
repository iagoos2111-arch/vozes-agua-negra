# Importa o módulo sqlite3.
#
# Esse módulo permite que o Python crie
# e utilize um banco de dados SQLite.
#
# Ele já acompanha a instalação do Python.
# Não é necessário instalar o SQLite separadamente.
import sqlite3


# Cria uma conexão com o banco.
#
# Se o arquivo torto_arado.db ainda não existir,
# o SQLite criará esse arquivo automaticamente.
conexao = sqlite3.connect("torto_arado.db")


# Ativa a verificação das chaves estrangeiras.
conexao.execute("PRAGMA foreign_keys = ON")


# Cria o cursor.
#
# O cursor será utilizado para enviar
# os comandos SQL ao banco de dados.
cursor = conexao.cursor()


# Remove primeiro a tabela voto, caso ela exista.
#
# Ela precisa ser removida antes da tabela tema
# porque possui uma chave estrangeira ligada a ela.
cursor.execute("DROP TABLE IF EXISTS voto")


# Remove a tabela questao, caso ela exista.
cursor.execute("DROP TABLE IF EXISTS questao")


# Remove a tabela tema, caso ela exista.
cursor.execute("DROP TABLE IF EXISTS tema")


# Cria a tabela tema.
cursor.execute("""
CREATE TABLE tema (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT NOT NULL,
    texto TEXT NOT NULL
)
""")


# Cria a tabela das questões do quiz.
cursor.execute("""
CREATE TABLE questao (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    enunciado TEXT NOT NULL,
    alternativa_a TEXT NOT NULL,
    alternativa_b TEXT NOT NULL,
    alternativa_c TEXT NOT NULL,
    alternativa_d TEXT NOT NULL,
    correta TEXT NOT NULL,
    explicacao TEXT NOT NULL
)
""")


# Cria a tabela que armazenará
# as participações dos visitantes.
cursor.execute("""
CREATE TABLE voto (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tema_id INTEGER NOT NULL,
    reflexao TEXT NOT NULL,
    criado_em TEXT DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (tema_id)
        REFERENCES tema(id)
)
""")


# Cria uma lista com os seis temas.
#
# Cada elemento possui dois dados:
# 1. nome do tema;
# 2. texto explicativo.
temas = [
    (
        "Território",

        "A terra representa moradia, trabalho, identidade e "
        "pertencimento. A obra questiona a desigualdade entre "
        "quem trabalha no território e quem possui poder legal "
        "sobre ele."
    ),

    (
        "Ancestralidade e memória",

        "Conhecimentos, lembranças e práticas atravessam gerações. "
        "Preservar a memória ajuda a enfrentar o apagamento de "
        "histórias negras e rurais."
    ),

    (
        "Racismo estrutural",

        "A abolição legal não eliminou desigualdades. Terra, direitos "
        "e oportunidades continuaram distribuídos de maneira desigual "
        "na sociedade brasileira."
    ),

    (
        "Trabalho e exploração",

        "Os moradores produzem e cuidam da terra, mas vivem sem "
        "segurança e reconhecimento justos. O trabalho aparece ligado "
        "a relações históricas de dependência."
    ),

    (
        "Protagonismo feminino",

        "As mulheres não aparecem apenas como vítimas. Elas trabalham, "
        "preservam conhecimentos, tomam decisões e constroem formas "
        "de resistência."
    ),

    (
        "Religiosidade e respeito",

        "O jarê aparece ligado à espiritualidade, à cura, à "
        "ancestralidade e à vida comunitária. Práticas religiosas "
        "de matriz africana devem ser abordadas sem caricatura "
        "ou intolerância."
    )
]


# Insere os seis temas na tabela.
#
# O primeiro ponto de interrogação recebe o nome.
# O segundo recebe o texto.
cursor.executemany("""
INSERT INTO tema (
    nome,
    texto
)
VALUES (?, ?)
""", temas)


# Cria a lista com as questões.
#
# Cada questão contém:
# enunciado;
# alternativas A, B, C e D;
# letra correta;
# explicação.
questoes = [
    (
        "Na apresentação, a terra representa:",

        "Somente produção agrícola.",

        "Moradia, trabalho, identidade e pertencimento.",

        "Um espaço sem relação com memória.",

        "Apenas propriedade dos trabalhadores.",

        "B",

        "A terra representa moradia, trabalho, identidade "
        "e pertencimento."
    ),

    (
        "Preservar memórias ajuda a:",

        "Apagar diferenças culturais.",

        "Substituir experiências humanas por números.",

        "Enfrentar o apagamento de histórias negras e rurais.",

        "Evitar a transmissão de conhecimentos.",

        "C",

        "A memória preserva experiências e conhecimentos "
        "transmitidos entre gerações."
    ),

    (
        "Compreender o racismo como estrutural significa entender que:",

        "A abolição eliminou todas as desigualdades.",

        "O racismo existe apenas quando há uma ofensa.",

        "As desigualdades também permanecem nas estruturas sociais.",

        "O racismo pertence somente ao passado.",

        "C",

        "Direitos e oportunidades podem continuar distribuídos "
        "de maneira desigual."
    ),

    (
        "Na obra, trabalho e exploração aparecem relacionados porque:",

        "Os trabalhadores controlam toda a propriedade.",

        "Não existe produção agrícola na comunidade.",

        "Todos recebem os mesmos direitos.",

        "Quem produz pode viver sem segurança e reconhecimento justos.",

        "D",

        "O trabalho acontece dentro de relações históricas "
        "de dependência."
    ),

    (
        "Como o projeto apresenta as mulheres?",

        "Somente como vítimas.",

        "Como sujeitos de conhecimento, decisão e resistência.",

        "Como personagens sem participação social.",

        "Apenas como cuidadoras.",

        "B",

        "O protagonismo feminino envolve conhecimento, "
        "trabalho, decisão e resistência."
    ),

    (
        "Qual é a abordagem adequada para o jarê?",

        "Tratamento respeitoso, ligado à espiritualidade "
        "e à ancestralidade.",

        "Uso apenas como decoração.",

        "Apresentação como uma superstição inferior.",

        "Imitação cômica durante a exposição.",

        "A",

        "Práticas religiosas de matriz africana exigem "
        "respeito e contextualização."
    )
]


# Insere todas as questões no banco.
cursor.executemany("""
INSERT INTO questao (
    enunciado,
    alternativa_a,
    alternativa_b,
    alternativa_c,
    alternativa_d,
    correta,
    explicacao
)
VALUES (?, ?, ?, ?, ?, ?, ?)
""", questoes)


# Salva definitivamente as alterações.
conexao.commit()


# Consulta os temas que acabaram de ser cadastrados.
temas_cadastrados = cursor.execute("""
SELECT
    id,
    nome
FROM tema
ORDER BY id
""").fetchall()


# Consulta a quantidade de questões.
quantidade_questoes = cursor.execute("""
SELECT COUNT(*)
FROM questao
""").fetchone()[0]


# Mostra uma confirmação no terminal.
print("Banco de dados criado com sucesso!")

print("\nTemas cadastrados:")


# Percorre os temas encontrados no banco.
for tema in temas_cadastrados:

    # tema[0] representa o id.
    # tema[1] representa o nome.
    print(tema[0], "-", tema[1])


# Mostra a quantidade de perguntas.
print(
    "\nQuantidade de questões:",
    quantidade_questoes
)


# Encerra a conexão com o banco.
conexao.close()