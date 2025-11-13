# SmartBase

**SmartBase** è un tool a riga di comando che analizza una directory di progetto, estrae la struttura delle cartelle e il contenuto di tutti i file di codice significativi, e li consolida in un unico file di testo/markdown.

Questo "contesto" unificato è perfetto per essere fornito a un Large Language Model (LLM) per consentirgli di comprendere a fondo l'intero codebase.

## Caratteristiche

- **Struttura del Progetto**: Genera una visualizzazione ad albero della struttura di cartelle e file.
- **Filtro Intelligente**: Ignora automaticamente le directory comuni non necessarie (`.git`, `venv`, `node_modules`, etc.).
- **Selezione per Estensione**: Include solo i file con estensioni di codice o configurazione rilevanti (`.py`, `.js`, `.md`, `Dockerfile`, etc.).
- **Output Unificato**: Combina tutto in un unico file, facile da copiare e incollare.
- **Pronto per PyPI**: Facile da installare tramite `pip`.

## Installazione

Puoi installare SmartBase direttamente da PyPI:

```sh
pip install smartbase
```

## Come Usarlo

Una volta installato, avrai a disposizione il comando `smartbase` nel tuo terminale.

**Uso di base:**

Naviga nella cartella del tuo progetto (o in una cartella padre) ed esegui:

```sh
smartbase /percorso/del/tuo/progetto
```

Questo comando creerà un file chiamato `llm_context.md` nella directory corrente.

**Specificare un file di output:**

Usa l'opzione `-o` o `--output` per definire un nome diverso per il file di contesto.

```sh
smartbase /percorso/del/tuo/progetto -o contesto_progetto.txt
```

## Licenza

Questo progetto è rilasciato sotto la licenza MIT. Vedi il file `LICENSE` per i dettagli.