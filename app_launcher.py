# ============================================================
# BLOCO 1 — IMPORTAÇÃO DAS BIBLIOTECAS
# ============================================================
#
# Este bloco importa todas as dependências necessárias
# para o funcionamento da aplicação desktop.
#
# Bibliotecas utilizadas:
#
# - webbrowser:
#   Responsável por abrir URLs no navegador padrão do sistema.
#
# - tkinter:
#   Biblioteca nativa do Python utilizada para criação
#   de interfaces gráficas desktop.
#
# - messagebox:
#   Módulo do tkinter utilizado para exibir caixas
#   de diálogo informativas e de erro.
#
# - sys:
#   Biblioteca padrão para interação com o sistema operacional.
#   Neste código específico ela ainda não está sendo utilizada,
#   mas pode ter sido importada para futuras expansões.
#
# Observação:
# Importações não utilizadas podem ser removidas futuramente
# para manter o código mais limpo.
# ============================================================

import webbrowser
import tkinter as tk
from tkinter import messagebox
import sys


# ============================================================
# BLOCO 2 — CONFIGURAÇÕES GLOBAIS DA APLICAÇÃO
# ============================================================
#
# Este bloco centraliza configurações importantes
# utilizadas em toda a aplicação.
#
# Benefícios dessa abordagem:
#
# - Facilita manutenção futura
# - Evita repetição de valores fixos (hardcoded)
# - Permite alterar nome, URL ou ícone em apenas um local
#
# APP_NAME:
# Nome exibido na janela e nas mensagens.
#
# APP_URL:
# URL da aplicação hospedada online.
# IMPORTANTE:
# O link deve ser substituído pelo endereço real
# do Streamlit Cloud antes da distribuição.
#
# APP_ICON:
# Emoji utilizado visualmente no título da interface.
# ============================================================

APP_NAME = "ConsultaNF - Make Distribuidora"

# URL provisória da aplicação online
# Deve ser substituída pelo link final publicado.
APP_URL = "https://seu-nome-streamlit.streamlit.app"

APP_ICON = "📦"


# ============================================================
# BLOCO 3 — FUNÇÃO RESPONSÁVEL POR ABRIR A APLICAÇÃO
# ============================================================
#
# Objetivo:
# Abrir a aplicação web no navegador padrão do usuário.
#
# Fluxo de execução:
#
# 1. Exibe uma mensagem informando que a aplicação
#    será aberta.
#
# 2. Abre a URL utilizando o navegador padrão do sistema.
#
# 3. Fecha a interface Tkinter após abrir o navegador.
#
# Tratamento de erro:
#
# Caso ocorra algum problema durante a abertura
# da URL (por exemplo:
# - navegador indisponível
# - URL inválida
# - erro do sistema operacional)
#
# uma mensagem de erro será exibida ao usuário.
#
# Observação importante:
# janela.quit() encerra o loop principal da interface.
# ============================================================

def abrir_aplicacao():
    """Abre a aplicação online no navegador padrão."""

    try:

        # Exibe mensagem informativa antes da abertura
        messagebox.showinfo(
            APP_NAME,
            f"Abrindo a aplicação online...\n\n{APP_URL}"
        )

        # Abre a URL no navegador padrão do sistema operacional
        webbrowser.open(APP_URL)

        # Encerra a aplicação desktop após abrir o navegador
        janela.quit()

    except Exception as e:

        # Exibe mensagem de erro detalhada
        messagebox.showerror(
            "Erro",
            f"Não foi possível abrir a aplicação:\n{str(e)}"
        )


# ============================================================
# BLOCO 4 — FUNÇÃO RESPONSÁVEL POR COPIAR O LINK
# ============================================================
#
# Objetivo:
# Permitir que o usuário copie rapidamente
# o endereço da aplicação para a área de transferência.
#
# Fluxo:
#
# 1. Limpa qualquer conteúdo atual da área de transferência.
#
# 2. Adiciona a URL da aplicação.
#
# 3. Exibe confirmação visual para o usuário.
#
# Possível melhoria futura:
#
# Poderia existir um tratamento de erro caso
# o sistema operacional bloqueie acesso
# à área de transferência.
# ============================================================

def copiar_link():
    """Copia o link da aplicação para a área de transferência."""

    # Remove conteúdo anterior da área de transferência
    janela.clipboard_clear()

    # Adiciona a URL da aplicação
    janela.clipboard_append(APP_URL)

    # Feedback visual para o usuário
    messagebox.showinfo(
        APP_NAME,
        "Link copiado para a área de transferência!"
    )


# ============================================================
# BLOCO 5 — CRIAÇÃO DA JANELA PRINCIPAL
# ============================================================
#
# Este bloco inicializa a interface gráfica principal.
#
# Configurações aplicadas:
#
# - título da janela
# - tamanho fixo
# - bloqueio de redimensionamento
#
# geometry("400x250"):
# Define largura e altura da janela.
#
# resizable(False, False):
# Impede que o usuário redimensione manualmente.
#
# Isso garante consistência visual da interface.
# ============================================================

janela = tk.Tk()

# Define o título exibido na barra superior
janela.title(APP_NAME)

# Define tamanho da janela
janela.geometry("400x250")

# Impede redimensionamento horizontal e vertical
janela.resizable(False, False)


# ============================================================
# BLOCO 6 — CENTRALIZAÇÃO DA JANELA NA TELA
# ============================================================
#
# Objetivo:
# Fazer a interface abrir centralizada
# na tela do usuário.
#
# Processo:
#
# 1. Atualiza cálculos internos da janela.
#
# 2. Obtém resolução atual da tela.
#
# 3. Calcula coordenadas X e Y centrais.
#
# 4. Reposiciona a janela.
#
# Fórmula utilizada:
#
# posição_central =
# (tamanho_da_tela / 2) - (tamanho_da_janela / 2)
#
# Isso melhora experiência visual e usabilidade.
# ============================================================

# Atualiza informações internas da interface
janela.update_idletasks()

# Calcula posição horizontal central
x = (
    (janela.winfo_screenwidth() // 2)
    - (janela.winfo_width() // 2)
)

# Calcula posição vertical central
y = (
    (janela.winfo_screenheight() // 2)
    - (janela.winfo_height() // 2)
)

# Aplica nova posição da janela
janela.geometry(f"+{x}+{y}")


# ============================================================
# BLOCO 7 — CRIAÇÃO DO TÍTULO PRINCIPAL
# ============================================================
#
# Label responsável por exibir:
#
# - ícone da aplicação
# - nome do sistema
#
# Configurações visuais:
#
# - fonte Arial
# - tamanho 16
# - negrito
#
# pack(pady=20):
# Adiciona espaçamento vertical externo.
# ============================================================

titulo = tk.Label(
    janela,
    text=f"{APP_ICON} {APP_NAME}",
    font=("Arial", 16, "bold")
)

titulo.pack(pady=20)


# ============================================================
# BLOCO 8 — DESCRIÇÃO DO SISTEMA
# ============================================================
#
# Exibe uma pequena descrição institucional
# explicando o objetivo da aplicação.
#
# justify=tk.CENTER:
# Centraliza múltiplas linhas de texto.
#
# Esse bloco melhora entendimento inicial do usuário.
# ============================================================

descricao = tk.Label(
    janela,
    text="Sistema de Consulta e Extração de NF\nMake Distribuidora",
    font=("Arial", 10),
    justify=tk.CENTER
)

descricao.pack(pady=10)


# ============================================================
# BLOCO 9 — EXIBIÇÃO DO LINK DA APLICAÇÃO
# ============================================================
#
# Este Label exibe visualmente a URL.
#
# Características:
#
# - Texto azul simulando hyperlink
# - Cursor "hand2" imita ponteiro de link web
#
# Observação:
#
# Apesar da aparência de hyperlink,
# este Label ainda não possui evento de clique.
#
# Possível melhoria futura:
#
# Implementar bind("<Button-1>", ...)
# para permitir clique direto no link.
# ============================================================

link_label = tk.Label(
    janela,
    text=APP_URL,
    font=("Arial", 9),
    fg="blue",
    cursor="hand2"
)

link_label.pack(pady=10)


# ============================================================
# BLOCO 10 — BOTÃO PRINCIPAL DE ACESSO
# ============================================================
#
# Botão responsável por abrir a aplicação online.
#
# command=abrir_aplicacao:
# Define qual função será executada ao clicar.
#
# Configurações visuais:
#
# - fundo azul
# - texto branco
# - fonte destacada
# - padding interno
#
# width=25:
# Define largura padronizada do botão.
# ============================================================

botao_abrir = tk.Button(
    janela,
    text="🌐 Abrir Aplicação",
    command=abrir_aplicacao,
    bg="#1f77b4",
    fg="white",
    font=("Arial", 12, "bold"),
    padx=20,
    pady=10,
    width=25
)

botao_abrir.pack(pady=15)


# ============================================================
# BLOCO 11 — BOTÃO DE CÓPIA DO LINK
# ============================================================
#
# Permite copiar rapidamente o endereço
# da aplicação para compartilhamento.
#
# Esse recurso melhora acessibilidade
# e experiência do usuário.
# ============================================================

botao_copiar = tk.Button(
    janela,
    text="📋 Copiar Link",
    command=copiar_link,
    bg="#444",
    fg="white",
    font=("Arial", 10),
    padx=15,
    pady=5,
    width=25
)

botao_copiar.pack(pady=5)


# ============================================================
# BLOCO 12 — RODAPÉ INFORMATIVO
# ============================================================
#
# Exibe uma informação complementar
# no final da interface.
#
# Objetivo:
# Informar disponibilidade contínua do sistema.
#
# Cor cinza utilizada para reduzir destaque visual
# e manter hierarquia da interface.
# ============================================================

rodape = tk.Label(
    janela,
    text="Acesso 24h disponível",
    font=("Arial", 8),
    fg="gray"
)

rodape.pack(pady=10)


# ============================================================
# BLOCO 13 — LOOP PRINCIPAL DA INTERFACE
# ============================================================
#
# mainloop() inicia o loop de eventos do Tkinter.
#
# Sem essa instrução:
# - a janela abriria e fecharia imediatamente.
#
# O loop permanece:
#
# - aguardando cliques
# - processando eventos
# - atualizando interface
# - respondendo interações do usuário
#
# Este é o núcleo operacional da aplicação gráfica.
# ============================================================

janela.mainloop()