# Story: Corrigir Visualização na Aba de Preview para Código Python

## 📋 Status
**Status:** Ready for Dev

## 📖 Story
Como usuário do sistema,
Eu quero que a aba de "Preview" renderize corretamente o código caso o resultado gerado pelo agente seja um script (Python, etc) e não apenas HTML/UI,
Para que eu consiga ler e interpretar os blocos de código sem que eles fiquem formatados incorretamente ou fora da caixa de código, enquanto a aba "Code" mostra o raw markdown.

## 🎯 Acceptance Criteria
- [ ] No arquivo `app_completo.py`, ao renderizar a aba de **Preview** (`tab_preview`), caso o regex *não encontre um HTML renderizável*, o sistema deve verificar se há formatação Markdown comumente injetada em um container Python.
- [ ] Se houver um bloco ````python` sendo enviado para a tab preview, a UI não deve quebrar nem exibi-lo esteticamente mal; o fallback `st.markdown(dev_result)` deve funcionar de forma nativa e ser agradável de ler. Contudo, atualmente o Streamlit pode não estar processando a altura dinamicamente ou renderizando um bloco "cru".
- [ ] Se o output for apenas código Python (```python...```), a renderização na aba "Preview" deve usar as marcações de Markdown nativas (`st.markdown`) corretamente. A aba "Code" exibe o raw (via `st.code(dev_result, language="markdown")`).
- [ ] O problema específico dos screenshots (o código apareceu formatado solto, sem background dark code block na aba Preview) deve ser corrigido ajustando o comportamento de `st.markdown()` ou removendo wrappers problemáticos que impeçam o code highlighting do st.markdown.

## 🛠️ Tasks
- [ ] Inspecionar a forma que a string `dev_result` chega do agente Fox Full-Stack Developer em `app_completo.py`.
- [ ] Otimizar a aba Preview: caso o `html_match` falhe, garantir que `st.markdown(dev_result)` lide adequadamente com blocos ````python`.
- [ ] Ajustar a aba Code: modificar `st.code(dev_result)` para `st.code(dev_result, language="markdown")` para o raw markdown ficar com highlight adequado.

## 📝 Dev Agent Record
- [ ] Lógicas de fallback em Preview foram otimizadas.
- [ ] Renderização em Code usa a tag de language "markdown".

---
**CodeRabbit Integration:** Padrão

## 📝 Dev Agent Record
- [x] Lógicas de fallback em Preview foram otimizadas separando os blocks e inserindo no Streamlit usando `st.code()`.
- [x] Renderização em Code usa a tag de language "markdown".
- [x] O CSS que quebrava o display do st.markdown de code blocks (`html, body, [class*="css"]`) foi reestruturado para ser mais amigável a código fonte.

**CodeRabbit Integration:** Padrão

## 🛡️ QA Results
- [x] O CSS Global foi ajustado para preservar fontes monoespaçadas nas tags de código, garantindo visualização confortável.
- [x] O regex modificado agora avalia toda a string para renderizar adequadamente `st.code` em todos os trechos intermisturados no formato markdown, superando as limitações do bloco livre.
- [x] O texto base da tab "Code" adicionou `language="markdown"` permitindo highlight apropriado da documentação e código combinados.
- [x] A nova lógica não deve gerar quebras com outras entregas.

**Veredicto:** PASS (Aprovado).
