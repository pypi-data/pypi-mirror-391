import os
import sys
import re 
from pathlib import Path
from unicodedata import normalize 
import tkinter as tk
from tkinter import filedialog
import pygetwindow as gw
import ctypes    

class misc: # Classe de miscelâneas
    """
#### Classe **misc**

Classe que reune pequenas funções uteis para agilizar tarefas comuns.

Sintaxe e exemplos de uso. Parametros omissos assume-se os valores padrão indicados abaixo:

    - `Arquivo = seleciona_arquivo(DirBase, TiposArquivo=[('Todos os arquivos', '*.*')], Titulo='Selecionar arquivo')`
    - `Diretório = seleciona_dir(DirBase=Path(r'./'), Titulo='Selecionar diretório'):`
    - `NomeLimpo = normaliza('String # SEM Noção!') # string_sem_nocao`
    - `cmd_window = get_cmd_window()`
    - `maximize_console()`    
    - `print(cor('Texto branco ', 'BC') + cor('Texto preto ', 'PT'))`
    """
    def __init__(self):
        pass
        #
        #    
    def seleciona_arquivo(DirBase, TiposArquivo=[('Todos os arquivos', '*.*')], Titulo='Selecionar arquivo'): # Picker para selecionar arquivo
        root = tk.Tk()
        root.withdraw()  # Esconde a janela principal do Tkinter
        Arquivo = filedialog.askopenfilename(initialdir=DirBase, filetypes=TiposArquivo, title=Titulo)
        Arquivo = Path(Arquivo)
        root.destroy()
        return Arquivo
        #
        #
    def seleciona_dir(DirBase=Path(r'./'), Titulo='Selecionar diretório'): # Picker para selecionar diretório
        root = tk.Tk() # objeto picker  (Tkinter)para selecionar arquivos e diretórios
        root.withdraw()  # Esconde a janela principal do Tkinter
        Diretorio = filedialog.askdirectory(initialdir=DirBase, title=Titulo)
        Diretorio = Path(Diretorio)
        root.destroy()
        return Diretorio
        #
        #
    def normaliza(Original, Case='lower', KeepSpaces=False, KeepDelim=False, KeepDirTree=False): # Limpa e padroniza nomes
        
        Lixo = r'?%§ªº°`´^~*|"<>!@#$%¨&*_+=-"\''
        Lixo = Lixo + r' ' if not KeepSpaces else Lixo
        Lixo = Lixo + r'(){}[]' if not KeepDelim else Lixo
        Lixo = Lixo + r':/\\' if not KeepDirTree else Lixo

        if Case and not Case.lower() in ['upper', 'lower', 'keep']:
            raise ValueError('Parametro opcioanl "Case" deve ser ["upper", "lower", "keep"]. Se omisso (None), string será convertida para caixa baixa.')
        
        Normalizar = (''.join(c for c in normalize('NFKD', Original) if c.encode('ascii', 'ignore').decode('ascii'))) if Case.lower() == 'keep' else normalize('NFKD', Original).encode('ASCII', 'ignore').decode('ASCII') 
        RemoverLixo = [c if c not in Lixo else '_' for c in Normalizar]    
        Limpo = "".join(RemoverLixo)
        Limpo = re.sub(r'\.(?=.*\.)', '_', Limpo) # troca todos os pontos por underline
        Limpo = re.sub(r'_+', '_', Limpo)  # limpa as reptições do underline
        Limpo = Limpo.lower() if not Case or Case.lower() == 'lower' else Limpo.upper() if Case.lower() == 'upper' else Limpo
        return Limpo
        #
        #
    def get_cmd_window(): # Captura a referencia da janela atual para retornar o foco à ela depois de chamar os pickers
        pid = os.getpid()
        windows = gw.getWindowsWithTitle("")
        for window in windows:
            if window.title and window.visible and window.topleft:
                return window
        return None
        #
        #
    def maximize_console(): # Ajustar o buffer de console
        # os.system('mode con: cols=500 lines=100')
        # Obter o handle da janela do console
        kernel32 = ctypes.WinDLL('kernel32')
        user32 = ctypes.WinDLL('user32')
        hWnd = kernel32.GetConsoleWindow()
        if hWnd:
            # Definir as dimensões da tela
            user32.ShowWindow(hWnd, 3)  # 3 = SW_MAXIMIZE  
        #
        #
    def encontra_projeto_raiz(caminho_partida):
        """Sobe a árvore procurando por .venv OU pyproject.toml como raiz do projeto"""
        dir_atual = os.path.abspath(caminho_partida)
        while True:
            if (
                os.path.isdir(os.path.join(dir_atual, '.venv')) or
                os.path.isfile(os.path.join(dir_atual, 'pyproject.toml'))
            ):
                return dir_atual
            novo_dir = os.path.dirname(dir_atual)
            if novo_dir == dir_atual:
                return None  # Chegou na raiz do sistema
            dir_atual = novo_dir
        #
        #
    def encontra_python_venv(raiz_projeto):
        """Retorna o caminho do python da .venv se existir, senão None"""
        if os.name == 'nt':
            # Windows
            python_venv = os.path.join(raiz_projeto, '.venv', 'Scripts', 'python.exe')
        else:
            # Linux/Mac
            python_venv = os.path.join(raiz_projeto, '.venv', 'bin', 'python')
        return python_venv if os.path.isfile(python_venv) else None 
        #
        #
    def nome_modulo(script_path, raiz_projeto):
        """
        Dado o caminho absoluto do script (ex: C:/.../src/cnab/main.py)
        e da raiz do projeto (ex: C:/...),
        retorna o caminho do módulo python no formato pacote.subpacote.modulo
        Exemplo: src.cnab.main
        """
        relpath = os.path.relpath(script_path, raiz_projeto)
        if relpath.endswith('.py'):
            relpath = relpath[:-3]  # remove .py
        partes = []
        for parte in relpath.replace("\\", "/").split("/"):
            if parte not in ("", "__init__"):
                partes.append(parte)
        return ".".join(partes)
        #
        #
    @classmethod
    def cor(cls, text, color=None, style=None):
        """
            Aplica cor e estilo ao texto fornecido.

            Exemplo de uso:

            from lbxtoolkit import misc

            os.system('') ## necessário para ativar o suporte a caracteres ANSI

            print(cor('Texto branco ', 'BC') + cor('Texto preto ', 'PT'))
            print(cor('Texto Azul Fundo Amarelo', 'AZ', 'bAM') 
            print(cor('Texto branco negrito', 'BC', 'NG'))
            print(cor('Texto cinza claro', 'CL'))
            print(cor('Texto cinza escuro', 'CE'))
            print(cor('FUNDO cinza claro', style='bCL'))
            print(cor('FUNDO cinza escuro', style='bCE'))            
        """
        COLORS = {
            'PT': '\033[30m',  # Preto
            'CE': '\033[90m',  # Cinza (Cinza Escuro)
            'CL': '\033[37m',  # Cinza Claro
            'VM': '\033[91m',  # Vermelho
            'VD': '\033[92m',  # Verde
            'AM': '\033[93m',  # Amarelo
            'AZ': '\033[94m',  # Azul
            'MG': '\033[95m',  # Magenta
            'CY': '\033[96m',  # Ciano
            'BC': '\033[97m',  # Branco
            'RS': '\033[0m'    # Reset
        }

        STYLES = {
            'NG': '\033[1m',   # Negrito
            'SB': '\033[4m',   # Sublinhado
            'RS': '\033[0m',   # Reset
            # Cores de fundo
            'bPT': '\033[40m',  # Fundo Preto
            'bCE': '\033[100m', # Fundo Cinza Escuro
            'bCL': '\033[47m',  # Fundo Cinza Claro
            'bVM': '\033[41m',  # Fundo Vermelho
            'bVD': '\033[42m',  # Fundo Verde
            'bAM': '\033[43m',  # Fundo Amarelo
            'bAZ': '\033[44m',  # Fundo Azul
            'bMG': '\033[45m',  # Fundo Magenta
            'bCY': '\033[46m',  # Fundo Ciano
            'bBC': '\033[107m'  # Fundo Branco
    }        
        color_code = COLORS.get(color, '')
        style_code = STYLES.get(style, '')
        RS_code = COLORS['RS']
        return f"{color_code}{style_code}{text}{RS_code}"