from pathlib import Path

import frontmatter

from config import VAULT_PATH, validate_config
from database import get_or_create_table
from embeddings import create_embedding


# ============================================================
# RECHERCHE
# ============================================================

def brain_search(
    query: str,
    limit: int = 5,
):
    """
    Recherche les connaissances les plus pertinentes
    dans le cerveau.
    """

    if not query or not query.strip():
        raise ValueError(
            "La requête ne peut pas être vide."
        )

    # --------------------------------------------------------
    # Transformation de la question en vecteur
    # --------------------------------------------------------

    query_vector = create_embedding(
        query.strip()
    )

    # --------------------------------------------------------
    # Recherche LanceDB
    # --------------------------------------------------------

    table = get_or_create_table()

    results = (
        table
        .search(query_vector)
        .limit(limit)
        .to_list()
    )

    return results


# ============================================================
# LECTURE D'UNE NOTE
# ============================================================

def brain_read(
    source: str,
):
    """
    Lit une note directement depuis Obsidian.

    `source` doit être un chemin relatif au Vault.
    """

    file_path = (
        VAULT_PATH / source
    ).resolve()

    # --------------------------------------------------------
    # Sécurité : empêcher de sortir du Vault
    # --------------------------------------------------------

    try:

        file_path.relative_to(
            VAULT_PATH
        )

    except ValueError:

        raise ValueError(
            "Le fichier demandé est en dehors du Vault."
        )

    # --------------------------------------------------------
    # Vérification
    # --------------------------------------------------------

    if not file_path.exists():

        raise FileNotFoundError(
            f"Note introuvable : {source}"
        )

    if not file_path.is_file():

        raise ValueError(
            f"Le chemin n'est pas un fichier : {source}"
        )

    # --------------------------------------------------------
    # Lecture
    # --------------------------------------------------------

    post = frontmatter.load(
        file_path
    )

    return {
        "source": source,

        "title": file_path.stem,

        "metadata": dict(
            post.metadata
        ),

        "content": post.content.strip(),
    }


# ============================================================
# NOTES RECENTES
# ============================================================

def brain_recent(
    limit: int = 10,
):
    """
    Retourne les notes Markdown récemment modifiées
    dans le Vault.
    """

    if limit <= 0:

        raise ValueError(
            "limit doit être supérieur à 0."
        )

    # --------------------------------------------------------
    # Recherche des fichiers Markdown
    # --------------------------------------------------------

    files = list(
        VAULT_PATH.rglob("*.md")
    )

    # --------------------------------------------------------
    # Tri par date de modification
    # --------------------------------------------------------

    files.sort(
        key=lambda path: path.stat().st_mtime,
        reverse=True,
    )

    # --------------------------------------------------------
    # Construction du résultat
    # --------------------------------------------------------

    results = []

    for file_path in files[:limit]:

        relative_path = str(
            file_path.relative_to(
                VAULT_PATH
            )
        )

        results.append(
            {
                "source": relative_path,

                "name": file_path.stem,

                "modified": file_path.stat().st_mtime,
            }
        )

    return results


# ============================================================
# TEST
# ============================================================

if __name__ == "__main__":

    validate_config()

    print()
    print("=" * 60)
    print("              CerveauIA - Brain API")
    print("=" * 60)


    # ========================================================
    # TEST SEARCH
    # ========================================================

    print()
    print("[1] brain_search()")
    print()

    results = brain_search(
        "Qu'est-ce que le projet CerveauIA ?",
        limit=3,
    )

    for index, result in enumerate(
        results,
        start=1,
    ):

        print(
            f"#{index} "
            f"{result.get('title', 'Sans titre')}"
        )

        print(
            f"    Section : "
            f"{result.get('section', '')}"
        )

        print(
            f"    Source  : "
            f"{result.get('source', '')}"
        )

        print(
            f"    Type    : "
            f"{result.get('type', '')}"
        )

        print(
            f"    Distance: "
            f"{result.get('_distance', '')}"
        )


    # ========================================================
    # TEST READ
    # ========================================================

    print()
    print("[2] brain_read()")
    print()

    try:

        note = brain_read(
            "03_Connaissances/test-rag.md"
        )

        print(
            f"Titre : {note['title']}"
        )

        print(
            f"Métadonnées : {note['metadata']}"
        )

        print()
        print("Contenu :")
        print(note["content"])

    except Exception as error:

        print(
            f"[ERREUR] {error}"
        )


    # ========================================================
    # TEST RECENT
    # ========================================================

    print()
    print("[3] brain_recent()")
    print()

    recent = brain_recent(
        limit=10
    )

    for index, note in enumerate(
        recent,
        start=1,
    ):

        print(
            f"#{index} "
            f"{note['source']}"
        )


    print()
    print("=" * 60)
    print("Tests terminés.")
    print("=" * 60)
    print()