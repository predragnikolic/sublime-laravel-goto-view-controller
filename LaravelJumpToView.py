import sublime_plugin
from .core.Event import Event
from .core.Path import Path


class LaravelGotoViewController(sublime_plugin.TextCommand):
    def is_supported(self):
        supported_scopes = [
            "string.quoted.single.php",
            "string.quoted.double.php"
        ]

        # all scopes at the cursor position
        self.cursorPos = self.getCursorPos()
        scopes = self.getScopes()

        for supported_scope in supported_scopes:
            return True if supported_scope in scopes else False

    def run(self, edit):
        if not self.is_supported():
            self.view.run_command('lsp_symbol_definition')
            return

        text = self.getText()
        window = self.view.window()
        path = Path(self.view)

        if '@' in text:
            controller, method = text.split('@')

            filename = controller + '.php'

            window.open_file(path.for_controllers() + filename)
            Event.listen('view.on_load_async', lambda view:
                         self.show_at_center(view, method)
                         )

        elif 'controller' in text.lower():
            filename = text + '.php'
            window.open_file(path.for_controllers() + filename)

        else:
            filename = text + '.blade.php'
            window.open_file(path.for_views() + filename)

    def show_at_center(self, view, method):
        symbols = view.symbols()

        for region, symbol_method in symbols:
            if symbol_method == method:
                view.show_at_center(region.end())
                view.sel().clear()
                view.sel().add(region.end())

    def getCursorPos(self):
        return self._getFirstSelection().begin()

    def getScopes(self):
        return self.view.scope_name(self.cursorPos).split(' ')

    def getText(self):
        # expand to single or double quotes
        self._expandSelectionToQuotes()

        region = self._getFirstSelection()

        # extract the word from the region
        text = self.view.substr(region)

        self._clearSelection()
        return self._normalizeSelected(text)

    def _getFirstSelection(self):
        return self.view.sel()[0]

    def _expandSelectionToQuotes(self):
        window = self.view.window()
        window.run_command("expand_selection", {"to": "scope"})

    def _normalizeSelected(self, text):
        text = text.replace('.', '/')
        text = text.replace('\'', '').replace('"', '')
        text = text.replace(')', '').replace('(', '')
        return text

    def _clearSelection(self):
        self.view.sel().clear()
        self.view.sel().add(self.cursorPos)


class DocumentSyncListener(sublime_plugin.EventListener):
    def on_load_async(self, view):
        Event.fire("view.on_load_async", view)