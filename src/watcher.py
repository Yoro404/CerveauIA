import time
from pathlib import Path

from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer

from config import VAULT_PATH, validate_config
from ingest import ingest_file


class VaultWatcher(FileSystemEventHandler):
    """
    Surveille le Vault Obsidian et réindexe automatiquement
    les fichiers Markdown modifiés ou créés.
    """

    def __init__(self):
        super().__init__()

        # Évite de traiter plusieurs événements identiques
        # générés rapidement par Obsidian.
        self.last_events = {}

    def _should_process(self, file_path: Path) -> bool:
        if file_path.suffix.lower() != ".md":
            return False

        now = time.time()
        key = str(file_path.resolve())

        last_time = self.last_events.get(key, 0)

        # Ignore les doublons pendant 1 seconde.
        if now - last_time < 1:
            return False

        self.last_events[key] = now
        return True

    def on_created(self, event):
        if event.is_directory:
            return

        file_path = Path(event.src_path)

        if not self._should_process(file_path):
            return

        print()
        print("=" * 60)
        print("[NOUVEAU] Note détectée")
        print(f"Fichier : {file_path}")
        print("=" * 60)

        self._index(file_path)

    def on_modified(self, event):
        if event.is_directory:
            return

        file_path = Path(event.src_path)

        if not self._should_process(file_path):
            return

        print()
        print("=" * 60)
        print("[MODIFICATION] Note détectée")
        print(f"Fichier : {file_path}")
        print("=" * 60)

        self._index(file_path)

    def on_deleted(self, event):
        if event.is_directory:
            return

        file_path = Path(event.src_path)

        if file_path.suffix.lower() != ".md":
            return

        print()
        print("=" * 60)
        print("[SUPPRESSION] Note supprimée")
        print(f"Fichier : {file_path}")
        print("=" * 60)

        self._delete_from_database(file_path)

    def _index(self, file_path: Path):
        try:
            # Vérification de sécurité :
            file_path.resolve().relative_to(VAULT_PATH)

            # Obsidian peut générer un événement avant
            # que le fichier soit complètement écrit.
            time.sleep(0.5)

            if not file_path.exists():
                return

            ingest_file(file_path)

            print("[OK] Synchronisation terminée.")

        except Exception as exc:
            print(f"[ERREUR] Impossible d'indexer {file_path}")
            print(f"        {exc}")

    def _delete_from_database(self, file_path: Path):
        try:
            from database import get_or_create_table

            relative_path = str(
                file_path.resolve().relative_to(VAULT_PATH)
            )

            table = get_or_create_table()

            # ingest.py utilise le champ source pour identifier
            # les chunks appartenant à une note.
            table.delete(
                f"source = '{relative_path.replace(chr(39), chr(39) * 2)}'"
            )

            print(f"[OK] Entrées supprimées de LanceDB : {relative_path}")

        except Exception as exc:
            print("[ERREUR] Impossible de supprimer l'ancienne indexation.")
            print(f"        {exc}")


def main():
    validate_config()

    print("=" * 60)
    print("CERVEAUIA — WATCHER OBSIDIAN")
    print("=" * 60)
    print()
    print(f"Vault surveillé : {VAULT_PATH}")
    print()
    print("Surveillance active.")
    print("Modifie ou crée une note .md pour tester.")
    print("CTRL+C pour arrêter.")
    print()

    event_handler = VaultWatcher()

    observer = Observer()

    observer.schedule(
        event_handler,
        str(VAULT_PATH),
        recursive=True,
    )

    observer.start()

    try:
        while True:
            time.sleep(1)

    except KeyboardInterrupt:
        print()
        print("Arrêt du watcher...")

        observer.stop()

    observer.join()

    print("Watcher arrêté.")


if __name__ == "__main__":
    main()