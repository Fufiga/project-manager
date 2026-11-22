"""Vérification de mise à jour basée sur les tags git, sans jamais bloquer le démarrage.

Principe : le réseau n'est jamais appelé pendant que l'utilisateur attend.
  1. start_background_check() interroge GitHub dans un thread et mémorise le
     dernier tag dans .update_state.json. Il rend la main immédiatement.
  2. prompt_for_update() lit uniquement ce fichier local (instantané) et
     propose la mise à jour (y/n) si un tag plus récent a été trouvé.

Usage dans ton TUI, au démarrage :

    from updater import start_background_check, prompt_for_update

    prompt_for_update()        # instantané : utilise le résultat du lancement précédent
    start_background_check()   # rend la main tout de suite, le réseau tourne en arrière-plan
    # ... lancer le TUI
"""

import json
import os
import re
import subprocess
import threading
import time
from pathlib import Path

# Racine du gestionnaire (dossier de ce fichier), pas le dossier courant
APP_ROOT = Path(__file__).resolve().parent
# Fichier dédié à l'état des mises à jour (séparé de data.json)
STATE_FILE = APP_ROOT / ".update_state.json"

CHECK_INTERVAL = 24 * 3600  # une vérification réseau par jour maximum
GIT_TIMEOUT = 5             # secondes, sans importance : ça tourne en arrière-plan
INCLUDE_PRERELEASES = True  # mettre False pour ignorer les -beta, -rc, etc.

_TAG_RE = re.compile(r"^v?(\d+(?:\.\d+)*)(?:-(.+))?$")
_lock = threading.Lock()


def _git(*args, timeout=GIT_TIMEOUT):
    """Exécute une commande git dans APP_ROOT. Retourne la sortie ou None."""
    try:
        result = subprocess.run(
            ["git", *args],
            cwd=APP_ROOT,
            capture_output=True,
            text=True,
            timeout=timeout,
            stdin=subprocess.DEVNULL,
            # Évite qu'une demande d'identifiants git ne vienne polluer le terminal du TUI
            env={**os.environ, "GIT_TERMINAL_PROMPT": "0"},
        )
    except (subprocess.TimeoutExpired, FileNotFoundError, OSError):
        return None
    if result.returncode != 0:
        return None
    return result.stdout.strip()


def _version_key(tag):
    """Clé de tri : v1.2.0 > v1.2.0-beta, et v1.10 > v1.9."""
    m = _TAG_RE.match(tag)
    if not m:
        return None
    nums = [int(n) for n in m.group(1).split(".")]
    nums += [0] * (3 - len(nums))
    suffix = m.group(2)
    # Une version finale est plus récente qu'une pre-release du même numéro
    return (tuple(nums), 1 if suffix is None else 0, suffix or "")


def _is_prerelease(tag):
    m = _TAG_RE.match(tag)
    return bool(m and m.group(2))


def get_local_version():
    return _git("describe", "--tags", "--abbrev=0")


def get_latest_remote_version():
    """Appel réseau (lent) : à ne jamais faire dans le thread principal."""
    out = _git("ls-remote", "--tags", "--refs", "origin")
    if not out:
        return None
    tags = [line.split("refs/tags/")[-1] for line in out.splitlines() if "refs/tags/" in line]
    tags = [t for t in tags if _version_key(t) is not None]
    if not INCLUDE_PRERELEASES:
        tags = [t for t in tags if not _is_prerelease(t)]
    return max(tags, key=_version_key) if tags else None


def _load_state():
    try:
        return json.loads(STATE_FILE.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}


def _update_state(**changes):
    """Lit, modifie et réécrit l'état (protégé contre les accès simultanés)."""
    with _lock:
        state = _load_state()
        state.update(changes)
        try:
            STATE_FILE.write_text(json.dumps(state, indent=2), encoding="utf-8")
        except OSError:
            pass  # pas grave si on ne peut pas sauvegarder


def _refresh_remote_version():
    """Corps du thread : interroge GitHub et mémorise le résultat."""
    latest = get_latest_remote_version()
    if latest:  # hors ligne -> on ne touche à rien, on réessaiera au prochain lancement
        _update_state(latest=latest, last_check=time.time())


def start_background_check(force=False):
    """Lance la vérification réseau en arrière-plan et rend la main immédiatement.

    Retourne le thread (ou None si une vérification récente existe déjà).
    """
    if not force and time.time() - _load_state().get("last_check", 0) < CHECK_INTERVAL:
        return None
    thread = threading.Thread(target=_refresh_remote_version, daemon=True)
    thread.start()
    return thread


def get_pending_update(ignore_declined=False):
    """Retourne (version_locale, dernier_tag) si une mise à jour est disponible, sinon None.

    Lecture locale uniquement : instantané. Pratique pour afficher une bannière
    dans le TUI sans passer par input().
    """
    state = _load_state()
    latest = state.get("latest")
    local = get_local_version()
    if not latest or not local:
        return None

    local_key, latest_key = _version_key(local), _version_key(latest)
    if not local_key or not latest_key or latest_key <= local_key:
        return None
    if not ignore_declined and state.get("declined") == latest:
        return None  # l'utilisateur a déjà refusé cette version
    return local, latest


def apply_update(tag):
    """Télécharge les tags et se place sur le tag demandé."""
    if _git("fetch", "--tags", timeout=30) is None:
        print("Échec du téléchargement des mises à jour.")
        return False
    if _git("checkout", tag, timeout=30) is None:
        print("Impossible de changer de version (modifications locales ?).")
        return False
    print(f"Mise à jour vers {tag} effectuée. Relance l'application.")
    return True


def prompt_for_update(ignore_declined=False):
    """Propose la mise à jour (y/n) si un tag plus récent est connu. Instantané."""
    pending = get_pending_update(ignore_declined=ignore_declined)
    if not pending:
        return False
    local, latest = pending

    answer = input(
        f"L'application peut être mise à jour ({local} -> {latest}). "
        "Mettre à jour ? (y/n) "
    ).strip().lower()

    if answer == "y":
        return apply_update(latest)

    _update_state(declined=latest)
    return False


if __name__ == "__main__":
    # Test manuel : force la vérification, attend le résultat, puis propose la mise à jour
    t = start_background_check(force=True)
    if t:
        t.join()
    prompt_for_update(ignore_declined=True)
