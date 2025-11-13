from textual.app import App, ComposeResult
from textual.screen import Screen, ModalScreen
from textual.widgets import Header, Footer, Static, Button, Label, Input, DataTable
from textual.containers import Container, Grid, Horizontal

from .git_utils import (
    is_git_repo, git_init, get_git_status, create_snapshot, 
    list_snapshots, restore_snapshot, discard_all_changes, get_current_snapshot_tag,
    get_snapshots_to_push, git_push, delete_snapshot, rename_snapshot
)

# --- Modal Screens ---

class ConfirmDiscardScreen(ModalScreen[bool]):
    """Screen to confirm discarding all changes."""
    def compose(self) -> ComposeResult:
        yield Grid(
            Label("Tem a certeza que quer descartar TODAS as alterações?\nEsta ação não pode ser desfeita.", id="question"),
            Button("Cancelar", variant="default", id="cancel"),
            Button("Descartar", variant="error", id="discard"),
            id="dialog",
        )
    def on_button_pressed(self, event: Button.Pressed) -> None:
        self.dismiss(event.button.id == "discard")

class ConfirmRestoreScreen(ModalScreen[bool]):
    """Screen to confirm snapshot restoration."""
    def __init__(self, tag: str) -> None:
        self.tag = tag
        super().__init__()
    def compose(self) -> ComposeResult:
        yield Grid(
            Label(f"Tem a certeza que quer restaurar o snapshot '{self.tag}'?\nTodas as alterações não salvas serão perdidas.", id="question"),
            Button("Cancelar", variant="default", id="cancel"),
            Button("Restaurar", variant="error", id="restore"),
            id="dialog",
        )
    def on_button_pressed(self, event: Button.Pressed) -> None:
        self.dismiss(event.button.id == "restore")

class ConfirmDeleteScreen(ModalScreen[bool]):
    """Screen to confirm snapshot deletion."""
    def __init__(self, tag: str) -> None:
        self.tag = tag
        super().__init__()
    def compose(self) -> ComposeResult:
        yield Grid(
            Label(f"Tem a certeza que quer eliminar o snapshot '{self.tag}'?\nEsta ação não pode ser desfeita.", id="question"),
            Button("Cancelar", variant="default", id="cancel"),
            Button("Eliminar", variant="error", id="delete"),
            id="dialog",
        )
    def on_button_pressed(self, event: Button.Pressed) -> None:
        self.dismiss(event.button.id == "delete")

class RenameSnapshotScreen(ModalScreen[str]):
    """A modal screen to rename a snapshot."""
    def __init__(self, current_message: str) -> None:
        self.current_message = current_message
        super().__init__()

    def compose(self) -> ComposeResult:
        yield Grid(
            Label("Renomear mensagem do snapshot:"),
            Input(value=self.current_message, id="rename_input"),
            Button("Cancelar", variant="default", id="cancel"),
            Button("Renomear", variant="primary", id="rename"),
            id="dialog",
        )

    def on_mount(self) -> None:
        self.query_one(Input).focus()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "rename":
            new_message = self.query_one(Input).value
            self.dismiss(new_message)
        else:
            self.dismiss()

# --- Main Screens ---

class SnapshotListScreen(Screen):
    """Screen to display a list of snapshots."""
    BINDINGS = [
        ("escape", "app.pop_screen", "Voltar"),
        ("d", "delete_snapshot", "Eliminar"),
        ("r", "rename_snapshot", "Renomear"),
    ]

    def compose(self) -> ComposeResult:
        yield Header()
        yield Footer()
        yield Label("Lista de Snapshots Salvos. [d] eliminar, [r] renomear, [enter] restaurar.")
        yield DataTable(id="snapshot_table")

    def on_mount(self) -> None:
        self.refresh_table()

    def refresh_table(self) -> None:
        table = self.query_one(DataTable)
        table.clear()
        if not table.columns:
            table.add_columns("Snapshot (Tag)", "Mensagem")
        table.cursor_type = "row"
        
        active_tag = get_current_snapshot_tag()
        snapshots = list_snapshots()
        if snapshots:
            for snapshot in snapshots:
                is_active = snapshot.tag == active_tag
                display_tag = f"* {snapshot.tag}" if is_active else f"  {snapshot.tag}"
                row = table.add_row(display_tag, snapshot.message, key=snapshot.tag)
                if is_active:
                    row.emphasis = "primary"
        else:
            table.add_row("Nenhum", "Nenhum snapshot encontrado.")

    def on_data_table_row_selected(self, event: DataTable.RowSelected) -> None:
        tag_to_restore = event.row_key.value
        if tag_to_restore:
            def handle_confirmation(confirmed: bool) -> None:
                if confirmed:
                    self.dismiss(restore_snapshot(tag_to_restore))
            self.app.push_screen(ConfirmRestoreScreen(tag=tag_to_restore), handle_confirmation)

    def action_delete_snapshot(self) -> None:
        table = self.query_one(DataTable)
        if not table.row_count or table.cursor_row < 0: return
        
        row_data = table.get_row_at(table.cursor_row)
        tag_to_delete = row_data[0].strip().replace("* ", "")

        def handle_confirmation(confirmed: bool) -> None:
            if confirmed:
                success, message = delete_snapshot(tag_to_delete)
                self.notify(message, severity="information" if success else "error")
                self.refresh_table()
        
        self.app.push_screen(ConfirmDeleteScreen(tag=tag_to_delete), handle_confirmation)

    def action_rename_snapshot(self) -> None:
        table = self.query_one(DataTable)
        if not table.row_count or table.cursor_row < 0: return

        row_data = table.get_row_at(table.cursor_row)
        tag_to_rename = row_data[0].strip().replace("* ", "")
        current_message = row_data[1]

        def handle_rename(new_message: str) -> None:
            if new_message:
                success, message = rename_snapshot(tag_to_rename, new_message)
                self.notify(message, severity="information" if success else "error")
                self.refresh_table()

        self.app.push_screen(RenameSnapshotScreen(current_message), handle_rename)


class SyncScreen(Screen):
    """Screen for syncing with GitHub."""
    BINDINGS = [("escape", "app.pop_screen", "Voltar")]

    def compose(self) -> ComposeResult:
        yield Header()
        yield Footer()
        yield Label("A sincronizar com o GitHub...", id="sync_status_label")
        yield DataTable(id="sync_table")
        yield Horizontal(
            Button("Fazer Push para o GitHub", variant="primary", id="push_button", disabled=True),
            id="sync_buttons"
        )

    def on_mount(self) -> None:
        """Fetch remote status and populate the table."""
        table = self.query_one(DataTable)
        table.add_columns("Snapshot (Tag)", "Mensagem")
        
        snapshots, message = get_snapshots_to_push()
        status_label = self.query_one("#sync_status_label", Label)
        status_label.update(message)

        if snapshots is not None:
            if snapshots:
                self.query_one("#push_button").disabled = False
                for snapshot in snapshots:
                    table.add_row(snapshot.tag, snapshot.message)
            else:
                table.add_row("✅", "Tudo sincronizado.")
        else:
            # An error occurred, snapshots is None
            table.add_row("❌", "Não foi possível verificar o estado.")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "push_button":
            event.button.disabled = True
            status_label = self.query_one("#sync_status_label", Label)
            status_label.update("A fazer push...")
            
            success, message = git_push()
            self.notify(message, severity="information" if success else "error")
            if success:
                self.app.pop_screen()

class MainScreen(Screen):
    """The main screen of the application."""
    BINDINGS = [("r", "refresh_screen", "Refresh")]

    def compose(self) -> ComposeResult:
        yield Header()
        yield Footer()
        yield Container(id="main_container")

    def on_mount(self) -> None:
        self.action_refresh_screen()

    def handle_restore_result(self, result: tuple) -> None:
        if not result: return
        success, message = result
        self.notify(message, severity="information" if success else "error")
        if success:
            self.action_refresh_screen()

    def action_refresh_screen(self) -> None:
        main_container = self.query_one("#main_container")
        main_container.remove_children()
        if is_git_repo():
            changed_files = get_git_status()
            if not changed_files:
                main_container.mount(Label("✅ Repositório limpo. Não há alterações para salvar."))
                main_container.mount(Button("Ver e Restaurar Snapshots", id="list_snapshots_button"))
                main_container.mount(Button("Sincronizar com GitHub", id="sync_button"))
            else:
                main_container.mount(Label("Ficheiros modificados ou novos:"))
                for file in changed_files:
                    main_container.mount(Label(f"[b]{file.status}[/b] {file.path}"))
                main_container.mount(Input(placeholder="Descrição do seu snapshot...", id="snapshot_message"))
                button_container = Horizontal()
                button_container.mount(Button("Salvar Snapshot", variant="success", id="save_button"))
                button_container.mount(Button("Descartar Alterações", variant="error", id="discard_button"))
                main_container.mount(button_container)
        else:
            main_container.mount(Static("Esta pasta não é um repositório Git.\nDeseja inicializar um novo repositório aqui?"))
            main_container.mount(Button("Inicializar Repositório", variant="primary", id="init_button"))

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "init_button":
            success, message = git_init()
            self.notify(message)
            if success: self.action_refresh_screen()
        elif event.button.id == "save_button":
            message_input = self.query_one("#snapshot_message", Input)
            message = message_input.value
            if not message:
                self.notify("Por favor, escreva uma descrição para o snapshot.", severity="error"); return
            success, result_message = create_snapshot(message)
            self.notify(result_message, severity="information" if success else "error")
            if success: self.action_refresh_screen()
        elif event.button.id == "list_snapshots_button":
            self.app.push_screen(SnapshotListScreen(), self.handle_restore_result)
        elif event.button.id == "sync_button":
            self.app.push_screen(SyncScreen())
        elif event.button.id == "discard_button":
            def handle_discard(confirmed: bool) -> None:
                if confirmed:
                    success, message = discard_all_changes()
                    self.notify(message, severity="information" if success else "error")
                    if success:
                        self.action_refresh_screen()
            self.app.push_screen(ConfirmDiscardScreen(), handle_discard)

class GitSnapApp(App[None]):
    """A Textual app to manage git snapshots."""
    BINDINGS = [("d", "toggle_dark", "Toggle dark mode")]
    CSS_PATH = "main.css"

    def on_mount(self) -> None:
        self.push_screen(MainScreen())

    def action_toggle_dark(self) -> None:
        self.dark = not self.dark

def run():
    app = GitSnapApp()
    app.run()

if __name__ == "__main__":
    run()