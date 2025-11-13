import os
import subprocess
import json
from pathlib import Path
from dataclasses import dataclass
from typing import List, Tuple, Optional
from datetime import datetime

CONFIG_DIR = Path.home() / ".config" / "gitsnap"
CONFIG_FILE = CONFIG_DIR / "config.json"

@dataclass
class GitFile:
    """Represents a file with its git status."""
    status: str
    path: str

@dataclass
class GitSnapshot:
    """Represents a git tag snapshot."""
    tag: str
    message: str

# --- Config Functions ---

def _ensure_config_exists():
    """Ensures the config directory and file exist."""
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    if not CONFIG_FILE.is_file():
        CONFIG_FILE.write_text(json.dumps({"github_token": None}))

def save_token(token: str):
    """Saves the GitHub token to the config file."""
    _ensure_config_exists()
    with open(CONFIG_FILE, "r") as f:
        config = json.load(f)
    config["github_token"] = token
    with open(CONFIG_FILE, "w") as f:
        json.dump(config, f, indent=4)

def load_token() -> Optional[str]:
    """Loads the GitHub token from the config file."""
    if not CONFIG_FILE.is_file():
        return None
    with open(CONFIG_FILE, "r") as f:
        config = json.load(f)
    return config.get("github_token")

# --- Git Functions ---

def is_git_repo(path: str = ".") -> bool:
    """Checks if the given path is a git repository."""
    git_dir = os.path.join(path, ".git")
    return os.path.isdir(git_dir)

def git_init(path: str = "."):
    """Runs 'git init' in the specified path."""
    try:
        subprocess.run(["git", "init"], cwd=path, check=True, capture_output=True, text=True)
        return True, "Repositório Git inicializado com sucesso."
    except (FileNotFoundError, subprocess.CalledProcessError) as e:
        return False, f"Erro ao inicializar repositório: {e}"

def get_git_status(path: str = ".") -> List[GitFile]:
    """Gets the git status and returns a list of GitFile objects."""
    if not is_git_repo(path): return []
    result = subprocess.run(["git", "status", "--porcelain"], cwd=path, check=True, capture_output=True, text=True)
    files = [GitFile(status=line[:2], path=line[3:]) for line in result.stdout.strip().split('\n') if line]
    return files

def get_remote_url(path: str = ".") -> Optional[str]:
    """Gets the URL of the 'origin' remote."""
    try:
        return subprocess.run(
            ["git", "remote", "get-url", "origin"],
            cwd=path, check=True, capture_output=True, text=True
        ).stdout.strip()
    except (subprocess.CalledProcessError, FileNotFoundError):
        return None

def get_current_branch_name(path: str = ".") -> Optional[str]:
    """Gets the current active branch name."""
    try:
        return subprocess.run(
            ["git", "branch", "--show-current"],
            cwd=path, check=True, capture_output=True, text=True
        ).stdout.strip()
    except (subprocess.CalledProcessError, FileNotFoundError):
        return None

def git_push(path: str = ".") -> Tuple[bool, str]:
    """Pushes commits and tags to the remote repository."""
    remote_url = get_remote_url(path)
    if not remote_url:
        return True, " (Nenhum repositório remoto configurado para fazer push)"

    token = load_token()
    if not token:
        return False, " (Snapshot salvo localmente, mas o login no GitHub não está configurado)"

    current_branch = get_current_branch_name(path)
    if not current_branch:
        return False, " (Não foi possível determinar o ramo atual para fazer push)"

    try:
        env = os.environ.copy()
        env['GIT_TERMINAL_PROMPT'] = '0'
        timeout_seconds = 15

        if remote_url.startswith("https://"):
            auth_url = remote_url.replace("https://", f"https://{token}@")
            subprocess.run(["git", "push", auth_url, current_branch], cwd=path, check=True, capture_output=True, env=env, timeout=timeout_seconds)
            subprocess.run(["git", "push", auth_url, "--tags"], cwd=path, check=True, capture_output=True, env=env, timeout=timeout_seconds)
        else: # Assume SSH
            subprocess.run(["git", "push", "origin", current_branch], cwd=path, check=True, capture_output=True, env=env, timeout=timeout_seconds)
            subprocess.run(["git", "push", "origin", "--tags"], cwd=path, check=True, capture_output=True, env=env, timeout=timeout_seconds)
        
        return True, "Sincronização com o GitHub concluída com sucesso!"
    except subprocess.TimeoutExpired:
        return False, "Erro: O push para o GitHub demorou demasiado tempo"
    except FileNotFoundError:
        return False, "Erro: O comando 'git' não foi encontrado"
    except subprocess.CalledProcessError as e:
        error_output = e.stderr.decode().strip()
        return False, f"Erro do Git ao fazer push: {error_output}"

def create_snapshot(message: str, path: str = ".") -> Tuple[bool, str]:
    """Creates a new local snapshot."""
    if not message:
        return False, "A mensagem do snapshot não pode estar vazia."
    try:
        subprocess.run(["git", "add", "."], cwd=path, check=True, capture_output=True)
        subprocess.run(["git", "commit", "-m", message], cwd=path, check=True, capture_output=True)
        timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        tag_name = f"snapshot-{timestamp}"
        subprocess.run(["git", "tag", "-a", tag_name, "-m", message], cwd=path, check=True)
        
        return True, f"Snapshot '{tag_name}' criado com sucesso localmente."
    except subprocess.CalledProcessError as e:
        output = e.stdout.decode() or e.stderr.decode()
        if "nothing to commit" in output:
            return False, "Não há alterações para salvar num snapshot."
        return False, f"Erro ao criar snapshot: {output}"
    except FileNotFoundError:
        return False, "Erro: O comando 'git' não foi encontrado."

def list_snapshots(path: str = ".") -> List[GitSnapshot]:
    """Lists all snapshots (annotated tags)."""
    if not is_git_repo(path): return []
    try:
        result = subprocess.run(["git", "tag", "-l", "snapshot-*", "--sort=-creatordate"], cwd=path, check=True, capture_output=True, text=True)
        tags = result.stdout.strip().split('\n')
        if not tags or not tags[0]: return []
        snapshots = [GitSnapshot(tag=tag, message=subprocess.run(["git", "tag", "-n1", tag], cwd=path, check=True, capture_output=True, text=True).stdout.strip().split(None, 1)[1]) for tag in tags]
        return snapshots
    except (subprocess.CalledProcessError, FileNotFoundError):
        return []

def get_snapshots_to_push(path: str = ".") -> Tuple[Optional[List[GitSnapshot]], str]:
    """Fetches from remote and lists local snapshots that are not in the remote branch."""
    if not get_remote_url(path):
        return None, "Nenhum repositório remoto 'origin' configurado."

    current_branch = get_current_branch_name(path)
    if not current_branch:
        return None, "Não foi possível determinar o ramo atual."
    
    try:
        # Fetch latest data from remote
        subprocess.run(["git", "fetch", "origin"], cwd=path, check=True, capture_output=True, text=True, timeout=15)

        # Check if the remote branch exists. If not, it's the first push.
        remote_branches = subprocess.run(["git", "branch", "-r"], cwd=path, check=True, capture_output=True, text=True).stdout
        if f"origin/{current_branch}" not in remote_branches:
            return list_snapshots(path), "Este parece ser o primeiro push. Todos os snapshots locais serão enviados."

        # If remote branch exists, compare to find commits to push
        log_command = ["git", "log", f"origin/{current_branch}..{current_branch}", "--pretty=format:%H"]
        result = subprocess.run(log_command, cwd=path, check=True, capture_output=True, text=True)
        commit_hashes = [h for h in result.stdout.strip().split('\n') if h]
        
        if not commit_hashes:
            return [], "O seu repositório local já está sincronizado com o GitHub."

        all_snapshots = list_snapshots(path)
        snapshots_to_push = []
        for snapshot in all_snapshots:
            tag_commit_hash = subprocess.run(["git", "rev-parse", f"{snapshot.tag}^{{commit}}"], cwd=path, check=True, capture_output=True, text=True).stdout.strip()
            if tag_commit_hash in commit_hashes:
                snapshots_to_push.append(snapshot)
        
        return snapshots_to_push, "Snapshots para enviar:"

    except subprocess.TimeoutExpired:
        return None, "Erro: O fetch do GitHub demorou demasiado tempo."
    except (subprocess.CalledProcessError, FileNotFoundError) as e:
        return None, f"Erro do Git ao verificar o repositório: {e.stderr.strip() if hasattr(e, 'stderr') else e}"


def rename_snapshot(tag: str, new_message: str, path: str = ".") -> Tuple[bool, str]:
    """Renames a local snapshot's message by force-updating the tag."""
    if not new_message:
        return False, "A nova mensagem não pode estar vazia."
    try:
        subprocess.run(["git", "tag", "-a", tag, "-f", "-m", new_message], cwd=path, check=True, capture_output=True)
        return True, f"Snapshot '{tag}' renomeado com sucesso."
    except (subprocess.CalledProcessError, FileNotFoundError) as e:
        return False, f"Erro ao renomear o snapshot '{tag}': {e}"

def delete_snapshot(tag: str, path: str = ".") -> Tuple[bool, str]:
    """Deletes a local snapshot (tag)."""
    try:
        subprocess.run(["git", "tag", "-d", tag], cwd=path, check=True, capture_output=True)
        return True, f"Snapshot '{tag}' eliminado com sucesso."
    except (subprocess.CalledProcessError, FileNotFoundError) as e:
        return False, f"Erro ao eliminar o snapshot '{tag}': {e}"

def restore_snapshot(tag: str, path: str = ".") -> Tuple[bool, str]:
    """Restores the repository to a given snapshot tag."""
    try:
        timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        backup_branch_name = f"backup-before-restore-{timestamp}"
        subprocess.run(["git", "branch", backup_branch_name], cwd=path, check=True)
        subprocess.run(["git", "reset", "--hard", tag], cwd=path, check=True, capture_output=True)
        return True, f"Snapshot '{tag}' restaurado com sucesso."
    except (subprocess.CalledProcessError, FileNotFoundError) as e:
        return False, f"Erro ao restaurar snapshot: {e}"

def discard_all_changes(path: str = ".") -> Tuple[bool, str]:
    """Discards all changes in the working directory."""
    try:
        subprocess.run(["git", "reset", "--hard", "HEAD"], cwd=path, check=True, capture_output=True)
        subprocess.run(["git", "clean", "-fd"], cwd=path, check=True, capture_output=True)
        return True, "Todas as alterações foram descartadas."
    except (subprocess.CalledProcessError, FileNotFoundError) as e:
        return False, f"Erro ao descartar alterações: {e}"

def get_current_snapshot_tag(path: str = ".") -> Optional[str]:
    """Gets the tag of the current HEAD, if it's a snapshot."""
    try:
        result = subprocess.run(["git", "describe", "--tags", "--exact-match", "HEAD"], cwd=path, check=True, capture_output=True, text=True)
        tag = result.stdout.strip()
        if tag.startswith("snapshot-"):
            return tag
        return None
    except (subprocess.CalledProcessError, FileNotFoundError):
        return None