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
   - 3.1 Baseada no Tipo de Tarefa
       * feature/: Para novas funcionalidades.
         * Exemplo: feature/add-login-page
       * bugfix/: Para correções de bugs.
         * Exemplo: bugfix/fix-login-error
       * hotfix/: Para correções urgentes em produção.
         * Exemplo: hotfix/fix-critical-security-issue
       * refactor/: Para refatorações de código.
         * Exemplo: refactor/improve-code-structure
       * chore/: Para tarefas de manutenção ou configuração.
         * Exemplo: chore/update-dependencies
       * docs/: Para atualizações na documentação.
         * Exemplo: docs/update-readme

   - 3.2 Incluir o Número da Issue ou Ticket
       * Se você usa um sistema de issues (como Jira, GitHub Issues, etc.), inclua o número da issue no nome da branch.
         * Exemplo: feature/123-add-login-page ou bugfix/456-fix-login-error
   - 3.3 Usar Nomes Descritivos e Curtos
       * Evite nomes genéricos como minha-branch ou teste. Em vez disso, use nomes que descrevam claramente o propósito da branch.
         * Exemplo: feature/user-profile-avatar em vez de feature/new-stuff.
   - 3.4 Evitar Caracteres Especiais
       * Use apenas letras minúsculas, números e hifens (-) ou underlines (_).
       * Evite espaços, acentos ou caracteres especiais.

```bash
git checkout -b feature/nova-funcionalidade
```
Isso cria uma nova branch a partir da develop e já muda para ela.

## 4. Trabalhar na Nova Branch
Faça as alterações necessárias e faça commits:
   - 4.1 Padrão Convencional de Commits (Conventional Commits)
       * Esse é um dos mais usados, principalmente em projetos que utilizam CI/CD e versionamento semântico.
   
   ```bash
    <tipo>(<escopo opcional>): <mensagem breve>
   ```

       - tipo: Define o propósito da mudança.
       - escopo (opcional): Indica a área do código afetada.
       - mensagem breve: Explica a mudança.
     
   - Exemplos:
     ```bash
        feat(auth): adicionar autenticação com JWT
        fix(api): corrigir erro na requisição de usuários
        docs(readme): atualizar seção de instalação
        style(css): ajustar espaçamento do botão
        refactor(database): melhorar estrutura das tabelas
        test(services): adicionar testes para login
        chore(ci): atualizar configuração do GitHub Actions
     ```
| Emoji  | Tipo       | Uso |
|--------|-----------|--------------------------------------------------|
| ✨      | feat      | Adiciona uma nova funcionalidade |
| 🐛      | fix       | Corrige um bug |
| 🔥      | fix       | Remove código ou arquivos desnecessários |
| 📝      | docs      | Alterações na documentação |
| 🎨      | style     | Melhorias na formatação do código (sem alterar lógica) |
| ♻️      | refactor  | Refatoração do código (sem alterar funcionalidade) |
| 🚀      | perf      | Melhoria de performance |
| ✅      | test      | Adiciona ou modifica testes |
| 📦      | chore     | Atualizações de dependências, build, CI/CD |
| 🔧      | chore     | Alterações na configuração do projeto |
| 📜      | license   | Alterações na licença do projeto |
| 🚨      | lint      | Correção de erros de linting |
| 📌      | chore     | Fixação de versões de dependências |
| 🔖      | release   | Criação de uma nova versão/release |
| 👷      | ci        | Alterações na pipeline de CI/CD |
| 💄      | style     | Alterações na UI/UX do projeto |
| 🚑      | hotfix    | Correção crítica em produção |
| 💥      | break     | Introdução de mudanças que quebram compatibilidade |
| 🚧      | wip       | Trabalho em progresso (Work In Progress) |
| 🗃️     | db        | Mudanças no banco de dados |
| 🔄      | sync      | Sincronização de branches |
| ⚡      | perf      | Melhorias na performance do código |
| 🛑      | security  | Melhorias relacionadas à segurança |
| 🍱      | assets    | Adição ou modificação de assets (imagens, vídeos, etc.) |
| 🚚      | move      | Movimentação ou renomeação de arquivos |
| ✏️      | typo      | Correção de erros de digitação |
| 🛠️     | build     | Melhorias na estrutura do build do projeto |
| ➕      | deps      | Adição de novas dependências |
| ➖      | deps      | Remoção de dependências desnecessárias |
| 🔍      | seo       | Melhorias em SEO (Search Engine Optimization) |
| 🛂      | auth      | Mudanças na autenticação e controle de acesso |
| 📈      | analytics | Adição ou alteração de métricas e tracking |

Exemplos de uso no gitbash:
```bash
git commit -m "✨ feat: adicionar novo botão de login"
git commit -m "🐛 fix: corrigir erro no cálculo de frete"
git commit -m "📦 chore: atualizar dependências do projeto"
git commit -m "📝 docs: adicionar documentação para API"
git commit -m "🚀 perf: otimizar consulta ao banco de dados"
git commit -m "🔧 chore: ajustar configuração do ESLint"
git commit -m "🚑 hotfix: corrigir erro crítico na API"

```
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