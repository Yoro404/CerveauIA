import os
from pathlib import Path

from dotenv import load_dotenv


# ============================================================
# CHEMIN DU PROJET
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parent.parent


# ============================================================
# CHARGEMENT DU .ENV
# ============================================================

ENV_FILE = PROJECT_ROOT / ".env"

load_dotenv(ENV_FILE)


# ============================================================
# OBSIDIAN
# ============================================================

VAULT_PATH = Path(
    os.environ["VAULT_PATH"]
).resolve()


# ============================================================
# LM STUDIO
# ============================================================

LM_STUDIO_BASE_URL = os.getenv(
    "LM_STUDIO_BASE_URL",
    "http://localhost:1234/v1"
)

EMBEDDING_MODEL = os.getenv(
    "EMBEDDING_MODEL",
    "text-embedding-bge-m3"
)


# ============================================================
# LANCEDB
# ============================================================

DATABASE_PATH = Path(
    os.getenv("DATABASE_PATH", "./database")
)

if not DATABASE_PATH.is_absolute():
    DATABASE_PATH = PROJECT_ROOT / DATABASE_PATH

DATABASE_PATH = DATABASE_PATH.resolve()


TABLE_NAME = os.getenv(
    "TABLE_NAME",
    "memories"
)


# ============================================================
# RAG
# ============================================================

CHUNK_SIZE = int(
    os.getenv("CHUNK_SIZE", "800")
)

CHUNK_OVERLAP = int(
    os.getenv("CHUNK_OVERLAP", "100")
)

MIN_CHUNK_SIZE = int(
    os.getenv("MIN_CHUNK_SIZE", "100")
)


# ============================================================
# VALIDATION
# ============================================================

def validate_config():

    if not ENV_FILE.exists():
        raise FileNotFoundError(
            f"Fichier .env introuvable : {ENV_FILE}"
        )

    if not VAULT_PATH.exists():
        raise FileNotFoundError(
            f"Le Vault Obsidian est introuvable : {VAULT_PATH}"
        )

    if not VAULT_PATH.is_dir():
        raise NotADirectoryError(
            f"VAULT_PATH n'est pas un dossier : {VAULT_PATH}"
        )

    if CHUNK_SIZE <= 0:
        raise ValueError(
            "CHUNK_SIZE doit être supérieur à 0."
        )

    if CHUNK_OVERLAP < 0:
        raise ValueError(
            "CHUNK_OVERLAP ne peut pas être négatif."
        )

    if CHUNK_OVERLAP >= CHUNK_SIZE:
        raise ValueError(
            "CHUNK_OVERLAP doit être inférieur à CHUNK_SIZE."
        )

    if MIN_CHUNK_SIZE <= 0:
        raise ValueError(
            "MIN_CHUNK_SIZE doit être supérieur à 0."
        )


# ============================================================
# TEST
# ============================================================

if __name__ == "__main__":

    validate_config()

    print("Configuration valide.")
    print()
    print(f"Projet          : {PROJECT_ROOT}")
    print(f"Vault Obsidian  : {VAULT_PATH}")
    print(f"LM Studio       : {LM_STUDIO_BASE_URL}")
    print(f"Embedding       : {EMBEDDING_MODEL}")
    print(f"Base LanceDB    : {DATABASE_PATH}")
    print(f"Table           : {TABLE_NAME}")
    print(f"Chunk size      : {CHUNK_SIZE}")
    print(f"Chunk overlap   : {CHUNK_OVERLAP}")
    print(f"Min chunk size  : {MIN_CHUNK_SIZE}")