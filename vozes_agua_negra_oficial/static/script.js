/*
Localiza o formulário do quiz.
*/
const formQuiz = document.getElementById("formQuiz");


/*
Só executa esta parte se o formulário
do quiz estiver na página.
*/
if (formQuiz) {

    /*
    Observa o envio do formulário.
    */
    formQuiz.addEventListener(
        "submit",
        function (evento) {

            /*
            Localiza todas as questões.
            */
            const questoes =
                document.querySelectorAll(".questao");


            /*
            Percorre todas as questões.
            */
            for (
                let indice = 0;
                indice < questoes.length;
                indice++
            ) {

                /*
                Procura uma alternativa marcada
                dentro da questão atual.
                */
                const marcada =
                    questoes[indice].querySelector(
                        "input:checked"
                    );


                /*
                Se nenhuma alternativa foi marcada...
                */
                if (!marcada) {

                    /*
                    Impede o envio do formulário.
                    */
                    evento.preventDefault();


                    /*
                    Mostra um aviso.
                    */
                    alert(
                        "Responda à questão " +
                        (indice + 1) +
                        "."
                    );


                    /*
                    Encerra a função.
                    */
                    return;
                }
            }
        }
    );
}


/*
Localiza o campo de reflexão.
*/
const reflexao =
    document.getElementById("reflexao");


/*
Localiza o contador de caracteres.
*/
const contador =
    document.getElementById("contador");


/*
Só executa se os dois elementos existirem.
*/
if (reflexao && contador) {

    /*
    Observa cada alteração no campo.
    */
    reflexao.addEventListener(
        "input",
        function () {

            /*
            Conta os caracteres digitados.
            */
            const quantidade =
                reflexao.value.length;


            /*
            Atualiza a mensagem.
            */
            contador.textContent =
                quantidade +
                " de 240 caracteres";
        }
    );
}
