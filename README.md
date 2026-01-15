# ⚡ Kelven Optimizer PRO v2.0

<div align="center">

![Version](https://img.shields.io/badge/version-2.0-blue.svg)
![Platform](https://img.shields.io/badge/platform-Windows%2010%2F11-lightgrey.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)
![Downloads](https://img.shields.io/github/downloads/kelvenapk/kelven-optimizer/total.svg)

**Sistema Inteligente de Otimização para Windows com Detecção Automática de Hardware**

[Download](https://github.com/kelvenapk/kelven-optimizer/releases/latest) • [Discord](https://discord.gg/gNPhS3m3QF) • [Reportar Bug](https://github.com/kelvenapk/kelven-optimizer/issues)

</div>

---

## 🎯 Visão Geral

Kelven Optimizer PRO é uma ferramenta completa de otimização para Windows que oferece **157 tweaks inteligentes** organizados em 10 categorias, com detecção automática de hardware e interface moderna.

### ✨ Destaques

- 🚀 **157 Tweaks Inteligentes** - Otimizações profundas do sistema
- 🎮 **Modo Gaming** - Configurações específicas para jogos
- 🧹 **Limpeza Profissional** - Libera RAM e espaço em disco
- 🗜️ **Compactação do Windows** - Economiza GB de espaço
- 🔍 **Detecção de Hardware** - Identifica CPU/GPU automaticamente
- 📊 **Monitor em Tempo Real** - CPU, RAM e Disco
- 🎨 **Interface Moderna** - Design dark com animações
- 🔄 **Atualizações Automáticas** - Sistema integrado ao GitHub

---

## 📦 Download e Instalação

### Opção 1: Executável (Recomendado)

1. Baixe o arquivo `kelven-optimizer2.0.exe` da [página de releases](https://github.com/kelvenapk/kelven-optimizer/releases/latest)
2. Execute como **Administrador** (clique direito → Executar como administrador)
3. Pronto! O programa está pronto para uso

### Opção 2: Código Fonte

```bash
# Clone o repositório
git clone https://github.com/kelvenapk/kelven-optimizer.git
cd kelven-optimizer

# Execute o programa
kelven-optimizer2.0.py"
```

---

## 🎯 Categorias de Tweaks

### 🔴 CPU (10 tweaks)
- Desativa Core Parking
- Otimiza prioridades do processador
- Desativa throttling e estados de economia
- Maximiza performance do CPU

### 🟢 GPU (12 tweaks)
- Hardware acceleration
- Desativa power saving
- Otimiza TDR e preemption
- Shader cache e MSI mode

### 🟢 NVIDIA (10 tweaks)
- Low latency mode
- Max performance
- Shader cache otimizado
- Threaded optimization

### 🔴 AMD (10 tweaks)
- Radeon Anti-Lag
- Radeon Boost
- Enhanced Sync
- FreeSync optimization

### 🟡 Memory (12 tweaks)
- Desativa paging executive
- Large system cache
- Otimiza pool de memória
- Desativa compression

### 🟣 Network (15 tweaks)
- TCP/IP optimization
- Desativa throttling
- RSS e Chimney offload
- QoS packet scheduler

### 🟠 Gaming (15 tweaks)
- Game mode ativado
- Prioridades otimizadas
- Desativa mouse acceleration
- Gaming audio priority

### 🔵 System (35 tweaks)
- Desativa telemetria
- Desativa Windows Defender
- Desativa Firewall
- Remove 30+ serviços desnecessários

### 🔴 Debloat (23 tweaks)
- Remove OneDrive
- Desativa Xbox services
- Remove bloatware
- Otimiza RAM ao máximo
- Mantém Windows Store funcional

### 🩷 Kernel (15 tweaks)
- Timer resolution otimizado
- Desativa kernel paging
- DPC watchdog optimization
- Desativa Spectre/Meltdown
- Boot optimization

---

## 🚀 Funcionalidades

### 🏠 Dashboard
- Monitoramento em tempo real de CPU, RAM e Disco
- Informações de hardware detectado
- Ações rápidas de otimização
- Logs do sistema

### ⚡ Smart Tweaks
- Interface com abas por categoria
- Aplicação individual ou em massa
- Seleção automática de GPU (NVIDIA/AMD/Intel)
- Barra de progresso animada

### 🎮 Modo Gaming
- Otimizações específicas para jogos
- Reduz latência de rede
- Maximiza prioridade de GPU
- Desativa processos desnecessários

### 🧹 Limpeza Pro
- 3 modos: Rápida, Completa e Profunda
- Libera RAM sem fechar aplicativos
- Compactação do Windows integrada
- Limpeza de arquivos temporários

### 🗜️ Compactação do Windows
- Compacta sistema operacional
- Limpa WinSxS
- Economiza vários GB de espaço
- Barra de progresso em tempo real

### 🚀 Gerenciador de Inicialização
- Lista apps que iniciam com Windows
- Habilita/desabilita facilmente
- Reduz tempo de boot

### 🔄 Sistema de Atualizações
- Verifica atualizações no GitHub
- Changelog integrado
- Download direto da release

---

## ⚙️ Requisitos do Sistema

- **OS**: Windows 10 ou Windows 11
- **RAM**: 4GB mínimo (8GB recomendado)
- **Espaço**: 100MB livres
- **Permissões**: Administrador (recomendado)

---

## 🛠️ Compilar do Código Fonte

### Usando o script automático:
```bash
build.bat
```

### Manualmente:
```bash
pip install pyinstaller
pyinstaller --onefile --windowed --name "kelven-optimizer2.0" --icon "icon.ico" --add-data "icon.ico;." "kelven-optimizer2.0.py

O executável será gerado em: `dist\kelven-optimizer2.0.exe`

---

## ⚠️ Avisos Importantes

- ⚠️ **Crie um ponto de restauração** antes de aplicar tweaks
- ⚠️ **Execute como Administrador** para funcionalidade completa
- ⚠️ Alguns tweaks desativam recursos de segurança (Defender, Firewall)
- ⚠️ Tweaks de Kernel são avançados e podem afetar estabilidade
- ⚠️ Use por sua conta e risco

---

## 📸 Screenshots

### Dashboard
![Dashboard](https://via.placeholder.com/800x450/0F0F0F/00F0FF?text=Dashboard)

### Smart Tweaks
![Tweaks](https://via.placeholder.com/800x450/0F0F0F/FF006E?text=Smart+Tweaks)

### Gaming Mode
![Gaming](https://via.placeholder.com/800x450/0F0F0F/00FF41?text=Gaming+Mode)

---

## 🤝 Contribuindo

Contribuições são bem-vindas! Sinta-se à vontade para:

1. Fazer fork do projeto
2. Criar uma branch para sua feature (`git checkout -b feature/NovaFeature`)
3. Commit suas mudanças (`git commit -m 'Adiciona nova feature'`)
4. Push para a branch (`git push origin feature/NovaFeature`)
5. Abrir um Pull Request

---

## 📝 Changelog

### v2.0 (2024)
- ✨ Interface completamente redesenhada
- 🚀 157 tweaks (anteriormente 84)
- 🎨 Animações e transições suaves
- 🗜️ Sistema de compactação do Windows
- 🔍 Detecção automática de GPU
- 📊 Barra de progresso para aplicação de tweaks
- 🩷 Nova categoria: Kernel Tweaks (15 tweaks)
- 🔴 Categoria Debloat expandida (23 tweaks)
- 🔵 System tweaks expandido (35 tweaks)
- 👋 Tela de boas-vindas e despedida
- 🔄 Sistema de atualizações integrado

---

## 🔗 Links

- **GitHub**: [github.com/kelvenapk](https://github.com/kelvenapk)
- **Discord**: [discord.gg/gNPhS3m3QF](https://discord.gg/gNPhS3m3QF)
- **Releases**: [Baixar última versão](https://github.com/kelvenapk/kelven-optimizer/releases/latest)

---

## 📄 Licença

Este projeto está sob a licença MIT. Veja o arquivo [LICENSE](LICENSE) para mais detalhes.

---

## 💖 Apoie o Projeto

Se este projeto te ajudou, considere:

- ⭐ Dar uma estrela no GitHub
- 🐛 Reportar bugs e sugerir melhorias
- 💬 Entrar no Discord e compartilhar sua experiência
- 📢 Compartilhar com amigos

---

<div align="center">

**Desenvolvido com 💙 por [kelvenapk](https://github.com/kelvenapk)**

⚡ Kelven Optimizer PRO v2.0 ⚡

</div>
