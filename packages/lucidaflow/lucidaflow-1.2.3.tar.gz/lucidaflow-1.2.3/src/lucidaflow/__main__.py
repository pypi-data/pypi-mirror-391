# src/lucidaflow/__main__.py
import sys
from lucidaflow.cli import run_file, start_repl

def main():
    # Se um nome de arquivo foi passado, executa o arquivo
    if len(sys.argv) > 1:
        run_file(sys.argv[1])
    # Se não, entra no modo REPL
    else:
        start_repl()

if __name__ == "__main__":
    main()