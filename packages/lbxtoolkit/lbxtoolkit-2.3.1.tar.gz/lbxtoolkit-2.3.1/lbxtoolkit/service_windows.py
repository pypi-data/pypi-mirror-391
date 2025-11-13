from .config_manager import ConfigManager
from .lbx_logger import lbx_logger, SafeLogger
import os
import sys
from time import sleep
from pathlib import Path
import subprocess
import platform
import socket
import servicemanager
import win32serviceutil
import win32service
import win32event

class ServicoWindows(win32serviceutil.ServiceFramework): # Gerencia a execução/instalação como serviço do windows
    """
#### Classe **ServicoWindows**

Gerencia a instalação e execução de um daemon como um serviço do windows. Também assume o controle dos argumentos recebidos via linha de comando.

- `SvcInstall`: Cria um serviço do windows com base neste script
- `SvcRemove`: Remove o serviço do windows configurado à partir de `SvcInstall`
- `SvcStop`: Para/Interrompe a execução do serviço do windows criado por este script (método herdado da classe pai _win32serviceutil.ServiceFramework_ invocado automaticamente pela chamada do service manager do windows)
- `SvcDoRun`: Inicializa a execução do serviço do windows criado por este script (método herdado da classe pai _win32serviceutil.ServiceFramework_ invocado autoamticamente pela chamada do service manager do windwos)

A classe base possui ainda algumas dependÊncias que precisam ser inicializadas fora do contexto da classe configuradora/local. 
Para isso, use classe ConfigManager.initialize(), disponível também no módulo `lbxtoolkit`.
O objetos mandatórios a serem inicilizados pelo **ConfigManager** são:
-    **log** = Objeto instanciado da classe lbx_logger, para manipular as entradas de log
-    **daemon** = Objeto resultante do instanciamento da própria própria classe configuradora (deve ser inicializado após o instanciamento do objeto daemon, usando `ConfigManager.set()`)
-    **config** = Dicionário contento os parametros (name, display_name e description) para instalar o serviço do windows
-    **servicepath** = Objeto do Path com o caminho deste script
-    **argparse_cfg** = Dicionário contendo os parametros de configuração (descrition, usage, add_help e formatter_classe) do módulo argparse (manipulado dos parametros de linha de comando)
-    **argparse_opt** = Lista de dicionários com a configuração do argumentos de entrada aceitos (short, long, action, help)
-    **ambiente** = Definie o ambiente de excução: Linux, Windows [console] ou Serviço [Windows]  
-    **raiz_projeto** = A raiz do projeto para fins de execução por módulo (python -m) e não diretamente pelo script. Utilize `misc.encrontra_projeto_raiz` no módulo principal para obter essa informação 
-    **modulo** = O nome do módulo quando o projeto for extrutura para execução por módulo. Utilize `misc.nome_modulo` no módulo principal para obter essa informação

    """
    _svc_name_ = None
    _svc_display_name_ = None
    _svc_description_ = None   
    def __init__(self, args):
        self.log = ConfigManager.get('log')
        self.daemon = ConfigManager.get('daemon')
        self.config = ConfigManager.get('config')  
        self.raiz_projeto = ConfigManager.get('raiz_projeto')   
        self.modulo = ConfigManager.get('modulo')                 

        if self.log is None or (not isinstance(self.log, lbx_logger) and not isinstance(self.log, SafeLogger)):
            raise ValueError(f'Argumento "log" é mandatório e deve ser uma instância de "lbxtoolkit.lbx_logger" ou "lbxtoolkit.SaffeLogger"')
        elif self.daemon is None or not hasattr(self.daemon, 'run') or not hasattr(self.daemon, 'stop'):
            raise ValueError(f'Argumento "daemon" é mandatório e deve possuir os métodos run() e stop()')        
        elif self.config is None or not 'name' in self.config or not 'display_name' in self.config or not 'description' in self.config:
            raise ValueError(f'Argumento "config" é mandatório e deve ser um dicionário contendo as chaves/valores para "name", "display_name" e "description"')
        elif [chave for chave in self.config if self.config[chave] is None]:
            raise ValueError(f'Argumento "config" ({self.config}) possui as seguintes chaves com valores inválidos [None]: {[chave for chave in self.config if self.config[chave] is None]:}')
        elif self.raiz_projeto is None:
            raise ValueError(f'Argumento "raiz_projeto" é mandatório e deve ser obtido usando "misc.encrontra_projeto_raiz" no módulo principal') 
        elif self.modulo is None:
            raise ValueError(f'Argumento "modulo" é mandatório e deve ser obtido usando "misc.nome_modulo" no módulo principal')         

        self._svc_name_ = self.config['name']
        self._svc_display_name_ = self.config['display_name']
        self._svc_description_ = self.config['description']
        #super().__init__(args)

        win32serviceutil.ServiceFramework.__init__(self, args)
        self.hWaitStop = win32event.CreateEvent(None, 0, 0, None)
        socket.setdefaulttimeout(5)
        self.stop_requested = False      
        self.isAlive = True     
        #
        #   
    @staticmethod 
    def SvcInstall(): # Instala o script como um serviço do windows
        """Cria um serviço do windows com base no script"""
        ## use @staticmethod quando precisar referenciar o método sem instanciar a classe e não precisar de acesso a instâncias ou à própria classe
        ## se precisar acessar métodos ou atributos da classe e não da instância, use @classmethod, mas isso implcia em passar (cls) e não (self) na definição método
        try:

            log = ConfigManager.get('log')
            daemon = ConfigManager.get('daemon')   
            config = ConfigManager.get('config')  
            raiz_projeto = ConfigManager.get('raiz_projeto')   
            modulo = ConfigManager.get('modulo')       
            
            if log is None or (not isinstance(log, lbx_logger) and not isinstance(log, SafeLogger)):
                raise ValueError(f'Argumento "log" é mandatório e deve ser uma instância de "lbxtoolkit.lbx_logger" ou "lbxtoolkit.SaffeLogger"')
            elif daemon is None or not hasattr(daemon, 'run') or not hasattr(daemon, 'stop'):
                raise ValueError(f'Argumento "daemon" é mandatório e deve possuir os métodos run() e stop()')  
            elif config is None or not 'name' in config or not 'display_name' in config or not 'description' in config:
                raise ValueError(f'Argumento "config" é mandatório e deve ser um dicionário contendo as chaves/valores para "name", "display_name" e "description"')
            elif [chave for chave in config if config[chave] is None]:
                raise ValueError(f'Argumento "config" ({config}) possui as seguintes chaves com valores inválidos [None]: {[chave for chave in config if config[chave] is None]:}')

            _svc_name_ = config['name'] 
            _svc_display_name_ = config['display_name']
            _svc_description_ = config['description']

            ## para legado. suportar tanto a criação de execução direta do .py (originalmente) como por módulo
            ## a lógica é que raiz_projeto e modulo só sejam definidos se o projeto foi estrutura para execução por módulo/entrypoint (pythom -m ou poetry run). 
            #  neste caso, é esperado que service_path e python_path sejam nulos
            ## por outro lado, se a execução for diretamente pelo script (python script.py), é esperado que raiz_projeto e modulo sejam nulos. se service_path e python_path forem nulos também, serão definidos arbitrariamente
            if raiz_projeto and modulo: ## execução por módulo (novo)
                service_path = None
                python_path = None
                wrapper = Path(raiz_projeto, f'wrapper_servico_{modulo}.bat') ## tem que ser igual a SvcRemove. Mudou lá, muda aqui.
                wrapper_content = f"""
@echo off
REM ==================================================================================================================
REM !!!!NÃO TOQUE NESSE ARQUIVO. NÃO O APAQUE NEM O MODIFIQUE.!!!!
REM O serviço do windows [{config['display_name']}] que roda nesta máquina depende do conteúdo deste arquivo de lotes.
REM ==================================================================================================================
set PYTHONPATH=%~dp0
"%~dp0.venv\\Scripts\\python.exe" -m {modulo} %*
            """              
                with open(wrapper, "w", encoding="utf-8") as file:
                    file.write(wrapper_content)
                service_cmd = f'{wrapper}'

            else: ## execução direta do script (legado)
                service_path = ConfigManager.get('service_path') if ConfigManager.get('service_path') else os.path.abspath(__file__)
                python_path = ConfigManager.get('python_path') if ConfigManager.get('python_path') else os.path.join(os.getenv('VIRTUAL_ENV'), 'Scripts', 'python.exe') if os.getenv('VIRTUAL_ENV')  else sys.executable
                service_cmd = f'{python_path} {service_path}'


            IP = socket.gethostbyname(socket.gethostname())
            Host = socket.gethostname()
            OS = platform.system()
            Usuario = os.getlogin() if OS == 'Windows' else os.path.expanduser('~').split(r'/')[1]
            # Delete the service
            query = subprocess.run(["sc", "query", _svc_name_], capture_output=True, text=True)
            if _svc_name_ in query.stdout:
                if 'RUNNING' in query.stdout:
                    log.add(f'Parando serviço  [{_svc_display_name_} ({_svc_name_})] em {IP}/{Host}({Usuario})...\n')
                    try:
                        stop = subprocess.run(["sc", "stop", _svc_name_], capture_output=True)
                        saida = stop.stdout.decode('cp850').strip()
                        sleep(5)
                        log.info(f': {saida}')
                    except Exception as Err:
                        log.erro(f'Erro ao parar serviço: {saida}')
                delete = subprocess.run(["sc", "delete", _svc_name_], capture_output=True)
                saida = delete.stdout.decode('cp850').strip()
                if delete:
                    log.info(f'Excluindo serviço pre-existente [{_svc_display_name_} ({_svc_name_})] em {IP}/{Host}({Usuario}): {saida}')
            # Create the service
            svc = [
                    'sc', 
                    'create', 
                    _svc_name_,
                    'binPath=',
                    f'{service_cmd}',
                    'DisplayName=', 
                    _svc_display_name_,
                    'start=delayed-auto',
                ]
            install = subprocess.run(svc, capture_output=True)    
            saida = install.stdout.decode('cp850').strip()
            log.info(f'Criando novo serviço [{_svc_display_name_} ({_svc_name_})] em {IP}/{Host}({Usuario}): {saida}')
            # Set the service description
            descricao = subprocess.run(
                                        [
                                            'sc', 
                                            'description', 
                                            _svc_name_, 
                                            _svc_description_,
                                        ]
                                        , capture_output=True)    
            saida = descricao.stdout.decode('cp850').strip()
            log.info(f'Ajustando descrição do novo serviço [{_svc_display_name_} ({_svc_name_})]: {saida}')
        except Exception as Err:
            log.erro(f'Falha ao tentar criar o serviço [{_svc_display_name_} ({_svc_name_})]')     
            raise   
        #
        #
    @staticmethod 
    def SvcRemove(): # Remove o serviço do windows
        """Remove o serviço do windows configurado à partir de `SvcInstall`"""
        ## use @staticmethod quando precisar referenciar o método sem instanciar a classe e não precisar de acesso a instâncias ou à própria classe
        ## se precisar acessar métodos ou atributos da classe e não da instância, use @classmethod, mas isso implcia em passar (cls) e não (self) na definição método
        try:

            log = ConfigManager.get('log')
            daemon = ConfigManager.get('daemon')   
            config = ConfigManager.get('config')   
            raiz_projeto = ConfigManager.get('raiz_projeto')   
            modulo = ConfigManager.get('modulo')                                    

            if log is None or (not isinstance(log, lbx_logger) and not isinstance(log, SafeLogger)):
                raise ValueError(f'Argumento "log" é mandatório e deve ser uma instância de "lbxtoolkit.lbx_logger" ou "lbxtoolkit.SaffeLogger"')
            elif daemon is None or not hasattr(daemon, 'run') or not hasattr(daemon, 'stop'):
                raise ValueError(f'Argumento "daemon" é mandatório e deve possuir os métodos run() e stop()')  
            elif config is None or not 'name' in config or not 'display_name' in config or not 'description' in config:
                raise ValueError(f'Argumento "config" é mandatório e deve ser um dicionário contendo as chaves/valores para "name", "display_name" e "description"')
            elif [chave for chave in config if config[chave] is None]:
                raise ValueError(f'Argumento "config" ({config}) possui as seguintes chaves com valores inválidos [None]: {[chave for chave in config if config[chave] is None]:}')

            _svc_name_ = config['name'] 
            _svc_display_name_ = config['display_name']

            IP = socket.gethostbyname(socket.gethostname())
            Host = socket.gethostname()
            OS = platform.system()
            Usuario = os.getlogin() if OS == 'Windows' else os.path.expanduser('~').split(r'/')[1]
            # Delete the service
            query = subprocess.run(["sc", "query", _svc_name_], capture_output=True, text=True)
            if _svc_name_ in query.stdout:
                if 'RUNNING' in query.stdout:
                    log.add(f'Parando serviço  [{_svc_display_name_} ({_svc_name_})] em {IP}/{Host}({Usuario})...\n')
                    try:
                        stop = subprocess.run(["sc", "stop", _svc_name_], capture_output=True)
                        saida = stop.stdout.decode('cp850').strip()
                        sleep(5)
                        log.info(f': {saida}')
                    except Exception as Err:
                        log.erro(f'Erro ao parar serviço: {saida}')
                delete = subprocess.run(["sc", "delete", _svc_name_], capture_output=True)
                saida = delete.stdout.decode('cp850').strip()
                if delete:
                    log.info(f'Excluindo serviço pre-existente [{_svc_display_name_} ({_svc_name_})] em {IP}/{Host}({Usuario}): {saida}')
                    if raiz_projeto and modulo: ## execução por módulo (novo)
                        wrapper = Path(raiz_projeto, f'wrapper_servico_{modulo}.bat') ## tem que ser igual a SvcInstall. Mudou lá, muda aqui.
                        if wrapper.exists():
                            wrapper.unlink()                    
              
        except Exception as Err:
            log.erro(f'Falha ao tentar excluir o serviço [{_svc_display_name_} ({_svc_name_})]')     
            raise 
        #
        #           
    def SvcStop(self): # Para a execução do serviço
        """Para/Interrompe a execução do serviço do windows criado por este script"""
        self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
        win32event.SetEvent(self.hWaitStop)
        self.stop_requested = True
        self.isAlive = False
        self.daemon.stop('STOP')
        self.ReportServiceStatus(win32service.SERVICE_STOPPED)
        #
        #
    def SvcDoRun(self): # Inicia o serviço
        """Inicializa a execução do serviço do windows criado por este script"""
        #self.ReportServiceStatus(win32service.SERVICE_START_PENDING)     
        self.ReportServiceStatus(win32service.SERVICE_RUNNING)
        self.daemon.mode='[SERVIÇO (windows)]' 
        self.RunAsDaemon()              
        servicemanager.LogMsg(servicemanager.EVENTLOG_INFORMATION_TYPE, 
                              servicemanager.PYS_SERVICE_STARTED, (self._svc_name_, ''))  
        

    @staticmethod
    def SvcStatus(ServiceName=None):  # Verifica o status de um serviço específico ou do próprio serviço
        """
        Retorna o status do serviço do Windows.
        Se um nome for passado como parâmetro, verifica o status do serviço informado.
        Caso contrário, retorna o status do próprio serviço.
        """
        try:
            # Recuperar nome do serviço, se não for passado
            if not ServiceName:
                config = ConfigManager.get('config')
                if not config or 'name' not in config:
                    raise ValueError("Configuração do serviço inválida. O nome do serviço não pode ser determinado.")
                ServiceName = config['name']

            # Executa o comando SC QUERY para verificar o status
            resultado = subprocess.run(["sc", "query", ServiceName], capture_output=True, text=True)
            saida = resultado.stdout

            # Buscar o status na saída do comando
            if "RUNNING" in saida:
                return "RUNNING"
            elif "STOPPED" in saida:
                return "STOPPED"
            elif "PAUSED" in saida:
                return "PAUSED"
            elif "START_PENDING" in saida:
                return "START_PENDING"
            elif "STOP_PENDING" in saida:
                return "STOP_PENDING"
            else:
                return f"UNKNOWN STATUS: {saida.strip()}"
        
        except Exception as Err:
            log = ConfigManager.get('log')
            if log:
                log.erro(f"Erro ao obter status do serviço [{ServiceName}]: {Err}")
            return f"ERROR: {Err}"
        #
        #
    @staticmethod 
    def RunAsDaemon(): # Executa o script como um daemon
        ## use @staticmethod quando precisar referenciar o método sem instanciar a classe e não precisar de acesso a instâncias ou à própria classe
        ## se precisar acessar métodos ou atributos da classe e não da instância, use @classmethod, mas isso implcia em passar (cls) e não (self) na definição método

        log = ConfigManager.get('log')
        daemon = ConfigManager.get('daemon')   
        config = ConfigManager.get('config')                

        if log is None or (not isinstance(log, lbx_logger) and not isinstance(log, SafeLogger)):
            raise ValueError(f'Argumento "log" é mandatório e deve ser uma instância de "lbxtoolkit.lbx_logger" ou "lbxtoolkit.SaffeLogger"')
        elif daemon is None or not hasattr(daemon, 'run') or not hasattr(daemon, 'stop'):
            raise ValueError(f'Argumento "daemon" é mandatório e deve possuir os métodos run() e stop()')  
        elif config is None or not 'name' in config or not 'display_name' in config or not 'description' in config:
            raise ValueError(f'Argumento "config" é mandatório e deve ser um dicionário contendo as chaves/valores para "name", "display_name" e "description"')
        elif [chave for chave in config if config[chave] is None]:
            raise ValueError(f'Argumento "config" ({config}) possui as seguintes chaves com valores inválidos [None]: {[chave for chave in config if config[chave] is None]:}')
              
        PID = daemon.PID if daemon.PID else os.getppid()
        OS = daemon.OS if daemon.OS else platform.system()
        mode = daemon.mode if daemon.mode else '[DAEMON (console)]'
        IP = daemon.IP if daemon.IP else socket.gethostbyname(socket.gethostname())
        Host = daemon.Host if daemon.Host else socket.gethostname()
        Usuario = daemon.Usuario if daemon.Usuario else os.getlogin() if OS == 'Windows' else os.path.expanduser('~').split(r'/')[1]

        try:                
            Kill = f'taskkil /F /PID {PID}' if OS=='Windows' else f'kill -9 {PID}'
            Stop = f'use Ctrl+C (ou excepcionalmente [{Kill}])' if mode=='[DAEMON (console)]' else f'PARE o serviço [{config['display_name']} ({config['name']})]'
            log.info(f'Executando como {mode} em {Host}/{IP}({Usuario}). Para encerrar {Stop}...') 
            daemon.run()
        except KeyboardInterrupt:
            daemon.stop('STOP')
            log.info('Execução encerrada por Ctrl+C! [pego fora do daemon')
        except Exception as Err:
            daemon.stop('CRASH')
            log.erro(f'Interrompido por erro não previsto [pego fora do daemon]: [{Err}]')            
        finally:
            log.info('daemon encerrado!')               
        #
        #