from openai import OpenAI

from config import (
    EMBEDDING_MODEL,
    LM_STUDIO_BASE_URL,
)


# ============================================================
# CLIENT LM STUDIO
# ============================================================

client = OpenAI(
    base_url=LM_STUDIO_BASE_URL,
    api_key="lm-studio",
)


# ============================================================
# CREATION D'UN EMBEDDING
# ============================================================

def create_embedding(text: str) -> list[float]:
    """
    Transforme un texte en vecteur grâce au modèle
    d'embedding chargé dans LM Studio.
    """

    if not text or not text.strip():
        raise ValueError(
            "Impossible de créer un embedding à partir d'un texte vide."
        )

    response = client.embeddings.create(
        model=EMBEDDING_MODEL,
        input=text,
    )

    return response.data[0].embedding


# ============================================================
# TEST
# ============================================================

if __name__ == "__main__":

    text = (
        "Je construis un cerveau personnel pour "
        "mon agent Hermes avec Obsidian et un système RAG."
    )

    print("Création de l'embedding...")

    embedding = create_embedding(text)

    print()
    print(f"Modèle      : {EMBEDDING_MODEL}")
    print(f"Dimension    : {len(embedding)}")
    print(f"Premiers éléments : {embedding[:10]}")