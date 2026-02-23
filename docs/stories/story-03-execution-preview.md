# Story: Implementar Tela de Preview na Execução do Dev

## 📋 Status
**Status:** Ready for Dev

## 📖 Story
Como usuário do sistema,
Eu quero ter a opção de alternar entre "Preview" e "Code" na tela final de Execução (Resultados do Desenvolvedor),
Para que eu possa testar e visualizar o resultado visual daquilo que o Dev construiu, e não apenas o código gerado.

## 🎯 Acceptance Criteria
- [ ] A tela de "Resultados" exibindo as entregas do Desenvolvedor (Fox Full-Stack) deve ser dividida em **duas abas/opções de visualização**: 
      1. **Preview** (para exibir o visual).
      2. **Code** (para exibir o arquivo markdown/código).
- [ ] A aba **Code** deve manter o comportamento atual, utilizando `st.code()` para formatar apropriadamente.
- [ ] A aba **Preview** deve tentar renderizar adequadamente a interface que foi gerada na demanda (ex: renderizando via `st.components.v1.html` as strings HTML resultantes, se a demanda tiver sido a criação de uma web interface, ou exibições de diagramas e textos formatados quando couber).
- [ ] A interface e o layout das abas ("Preview" / "Code") devem remeter ao estilo de sub-janelas ou tabs como em IDEs cloud (referência no mockup visual).

## 🛠️ Tasks
- [ ] Localizar em `app_completo.py` o ponto de exibição dos resultados (possivelmente perto de `st.markdown("### 💻 Desenvolvedor Python - Código e Testes")`).
- [ ] Substituir o bloco puramente textual pelo uso de abas do Streamlit, como: `tab_preview, tab_code = st.tabs(["Preview", "Code"])`.
- [ ] Na aba `tab_code`, inserir: `st.code(st.session_state.resultados.get("Desenvolvedor Python", ...))`.
- [ ] Na aba `tab_preview`, inserir as heurísticas para a melhor pré-visualização. Se for um código front-end (HTML/CSS/JS exportado), ele deve ser inserido em um IFrame/HTML de Preview (tamanho fixo ou autoajustável). 

## 📝 Dev Agent Record
- [ ] Componente `st.tabs` implementado e funcionando sem quebrar states.
- [ ] Resultado na UI alterna perfeitamente o render e o source code.

---
**CodeRabbit Integration:** Padrão

## 🛡️ QA Results
- [x] O painel Fox Full-Stack Developer no app_completo.py subdivide seu rendering utilizando o component `st.tabs(["👁️ Preview", "📝 Code"])`.
- [x] Foi criado o regex para extração inteligente e renderizada usando `components.html(..., height=600, scrolling=True)` a fim de renderizar o iframe via streamlit components quando string HTML for detectada no resultado do Developer.
- [x] O uso de fall-back via `st.markdown(dev_result)` confere tratamento a saídas puras sem block code em formato de front-end. E a cópia do output não formatada permanece intacta através do componente nativo `st.code(dev_result)`.
- [x] A execução visual se equipara ao design/UX pretendido de IDE cloud.

**Veredicto:** PASS (Aprovado).
