# datalake

Estudo de git hub

Passo 1: Clonar o Repositório
Primeiro, você precisa ter o repositório localmente no seu computador. Execute o seguinte comando no terminal:

``` bash
git clone https://github.com/danielcs7/datalake.git
```


Isso criará uma pasta chamada datalake com todos os arquivos do projeto.


Passo 2: Navegar até o Diretório
Depois de clonar, entre no diretório do projeto:

bash
Copiar
Editar
cd datalake
Passo 3: Verificar o Status do Repositório
Antes de começar a trabalhar, veja em qual branch você está:

bash
Copiar
Editar
git status
Se estiver na main, o ideal é criar uma branch separada para sua tarefa.

Passo 4: Criar uma Nova Branch para sua Tarefa
No trabalho em equipe, cada pessoa normalmente cria uma branch para desenvolver novas funcionalidades ou corrigir problemas.

Para criar uma nova branch e mudar para ela, use:

bash
Copiar
Editar
git checkout -b minha-feature
Substitua minha-feature pelo nome da funcionalidade ou correção que você está fazendo.

Passo 5: Fazer as Modificações no Código
Agora você pode editar arquivos, criar novos arquivos ou modificar o que for necessário.

Passo 6: Adicionar e Commitar as Alterações
Depois de fazer as mudanças, adicione os arquivos ao commit:

bash
Copiar
Editar
git add .
E faça um commit com uma mensagem descritiva:

bash
Copiar
Editar
git commit -m "Adicionei nova funcionalidade X"
Passo 7: Enviar para o GitHub
Agora, envie a branch para o repositório remoto no GitHub:

bash
Copiar
Editar
git push origin minha-feature
Passo 8: Criar um Pull Request (PR)
Acesse o repositório no GitHub:
👉 Datalake no GitHub
Clique na aba Pull Requests.
Clique em New Pull Request.
Escolha a branch minha-feature e compare com main.
Adicione uma descrição do que foi feito e clique em Create Pull Request.
Espere a revisão dos colegas antes de fazer o merge.
Passo 9: Atualizar Seu Código Localmente
Se outros membros da equipe fizeram mudanças na main, você precisa manter seu código atualizado.

Para baixar as últimas atualizações:

bash
Copiar
Editar
git checkout main
git pull origin main
E para atualizar sua branch com as novas mudanças:

bash
Copiar
Editar
git checkout minha-feature
git merge main
Passo 10: Depois do Merge, Apague a Branch
Depois que sua feature for aceita e integrada à main, você pode apagar a branch localmente e no GitHub:

bash
Copiar
Editar
git branch -d minha-feature
git push origin --delete minha-feature
Bônus: Dicas para Trabalho em Equipe no GitHub
✅ Use commits pequenos e descritivos
✅ Crie branches para cada nova funcionalidade ou correção
✅ Sincronize frequentemente com a main para evitar conflitos
✅ Participe das revisões de código (Code Reviews)
✅ Escreva um bom README e documentação se for necessário

Se precisar de mais alguma coisa, só perguntar! 🚀







Esta conversa foi útil at