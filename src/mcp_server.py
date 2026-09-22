import asyncio
import sys

from mcp.server import MCPServer

from brain import (
    brain_read,
    brain_recent,
    brain_search,
)

from brain_write import save_brain_note
from brain_update import update_brain_note


# ============================================================
# SERVEUR MCP
# ============================================================

mcp = MCPServer("CerveauIA")


# ============================================================
# OUTIL : RECHERCHE DANS LE CERVEAU
# ============================================================

@mcp.tool()
def search_brain(
    query: str,
    limit: int = 5,
) -> list[dict]:
    """
    Recherche des informations pertinentes
    dans le cerveau personnel.
    """

    try:
        results = brain_search(
            query=query,
            limit=limit,
        )

        output = []

        for result in results:
            output.append({
                "title": result.get("title", ""),
                "section": result.get("section", ""),
                "source": result.get("source", ""),
                "type": result.get("type", ""),
                "category": result.get("category", ""),
                "importance": result.get("importance", 0),
                "confidence": result.get("confidence", 0),
                "status": result.get("status", ""),
                "distance": result.get("_distance", None),
                "text": result.get("text", ""),
            })

        return output

    except Exception as exc:
        print(
            f"[ERREUR search_brain] {type(exc).__name__}: {exc}",
            file=sys.stderr,
            flush=True,
        )

        raise


# ============================================================
# OUTIL : LIRE UNE NOTE
# ============================================================

@mcp.tool()
def read_brain_note(
    source: str,
) -> dict:
    """
    Lit une note complète directement depuis Obsidian.

    Le chemin doit être relatif à la racine
    du Vault Obsidian.

    Exemple :
        03_Connaissances/test-rag.md
    """

    return brain_read(source)


# ============================================================
# OUTIL : NOTES RÉCENTES
# ============================================================

@mcp.tool()
def recent_brain_notes(
    limit: int = 10,
) -> list[dict]:
    """
    Retourne les notes Markdown récemment modifiées
    dans le Vault Obsidian.
    """

    return brain_recent(
        limit=limit,
    )

@mcp.tool()
def save_brain_note_tool(
    source: str,
    content: str,
) -> dict:
    """
    Crée une nouvelle note Markdown dans le Vault CerveauIA.

    Le chemin doit être relatif à la racine du Vault.
    La note ne doit pas déjà exister.
    """

    return save_brain_note(
        source=source,
        content=content,
    )


@mcp.tool()
def update_brain_note_tool(
    source: str,
    content: str,
) -> dict:
    """
    Met à jour une note Markdown existante dans le Vault CerveauIA.

    Le contenu fourni remplace le contenu actuel de la note.
    Le chemin doit être relatif à la racine du Vault.
    """

    return update_brain_note(
        source=source,
        content=content,
    )

# ============================================================
# DÉMARRAGE DU SERVEUR
# ============================================================

if __name__ == "__main__":
    asyncio.run(
        mcp.run_stdio_async()
    )