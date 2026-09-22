import lancedb

from config import (
    DATABASE_PATH,
    TABLE_NAME,
)


# ============================================================
# CONNEXION LANCEDB
# ============================================================

db = lancedb.connect(
    str(DATABASE_PATH)
)


# ============================================================
# CREATION / OUVERTURE DE LA TABLE
# ============================================================

def get_or_create_table():

    tables = db.list_tables().tables

    if TABLE_NAME in tables:

        return db.open_table(
            TABLE_NAME
        )

    # --------------------------------------------------------
    # Ligne temporaire uniquement pour créer le schéma
    # --------------------------------------------------------

    table = db.create_table(
        TABLE_NAME,
        data=[
            {
                "id": "__schema__",

                "text": "",

                "vector": [0.0] * 1024,

                "title": "",

                "section": "",

                "type": "system",

                "category": "system",

                "importance": 0,

                "confidence": 0.0,

                "status": "system",

                "source": "__schema__",
            }
        ],
    )

    # --------------------------------------------------------
    # Suppression de la ligne temporaire
    # --------------------------------------------------------

    table.delete(
        "id = '__schema__'"
    )

    return table


# ============================================================
# TEST
# ============================================================

if __name__ == "__main__":

    table = get_or_create_table()

    print(
        "Base LanceDB fonctionnelle."
    )

    print()

    print(
        f"Base       : {DATABASE_PATH}"
    )

    print(
        f"Table      : {TABLE_NAME}"
    )

    print(
        f"Tables     : {db.list_tables().tables}"
    )

    print(
        f"Nb lignes  : {table.count_rows()}"
    )