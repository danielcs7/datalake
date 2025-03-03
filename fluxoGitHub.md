# Fluxo de Trabalho que Você Descreveu
1 - Branch main:
  * Contém o código estável e pronto para produção.
  * Ninguém trabalha diretamente nela para evitar problemas em produção.

2 - Branch develop:
  * Criada a partir da main.
  * Serve como a branch de integração para o desenvolvimento.
  * Todas as novas funcionalidades, correções e melhorias são mescladas aqui antes de irem para a main.

3 - Branches de Tarefas (por exemplo, feature/, bugfix/, etc.):

  * Criadas a partir da develop.
  * Cada desenvolvedor trabalha em sua própria branch para implementar uma funcionalidade ou corrigir um bug.
  * Após concluir o trabalho, a branch é mesclada de volta na develop.

4 - Mesclagem na main:
  * Quando o código na develop está estável e pronto para produção, ele é mesclado na main.
  * Isso geralmente acontece durante um processo de release.

# Passo a Passo do Fluxo
## 1 - Verifica se a Branch develop existe:
  ```bash
  git fetch origin
  git branch -r
  ```
  Se a branch develop já existe remotamente, mas você não tem uma cópia local dela, siga estes passos:

  Crie uma cópia local da branch develop:
  ```bash
  git checkout develop
  ```
  Se a branch develop não existir localmente, o Git vai criar automaticamente uma cópia local a partir da branch remota origin/develop.

## 2 - Atualize sua branch develop local para garantir que está sincronizada com a remota:
```bash
git pull origin develop
```

## 3. Criar uma Nova Branch de Tarefa a Partir da develop
Agora que você está na branch develop, crie uma nova branch para trabalhar na sua tarefa (por exemplo, uma feature ou bugfix):
```bash
git checkout -b feature/nova-funcionalidade
```
Isso cria uma nova branch a partir da develop e já muda para ela.

## 4. Trabalhar na Nova Branch
Faça as alterações necessárias e faça commits:
```bash
git add .
git commit -m "Implementa nova funcionalidade"
```
## 5. Mesclar na develop
Quando terminar o trabalho na sua branch de tarefa, mescle-a de volta na develop:

   1 - Volte para a branch develop:
    ```bash
    git checkout develop
    ```
   2 - Atualize a develop com as últimas alterações remotas (se houver):
    ```bash
    git pull origin develop 
    ```
   3 - Mescle sua branch de tarefa na develop:
    ``` bash
    git merge feature/nova-funcionalidade 
    ```
   4 - Envie as alterações para o repositório remoto:
    ```bash
    git push origin develop 
    ```

## 6 Mesclar a develop na main (Quando Pronto)
Quando o código na develop estiver estável e pronto para produção, mescle-o na main:

1 - Mude para a branch main:
```bash
git checkout main
```
2 - Atualize a main com as últimas alterações remotas (se houver):
```bash
git pull origin main
```
3 - Mescle a develop na main:
```bash
git merge develop
```
4 - Envie as alterações para o repositório remoto:
```bash
git push origin main
```