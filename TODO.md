# **TODO - AtlantisBot**

## **Sorteios**

- Adicionar Sistema de sorteios
  - Comando administrativo, usuário digita `!giveaway`
  - Bot pergunta Nome da giveaway, data de ínicio e final (com horário, mostrando o formato), Prêmio, descrição (opcional), emoji a ser usado, chat a enviar a mensagem da giveaway
  - Requisito ser um User para reagir e participar, caso alguém reaja q não seja um User, o bot tentará (try/except) enviar uma mensagem no pvt dela, explicando o motivo e ensinando a se autenticar, e depois removerá a reação, caso alguém reja e seja um User, o bot irá enviar uma mensagem no pvt dela confirmando sua participação
  - Considerar verificar mensagens criadas de giveaway a cada alguns minutos, pro caso do bot perder algum evento de reação em período offline, para tentar entrar ele na giveaway novamente
  - Notificar administração, e atualizar mensagem com o ganhador após a giveaway finalizar 

---

## **Autenticação**

- Adicionar comando `!auth <user do discord>` para adicionar uma outra conta (ex. De mic/fone) e sincronizar as duas

---

## **Sistema de Inatividade**

- Criar comando para verificar usuários inativos a mais de X tempo com Y exp ganhos, valores customizáveis
  - Configurar também um padrão caso nenhum argumento seja passado

---

## **Amigo Secreto**

- ~~Utilizar ingame name da autenticação ao invés de pedir do usuário~~
- ~~Não permitir usuário se cadastrar caso tenha warning date ou caso esteja disabled, ou caso esteja não-autenticado~~
- ~~Ajustar data para ser configurável com um comando~~
- Remover do amigo secreto caso a pessoa receba uma warning de autenticação ou caso tenha sido desabilitada
- ~~Na hora de enviar o amigo secreto sorteado, utilizar o atual nome cadastrado do Usuário~~

---

## ClanInfo

- Adicionar informação do nick atual in-game da pessoa no comando `!claninfo`, caso ela esteja autenticada

---

## Sistema de pontos

***Em construção...***
