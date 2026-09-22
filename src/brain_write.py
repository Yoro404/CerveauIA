from pathlib import Path

from config import VAULT_PATH


def _validate_source(source: str) -> Path:
    """
    Vérifie qu'un chemin correspond à un fichier Markdown
    situé à l'intérieur du Vault.
    """

    if not source or not source.strip():
        raise ValueError("Le chemin de la note ne peut pas être vide.")

    source = source.strip()

    if not source.lower().endswith(".md"):
        raise ValueError(
            "CerveauIA autorise uniquement les fichiers Markdown (.md)."
        )

    file_path = (VAULT_PATH / source).resolve()

    try:
        file_path.relative_to(VAULT_PATH)
    except ValueError:
        raise ValueError(
            "Le fichier demandé est en dehors du Vault."
        )

    return file_path


def save_brain_note(
    source: str,
    content: str,
) -> dict:
    """
    Crée une nouvelle note Markdown dans le Vault.

    Le fichier ne doit pas déjà exister.
    """

    if content is None:
        raise ValueError("Le contenu ne peut pas être vide.")

    file_path = _validate_source(source)

    if file_path.exists():
        raise FileExistsError(
            f"La note existe déjà : {source}"
        )

    file_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    file_path.write_text(
        content,
        encoding="utf-8",
        newline="\n",
    )

    return {
        "success": True,
        "action": "created",
        "source": str(
            file_path.relative_to(VAULT_PATH)
        ),
    }