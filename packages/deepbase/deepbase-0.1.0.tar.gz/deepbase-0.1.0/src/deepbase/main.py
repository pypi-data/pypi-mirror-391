# src/deepbase/main.py

import os
import argparse

# --- CONFIGURAZIONE DEI FILTRI ---

# Directory da ignorare durante la scansione
IGNORED_DIRS = {
    "__pycache__", ".git", ".idea", ".vscode", "venv", ".venv", "env",
    ".env", "node_modules", "build", "dist", "target", "out", "bin",
    "obj", "logs", "tmp", "eggs", ".eggs", ".pytest_cache", ".tox",
}

# Estensioni e nomi di file significativi da includere
SIGNIFICANT_EXTENSIONS = {
    ".py", ".java", ".js", ".ts", ".html", ".css", ".scss", ".sql",
    ".md", ".json", ".xml", ".yml", ".yaml", ".sh", ".bat", "Dockerfile",
    ".dockerignore", ".gitignore", "requirements.txt", "pom.xml", "gradlew",
    "pyproject.toml", "setup.py",
}

def is_significant_file(file_path):
    """Verifica se un file è significativo."""
    file_name = os.path.basename(file_path)
    if file_name in SIGNIFICANT_EXTENSIONS:
        return True
    _, ext = os.path.splitext(file_name)
    return ext in SIGNIFICANT_EXTENSIONS

def generate_directory_tree(root_dir):
    """Genera una rappresentazione testuale della struttura delle cartelle."""
    tree_str = f"Struttura del progetto in: {os.path.abspath(root_dir)}\n\n"
    for dirpath, dirnames, filenames in os.walk(root_dir, topdown=True):
        # Esclude le directory non significative
        dirnames[:] = [d for d in dirnames if d not in IGNORED_DIRS and not d.startswith('.')]
        
        # Calcola il livello di indentazione
        level = dirpath.replace(root_dir, '').count(os.sep)
        indent = ' ' * 4 * (level)
        
        # Aggiunge la cartella corrente all'albero
        tree_str += f"{indent}📂 {os.path.basename(dirpath)}/\n"
        
        sub_indent = ' ' * 4 * (level + 1)
        
        # Aggiunge i file significativi
        for f in filenames:
            if is_significant_file(os.path.join(dirpath, f)):
                tree_str += f"{sub_indent}📄 {f}\n"
    
    return tree_str

def create_llm_context(root_dir, output_file):
    """Crea il documento di contesto unificato per l'LLM."""
    print(f"Avvio della scansione di '{root_dir}'...")
    try:
        with open(output_file, "w", encoding="utf-8") as outfile:
            # 1. Scrive il nome del progetto
            outfile.write(f"# Contesto del Progetto: {os.path.basename(os.path.abspath(root_dir))}\n\n")
            
            # 2. Scrive la struttura delle cartelle e dei file
            outfile.write("="*80 + "\n")
            outfile.write("### STRUTTURA DEL PROGETTO ###\n")
            outfile.write("="*80 + "\n\n")
            directory_tree = generate_directory_tree(root_dir)
            outfile.write(directory_tree)
            outfile.write("\n\n")

            # 3. Scrive il contenuto dei file
            outfile.write("="*80 + "\n")
            outfile.write("### CONTENUTO DEI FILE ###\n")
            outfile.write("="*80 + "\n\n")

            for dirpath, dirnames, filenames in os.walk(root_dir, topdown=True):
                dirnames[:] = [d for d in dirnames if d not in IGNORED_DIRS and not d.startswith('.')]

                for filename in sorted(filenames):
                    file_path = os.path.join(dirpath, filename)
                    if is_significant_file(file_path):
                        relative_path = os.path.relpath(file_path, root_dir).replace('\\', '/')
                        print(f"  -> Includo il file: {relative_path}")
                        
                        outfile.write(f"--- INIZIO FILE: {relative_path} ---\n\n")
                        try:
                            with open(file_path, "r", encoding="utf-8", errors="ignore") as infile:
                                content = infile.read()
                                outfile.write(content)
                        except Exception as e:
                            outfile.write(f"!!! Errore durante la lettura del file: {e} !!!\n")
                        
                        outfile.write(f"\n\n--- FINE FILE: {relative_path} ---\n\n")
                        outfile.write("-" * 40 + "\n\n")

        print(f"\n[SUCCESS] Contesto creato con successo nel file: {output_file}")

    except IOError as e:
        print(f"\n[ERROR] Errore durante la scrittura del file di output: {e}")
    except Exception as e:
        print(f"\n[ERROR] Si è verificato un errore inaspettato: {e}")

def cli():
    """Funzione di entry-point per la riga di comando."""
    parser = argparse.ArgumentParser(
        prog="deepbase",
        description="Crea un documento di contesto per un LLM esplorando una directory di progetto.",
        formatter_class=argparse.RawTextHelpFormatter
    )
    
    parser.add_argument(
        "directory",
        help="La directory principale del progetto da esplorare."
    )
    
    parser.add_argument(
        "-o", "--output",
        default="llm_context.md",
        help="Il nome del file di output che conterrà il contesto.\n(default: llm_context.md)"
    )
    
    parser.add_argument(
        "-v", "--version",
        action="version",
        version="%(prog)s 0.1.0" # La versione sarà gestita da pyproject.toml
    )
    
    args = parser.parse_args()

    if not os.path.isdir(args.directory):
        print(f"[ERROR] La directory specificata non esiste: {args.directory}")
    else:
        create_llm_context(args.directory, args.output)

if __name__ == "__main__":
    cli()