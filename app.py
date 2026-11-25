"""
Ponto de entrada da aplicação.

Modos de execução:
    python app.py              -> Inicia o menu categorizado no terminal (apresentação oral)
    python app.py --web        -> Inicia o servidor HTTP nativo com a interface gráfica (porta 8000)
    python app.py --web 8080   -> Inicia o servidor HTTP em uma porta personalizada
"""
import sys


def main():
    if "--web" in sys.argv:
        args = [a for a in sys.argv[1:] if a != "--web"]
        porta = int(args[0]) if args and args[0].isdigit() else 8000
        from src.ui.api_server import main as iniciar_web
        iniciar_web(porta)
    else:
        from src.ui.menu_console import iniciar_menu_console
        iniciar_menu_console()


if __name__ == "__main__":
    main()
