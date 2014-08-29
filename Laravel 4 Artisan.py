import os
import shlex
import subprocess
import sublime
import sublime_plugin

class Laravel4ArtisanCommand(sublime_plugin.WindowCommand):
    def __init__(self, *args, **kwargs):
        super(Laravel4ArtisanCommand, self).__init__(*args, **kwargs)
        settings = sublime.load_settings('Laravel 4 Artisan.sublime-settings')
        self.php_path = settings.get('php_path')
        self.artisan_path = settings.get('artisan_path')

    def run(self, *args, **kwargs):
        try:
            # The first folder needs to be the Laravel Project
            self.PROJECT_PATH = self.window.folders()[0]
            artisan_path = os.path.join(self.PROJECT_PATH, self.artisan_path)
            self.args = [self.php_path, artisan_path]

            if os.path.isfile("%s" % artisan_path):
                self.command = kwargs.get('command', None)
                if self.command == 'serveStop':
                    self.command = 'taskkill /F /IM php.exe'
                    self.args = []
                else:
                    self.args = [self.php_path, artisan_path]
                self.fill_in_accept = kwargs.get('fill_in', False)
                self.fill_in_label = kwargs.get('fill_in_lable', 'Enter the resource name')
                self.fields_accept = kwargs.get('fields', False)
                self.fields_label = kwargs.get('fields_label', 'Enter the fields')
                if self.command is None:
                    self.window.show_input_panel('Command name w/o args:', '', self.on_command_custom, None, None)
                else:
                    self.on_command(self.command)
            else:
                sublime.status_message("Artisan not found")
        except IndexError:
            sublime.status_message("Please open a Laravel Project")

    def on_command(self, command):
        self.args.extend(shlex.split(str(self.command)))

        if self.fill_in_accept is True:
            sublime.status_message(self.fill_in_label);
            if self.fill_in_label == 'Enter the port':
                self.window.show_input_panel(self.fill_in_label, "8000", self.on_fill_in, None, None)
            else:
                self.window.show_input_panel(self.fill_in_label, "", self.on_fill_in, None, None)
        else:
            self.on_done()

    def on_fill_in(self, fill_in):
        if self.fill_in_label == 'Enter the port':
            fill_in = "--port=" + fill_in
        self.args.extend(shlex.split(str(fill_in)))

        if self.fields_accept is True:
            self.window.show_input_panel(self.fields_label, "", self.on_fields, None, None)
        else:
            self.on_done()

    def on_fields(self, fields):
        if fields != '':
            self.args.append('--fields=')
            self.args.append(fields)
            self.on_done()
        else:
            self.on_done()

    def on_command_custom(self, command):
        self.args.extend(shlex.split(str(command)))
        self.on_done()

    def on_done(self):
        if os.name != 'posix':
            self.args = subprocess.list2cmdline(self.args)
        try:
            self.window.run_command("exec", {
                "cmd": self.args,
                "shell": os.name == 'nt',
                "working_dir": self.PROJECT_PATH})
        except IOError:
            sublime.status_message('IOError - command aborted')
