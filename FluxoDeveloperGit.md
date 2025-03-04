Copy
# Fluxo de Trabalho Git para Equipe

Este documento descreve o fluxo de trabalho Git que deve ser seguido pela equipe. Ele foi projetado para garantir um desenvolvimento organizado, colaborativo e eficiente, evitando conflitos e problemas em produção.

---

## Visão Geral do Fluxo

1. **Branch `main`**:
   - Contém o código estável e pronto para produção.
   - Ninguém trabalha diretamente nela para evitar problemas em produção.

2. **Branch `develop`**:
   - Criada a partir da `main`.
   - Serve como a branch de integração para o desenvolvimento.
   - Todas as novas funcionalidades, correções e melhorias são mescladas aqui antes de irem para a `main`.

3. **Branches de Tarefas**:
   - Criadas a partir da `develop`.
   - Cada desenvolvedor trabalha em sua própria branch para implementar uma funcionalidade ou corrigir um bug.
   - Após concluir o trabalho, a branch é mesclada de volta na `develop`.
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

4. **Mesclagem na `main`**:
   - Quando o código na `develop` está estável e pronto para produção, ele é mesclado na `main`.
   - Isso geralmente acontece durante um processo de release.

---

## Passo a Passo do Fluxo

### 1. Verificar e Sincronizar a Branch `develop`

Antes de começar, certifique-se de que a branch `develop` está atualizada.
1. **Verifique se a branch `develop` existe remotamente**:
   ```bash
   git fetch origin
   git branch -r
   ```
2. Crie uma cópia local da branch develop (se ainda não tiver):
```bash
git checkout develop
```
3. Atualize a branch develop local:
```bash
git pull origin develop   
```

### 2. Criar uma Nova Branch de Tarefa
Agora que você está na branch develop, crie uma nova branch para trabalhar na sua tarefa.

2.1 Padrão de Nomenclatura para Branches
Use o seguinte padrão para nomear suas branches:
   * feature/: Para novas funcionalidades.
     * Exemplo: feature/Chamado-123-add-login-page
   * bugfix/: Para correções de bugs.
     * Exemplo: bugfix/456-fix-login-error
   * hotfix/: Para correções urgentes em produção.
     * Exemplo: hotfix/789-fix-critical-security-issue
   * refactor/: Para refatorações de código.
     * Exemplo: refactor/234-improve-code-structure
   * chore/: Para tarefas de manutenção ou configuração.
     * Exemplo: chore/567-update-dependencies
   * docs/: Para atualizações na documentação.
     * Exemplo: docs/890-update-readme

2.2 Criando a Branch
```bash
git checkout -b feature/nova-funcionalidade

```
3. Trabalhar na Nova Branch
Faça as alterações necessárias e siga as boas práticas de commits.

3.1 Padrão de Commits (Conventional Commits)
Use o padrão Conventional Commits para mensagens de commit:

```bash
<tipo>(<escopo opcional>): <mensagem breve>
```
 * tipo: Define o propósito da mudança (ex: feat, fix, docs, style, refactor, test, chore).
 * escopo (opcional): Indica a área do código afetada.
 * mensagem breve: Explica a mudança de forma clara e concisa.

Exemplos:

```bash
git commit -m "feat(auth): adicionar autenticação com JWT"
git commit -m "fix(api): corrigir erro na requisição de usuários"
git commit -m "docs(readme): atualizar seção de instalação"
```
3.2 Emojis para Commits (Opcional)
Você pode usar emojis para tornar os commits mais visuais e descritivos. Aqui estão alguns exemplos:

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

Exemplo:
```bash
git commit -m "✨ feat: adicionar novo botão de login"
git commit -m "🐛 fix: corrigir erro no cálculo de frete"
```

4. Mesclar na develop
Quando terminar o trabalho na sua branch de tarefa, siga os passos abaixo para mesclá-la na develop.

   4.1 Volte para a branch develop:
    ```bash
    git checkout develop
    ```
   4.2 Atualize a develop com as últimas alterações remotas:
    ```bash
    git pull origin develop
    ```
   4.3 Mescle sua branch de tarefa na develop:
    ```bash
    git merge feature/nova-funcionalidade
    ```
   4.4 Envie as alterações para o repositório remoto:
    ```bash
    git push origin develop
    ```
5.Mesclar a develop na main (Quando Pronto)
Quando o código na develop estiver estável e pronto para produção, mescle-o na main.

    5.1 Mude para a branch main:
    ```bash
    git checkout main
    ```
    5.2 Atualize a main com as últimas alterações remotas:
    ```bash
    git pull origin main
    ```
    5.3 Mescle a develop na main:
    ```bash
    git merge develop
    ```    
    5.4 Envie as alterações para o repositório remoto:
    ```bash
    git push origin main
    ```

6. Excluir a Branch de Tarefa
Após mesclar a branch de tarefa na develop e na main, você pode excluí-la.

   6.1 Excluir a branch local:
    ```bash
    git branch -d feature/nova-funcionalidade
    ```
    6.2 Excluir a branch remota:
    ```bash
    git push origin --delete feature/nova-funcionalidade
    ```

7. Dicas e Boas Práticas
 * Sincronize o Repositório Local:
   Após excluir uma branch remota, outros desenvolvedores devem sincronizar seus repositórios locais:

    ```bash
    git fetch --prune
    ```
 * Evite Commits Genéricos:
   Sempre descreva claramente o que foi feito no commit. Evite mensagens como "atualização" ou "correção".

 * Resolva Conflitos com Cuidado:
   Ao mesclar branches, conflitos podem ocorrer. Certifique-se de testar o código após resolver conflitos.

 * Use Pull Requests (PRs):
   Para branches importantes, crie um PR no GitHub/GitLab para revisão do código antes de mesclar na develop.

## Resumo dos Comandos Principais
Ação	Comando
Criar uma nova branch	git checkout -b feature/nova-funcionalidade
Fazer commit	git add . && git commit -m "tipo(escopo): mensagem breve"
Mesclar na develop	git checkout develop && git pull origin develop && git merge feature/nova-funcionalidade
Mesclar na main	git checkout main && git pull origin main && git merge develop
Excluir branch local	git branch -d feature/nova-funcionalidade
Excluir branch remota	git push origin --delete feature/nova-funcionalidade
Fluxo Visual
```plaintext
main    ----------------------------(merge)----------------------------> Release
           ↑                                     ↑
develop   |----(merge)----> feature/branch ---->|
```   

```mermaid
graph TD;
    A[Trabalhar no Repositório] -->|Clone| B[git clone];
    B -->|Criar nova branch| C[git checkout -b feature-branch];
    C -->|Fazer alterações| D[Modificar arquivos];
    D -->|Adicionar mudanças| E[git add .];
    E -->|Commitar mudanças| F[git commit -m "Descrição"];
    F -->|Enviar para o repositório remoto| G[git push origin feature-branch];
    G -->|Criar Pull Request| H[Revisão de código];
    H -->|Merge na main| I[git merge];
    I -->|Atualizar localmente| J[git pull origin main];
```
