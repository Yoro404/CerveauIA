import asyncio
import sys
from pathlib import Path

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


TEST_NOTE = "03_Connaissances/mcp-write-test.md"


async def main():
    server_params = StdioServerParameters(
        command=sys.executable,
        args=["src/mcp_server.py"],
    )

    print("=" * 60)
    print("TEST MCP - CerveauIA")
    print("=" * 60)
    print()

    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:

            # --------------------------------------------------
            # Connexion
            # --------------------------------------------------

            await session.initialize()

            print("[OK] Connexion au serveur MCP")
            print()

            # --------------------------------------------------
            # Liste des outils
            # --------------------------------------------------

            tools = await session.list_tools()

            print("Outils disponibles :")
            print()

            for tool in tools.tools:
                print(f"  - {tool.name}")
                print(f"    {tool.description}")
                print()

            # --------------------------------------------------
            # TEST 1 : search_brain
            # --------------------------------------------------

            print("=" * 60)
            print("TEST 1 : search_brain")
            print("=" * 60)

            result = await session.call_tool(
                "search_brain",
                {
                    "query": "Qu'est-ce que le projet CerveauIA ?",
                    "limit": 3,
                },
            )

            print()
            print(result)
            print()

            # --------------------------------------------------
            # TEST 2 : read_brain_note
            # --------------------------------------------------

            print("=" * 60)
            print("TEST 2 : read_brain_note")
            print("=" * 60)

            result = await session.call_tool(
                "read_brain_note",
                {
                    "source": "03_Connaissances/test-rag.md",
                },
            )

            print()
            print(result)
            print()

            # --------------------------------------------------
            # TEST 3 : recent_brain_notes
            # --------------------------------------------------

            print("=" * 60)
            print("TEST 3 : recent_brain_notes")
            print("=" * 60)

            result = await session.call_tool(
                "recent_brain_notes",
                {
                    "limit": 10,
                },
            )

            print()
            print(result)
            print()

            # --------------------------------------------------
            # TEST 4 : save_brain_note_tool
            # --------------------------------------------------

            print("=" * 60)
            print("TEST 4 : save_brain_note_tool")
            print("=" * 60)

            create_content = """---
type: knowledge
category: test
importance: 3
confidence: 1.0
status: active
---

# Test écriture MCP

Cette note a été créée automatiquement par le test MCP.

Le code de test est MCP-CREATE-001.
"""

            result = await session.call_tool(
                "save_brain_note_tool",
                {
                    "source": TEST_NOTE,
                    "content": create_content,
                },
            )

            print()
            print(result)
            print()

            # --------------------------------------------------
            # TEST 5 : update_brain_note_tool
            # --------------------------------------------------

            print("=" * 60)
            print("TEST 5 : update_brain_note_tool")
            print("=" * 60)

            update_content = """---
type: knowledge
category: test
importance: 5
confidence: 1.0
status: active
---

# Test écriture MCP

Cette note a été créée puis modifiée automatiquement par le test MCP.

Le code de test est MCP-UPDATE-002.

La modification fonctionne correctement.
"""

            result = await session.call_tool(
                "update_brain_note_tool",
                {
                    "source": TEST_NOTE,
                    "content": update_content,
                },
            )

            print()
            print(result)
            print()

            # --------------------------------------------------
            # TEST 6 : vérifier la note créée/modifiée
            # --------------------------------------------------

            print("=" * 60)
            print("TEST 6 : lecture de la note modifiée")
            print("=" * 60)

            result = await session.call_tool(
                "read_brain_note",
                {
                    "source": TEST_NOTE,
                },
            )

            print()
            print(result)
            print()

            print("=" * 60)
            print("TEST MCP TERMINÉ")
            print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())