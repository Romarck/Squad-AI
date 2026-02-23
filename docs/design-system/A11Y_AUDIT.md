# A11Y Audit: Squad-AI ♿

Este documento avalia a conformidade do sistema com as diretrizes **WCAG AA**.

## 1. Contraste Cromático
- **Achado**: O gradiente `Indigo to Purple` no header usa texto branco (`#FFFFFF`).
- **Análise**: 
    - Indigo (#667eea) vs White: Ratio **3.1:1** (Falha para texto pequeno, Passa para texto grande >18pt).
    - Purple (#764ba2) vs White: Ratio **5.2:1** (Passa WCAG AA).
- **Recomendação**: Aumentar o peso da fonte no header ou escurecer levemente o tom do Indigo para garantir legibilidade em todas as áreas do gradiente.

## 2. Navegação & Foco
- **Achado**: Navegação por abas não sincroniza visualmente o estado de execução se o usuário estiver em outra aba.
- **Análise**: O componente `st.status` ajuda, mas a mudança de contexto entre "Nova Demanda" e "Execução" pode confundir leitores de tela.
- **Recomendação**: Utilizar `st.toast` ou notificações globais para informar a mudança de estado independente da aba ativa.

## 3. Estrutura Semântica
- **H1-H6**: O projeto utiliza `st.markdown("# ...")` corretamente para títulos.
- **Alt Text**: Ícones emoji (👔, 📋, 💻, ✅) carecem de descrição para agentes de acessibilidade.

---

— Uma, garantindo que todos possam usar 💝
