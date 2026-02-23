# Design System: Squad-AI 🎨

Bem-vindo ao Design System do **Squad-AI**. Este documento define os padrões visuais e componentes seguindo a metodologia **Atomic Design**.

## 1. Design Tokens (Atoms)

### Cores & Gradientes
| Nome | Valor | Exemplo |
|------|-------|---------|
| **Core Primary** | `#667eea` | Indigo |
| **Core Secondary** | `#764ba2` | Purple |
| **Main Gradient** | `linear-gradient(90deg, #667eea 0%, #764ba2 100%)` | Header |
| **Stat Gradient** | `linear-gradient(135deg, #667eea 0%, #764ba2 100%)` | Dashboard |
| **Neutral Bg** | `#f8f9fa` | Cards/Background |

### Tipografia
- **Font-Family**: System Default (Inter/Roboto/Segoe UI)
- **H1**: Bold, White (no header)
- **Subheader**: Semibold, Indigo accent.

---

## 2. Componentes (Organisms)

### 👔 Main Header
Container com gradiente horizontal que fixa o contexto do sistema no topo.
- **Style**: `.main-header`
- **Context**: Título + Descrição do Sistema.

### 📋 Demanda Card
Container para listagem no Histórico com borda lateral de destaque.
- **Style**: `.demanda-card`
- **Properties**: `border-left: 4px solid #667eea`, `border-radius: 8px`.

### 📊 Stat Box
Card de alto impacto para métricas quantitativas.
- **Style**: `.stat-box`
- **Properties**: Gradiente diagonal, White text, centered.

---

## 3. Interaction Patterns

### Real-time Logs (`st.status`)
- **Status**: Expansível.
- **Usage**: Cada agente escreve seu log interno no container durante o processamento.
- **Verdict**: Garante transparência e reduz ansiedade de espera.

### Guardiões de Formulário
- **Logic**: Validação obrigatória de Título e Descrição.
- **Feedback**: `st.error` toast persistente até a correção.

---

## 4. Roadmap UX
1. **Chat Interaction**: Migrar outputs de agentes para `st.chat_message`.
2. **Theming**: Implementar suporte full a Dark Mode.
3. **Micro-interactions**: Adicionar Lottie animations para estados "Thinking".

— Uma, desenhando com empatia 💝
