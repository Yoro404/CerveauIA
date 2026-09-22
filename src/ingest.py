from pathlib import Path
import re

import frontmatter

from config import (
    CHUNK_SIZE,
    MIN_CHUNK_SIZE,
    VAULT_PATH,
    validate_config,
)

from database import get_or_create_table
from embeddings import create_embedding


# ============================================================
# EXTRACTION DU TITRE
# ============================================================

def extract_title(
    file_path: Path,
    content: str,
) -> str:
    """
    Détermine le titre de la note.

    Priorité :
    1. titre H1 du Markdown
    2. nom du fichier
    """

    match = re.search(
        r"(?m)^#\s+(.+?)\s*$",
        content
    )

    if match:

        return match.group(1).strip()

    return file_path.stem


# ============================================================
# DECOUPAGE INTELLIGENT
# ============================================================

def split_markdown(
    content: str,
    chunk_size: int = CHUNK_SIZE,
) -> list[dict]:
    """
    Découpe un document Markdown en conservant
    le contexte des sections.
    """

    lines = content.splitlines()

    chunks = []

    current_section = ""

    current_parts = []

    current_word_count = 0

    # --------------------------------------------------------
    # Fonction interne pour sauvegarder un chunk
    # --------------------------------------------------------

    def save_chunk():

        nonlocal current_parts
        nonlocal current_word_count

        if not current_parts:

            return

        text = "\n\n".join(
            part.strip()
            for part in current_parts
            if part.strip()
        ).strip()

        if not text:

            current_parts = []
            current_word_count = 0

            return

        chunks.append(
            {
                "text": text,
                "section": current_section,
            }
        )

        current_parts = []
        current_word_count = 0

    # --------------------------------------------------------
    # Parcours du Markdown
    # --------------------------------------------------------

    for line in lines:

        stripped = line.strip()

        # ----------------------------------------------------
        # Ligne vide
        # ----------------------------------------------------

        if not stripped:

            continue

        # ----------------------------------------------------
        # Titre Markdown
        # ----------------------------------------------------

        heading_match = re.match(
            r"^(#{1,6})\s+(.+?)\s*$",
            stripped
        )

        if heading_match:

            # Avant de changer de section,
            # on sauvegarde le chunk actuel.
            save_chunk()

            level = len(
                heading_match.group(1)
            )

            heading = heading_match.group(2).strip()

            current_section = heading

            # Le titre est conservé dans le chunk
            # afin de maintenir le contexte.
            current_parts.append(
                stripped
            )

            current_word_count = len(
                stripped.split()
            )

            continue

        # ----------------------------------------------------
        # Ligne normale
        # ----------------------------------------------------

        line_word_count = len(
            stripped.split()
        )

        # ----------------------------------------------------
        # Si le chunk devient trop gros,
        # on le sauvegarde.
        # ----------------------------------------------------

        if (
            current_word_count > 0
            and current_word_count + line_word_count
            > chunk_size
        ):

            save_chunk()

            # On remet le contexte de section
            # au début du nouveau chunk.
            if current_section:

                current_parts.append(
                    f"Section : {current_section}"
                )

                current_word_count = len(
                    current_section.split()
                )

        # ----------------------------------------------------
        # Ajout de la ligne
        # ----------------------------------------------------

        current_parts.append(
            stripped
        )

        current_word_count += (
            line_word_count
        )

    # --------------------------------------------------------
    # Dernier chunk
    # --------------------------------------------------------

    save_chunk()

    return chunks


# ============================================================
# CHEMIN RELATIF
# ============================================================

def get_relative_source(
    file_path: Path,
) -> str:

    try:

        return str(
            file_path.relative_to(
                VAULT_PATH
            )
        )

    except ValueError:

        return str(file_path)


# ============================================================
# LECTURE MARKDOWN
# ============================================================

def read_markdown(
    file_path: Path,
):

    raw_text = file_path.read_text(
        encoding="utf-8"
    )

    post = frontmatter.loads(
        raw_text
    )

    content = post.content.strip()

    metadata = dict(
        post.metadata
    )

    return content, metadata


# ============================================================
# INGESTION D'UN FICHIER
# ============================================================

def ingest_file(
    file_path: Path,
):

    print()
    print(
        f"Lecture : {file_path}"
    )

    # --------------------------------------------------------
    # Lecture
    # --------------------------------------------------------

    content, metadata = read_markdown(
        file_path
    )

    # --------------------------------------------------------
    # Métadonnées
    # --------------------------------------------------------

    print()
    print(
        "Métadonnées détectées :"
    )

    if metadata:

        for key, value in metadata.items():

            print(
                f"  {key} = {value}"
            )

    else:

        print(
            "  Aucune métadonnée"
        )

    # --------------------------------------------------------
    # Vérification
    # --------------------------------------------------------

    if not content:

        print()
        print(
            f"[SKIP] Note vide : {file_path}"
        )

        return

    # --------------------------------------------------------
    # Informations document
    # --------------------------------------------------------

    title = extract_title(
        file_path,
        content
    )

    relative_source = (
        get_relative_source(
            file_path
        )
    )

    print()
    print(
        f"Titre : {title}"
    )

    # --------------------------------------------------------
    # Chunking intelligent
    # --------------------------------------------------------

    chunks = split_markdown(
        content
    )

    print(
        f"Chunks détectés : {len(chunks)}"
    )

    # --------------------------------------------------------
    # Connexion LanceDB
    # --------------------------------------------------------

    table = get_or_create_table()

    # --------------------------------------------------------
    # Suppression ancienne version
    # --------------------------------------------------------

    escaped_source = (
        relative_source.replace(
            "'",
            "''"
        )
    )

    try:

        table.delete(
            f"source = '{escaped_source}'"
        )

        print(
            f"[INFO] Ancienne version supprimée : "
            f"{relative_source}"
        )

    except Exception:

        pass

    # --------------------------------------------------------
    # Création des lignes
    # --------------------------------------------------------

    rows = []

    for index, chunk in enumerate(chunks):

        chunk_text = chunk["text"]

        section = chunk["section"]

        print()

        print(
            f"Embedding {index + 1}/"
            f"{len(chunks)} : "
            f"{file_path.name}"
        )

        if section:

            print(
                f"Section : {section}"
            )

        # ----------------------------------------------------
        # Embedding
        # ----------------------------------------------------

        vector = create_embedding(
            chunk_text
        )

        # ----------------------------------------------------
        # ID stable
        # ----------------------------------------------------

        chunk_id = (
            f"{relative_source}::{index}"
        )

        # ----------------------------------------------------
        # Ligne LanceDB
        # ----------------------------------------------------

        row = {

            "id": chunk_id,

            "text": chunk_text,

            "vector": vector,

            "title": title,

            "section": section,

            "type": str(
                metadata.get(
                    "type",
                    "unknown"
                )
            ),

            "category": str(
                metadata.get(
                    "category",
                    "unknown"
                )
            ),

            "importance": int(
                metadata.get(
                    "importance",
                    5
                )
            ),

            "confidence": float(
                metadata.get(
                    "confidence",
                    1.0
                )
            ),

            "status": str(
                metadata.get(
                    "status",
                    "active"
                )
            ),

            "source": relative_source,
        }

        rows.append(
            row
        )

    # --------------------------------------------------------
    # Ajout dans LanceDB
    # --------------------------------------------------------

    if rows:

        table.add(
            rows
        )

    # --------------------------------------------------------
    # Résultat
    # --------------------------------------------------------

    print()

    print(
        f"[OK] {len(rows)} chunk(s) indexé(s)"
    )

    print(
        f"Source : {relative_source}"
    )


# ============================================================
# TEST
# ============================================================

if __name__ == "__main__":

    validate_config()

    test_file = (
        VAULT_PATH
        / "03_Connaissances"
        / "test-rag.md"
    )

    if not test_file.exists():

        print(
            "[ERREUR] Fichier introuvable :"
        )

        print(
            test_file
        )

        raise SystemExit(1)

    ingest_file(
        test_file
    )