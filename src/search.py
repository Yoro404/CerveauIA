from config import validate_config
from database import get_or_create_table
from embeddings import create_embedding


# ============================================================
# RECHERCHE SEMANTIQUE
# ============================================================

def search(
    query: str,
    limit: int = 5,
):
    """
    Recherche les chunks les plus pertinents
    à partir d'une requête sémantique.
    """

    if not query or not query.strip():

        raise ValueError(
            "La requête ne peut pas être vide."
        )

    # --------------------------------------------------------
    # Embedding de la question
    # --------------------------------------------------------

    query_vector = create_embedding(
        query.strip()
    )

    # --------------------------------------------------------
    # Connexion LanceDB
    # --------------------------------------------------------

    table = get_or_create_table()

    # --------------------------------------------------------
    # Recherche vectorielle
    # --------------------------------------------------------

    results = (
        table
        .search(query_vector)
        .limit(limit)
        .to_list()
    )

    return results


# ============================================================
# AFFICHAGE
# ============================================================

def display_results(
    query: str,
    results: list,
):
    """
    Affiche les résultats de recherche.
    """

    print()
    print("=" * 70)
    print("RECHERCHE")
    print("=" * 70)

    print()
    print(
        f"Question : {query}"
    )

    print(
        f"Résultats : {len(results)}"
    )

    print()

    if not results:

        print(
            "Aucun résultat."
        )

        return

    # --------------------------------------------------------
    # Résultats
    # --------------------------------------------------------

    for index, result in enumerate(
        results,
        start=1
    ):

        print(
            "-" * 70
        )

        print(
            f"#{index}"
        )

        # ----------------------------------------------------
        # Identité du document
        # ----------------------------------------------------

        print(
            f"Titre       : "
            f"{result.get('title', 'inconnu')}"
        )

        print(
            f"Section     : "
            f"{result.get('section', 'inconnue')}"
        )

        print(
            f"Source      : "
            f"{result.get('source', 'inconnue')}"
        )

        # ----------------------------------------------------
        # Métadonnées
        # ----------------------------------------------------

        print(
            f"Type        : "
            f"{result.get('type', 'inconnu')}"
        )

        print(
            f"Catégorie   : "
            f"{result.get('category', 'inconnue')}"
        )

        print(
            f"Importance  : "
            f"{result.get('importance', '?')}"
        )

        print(
            f"Confiance   : "
            f"{result.get('confidence', '?')}"
        )

        print(
            f"Statut      : "
            f"{result.get('status', 'inconnu')}"
        )

        # ----------------------------------------------------
        # Distance
        # ----------------------------------------------------

        if "_distance" in result:

            print(
                f"Distance    : "
                f"{result['_distance']}"
            )

        # ----------------------------------------------------
        # Texte
        # ----------------------------------------------------

        print()

        print(
            "Contenu :"
        )

        print(
            result.get(
                "text",
                ""
            )
        )

    print()

    print(
        "=" * 70
    )


# ============================================================
# TEST INTERACTIF
# ============================================================

if __name__ == "__main__":

    validate_config()

    print()
    print("=" * 44)
    print("       CerveauIA - Recherche RAG")
    print("=" * 44)
    print()

    query = input(
        "Pose ta question : "
    ).strip()

    if not query:

        print()
        print(
            "[ERREUR] Question vide."
        )

        raise SystemExit(1)

    print()
    print(
        "Recherche en cours..."
    )

    results = search(
        query=query,
        limit=5,
    )

    display_results(
        query=query,
        results=results,
    )