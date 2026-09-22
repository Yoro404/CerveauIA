from brain_write import _validate_source
from config import VAULT_PATH


def update_brain_note(
    source: str,
    content: str,
) -> dict:
    """
    Remplace le contenu complet d'une note Markdown existante.
    """

    if content is None:
        raise ValueError("Le contenu ne peut pas être vide.")

    file_path = _validate_source(source)

    if not file_path.exists():
        raise FileNotFoundError(
            f"La note n'existe pas : {source}"
        )

    if not file_path.is_file():
        raise ValueError(
            f"Le chemin n'est pas un fichier : {source}"
        )

    file_path.write_text(
        content,
        encoding="utf-8",
        newline="\n",
    )

    relative_path = str(
        file_path.relative_to(VAULT_PATH)
    )

    return {
        "success": True,
        "action": "updated",
        "source": relative_path,
    }