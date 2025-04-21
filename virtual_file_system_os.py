import tkinter as tk

class VirtualFileSystem:
    def __init__(self):
        self.root = {}
        self.current_path = []

    def get_current_dir(self):
        current_dir = self.root
        for folder in self.current_path:
            current_dir = current_dir.get(folder, {})
        return current_dir

    def create_item(self, name, content, item_type, path):
        current_dir = self.root
        for folder in path:
            current_dir = current_dir.get(folder, {})

        if item_type == "file":
            current_dir[name] = {"type": "file", "content": content}
        elif item_type == "folder":
            current_dir[name] = {"type": "folder", "content": {}}

    def remove_item(self, name):
        current_dir = self.get_current_dir()
        if name in current_dir:
            del current_dir[name]
        else:
            print(f"Error: '{name}' not found.")

    def open_file(self, path):
        current_dir = self.get_current_dir()
        item = current_dir.get(path[-1])
        if item and item['type'] == 'file':
            return item['content']
        return "Error: File not found"

    def edit_file(self, path, new_content):
        current_dir = self.get_current_dir()
        item = current_dir.get(path[-1])
        if item and item['type'] == 'file':
            item['content'] = new_content
            return f"File '{path[-1]}' edited successfully."
        return "Error: File not found"

    def move_item(self, source, destination):
        current_dir = self.get_current_dir()

        if source not in current_dir:
            print(f"Error: Source item '{source}' not found.")
            return

        if destination in current_dir:
            print(f"Error: Destination item '{destination}' already exists.")
            return

        item = current_dir.pop(source)
        current_dir[destination] = item
        print(f"Item '{source}' moved/renamed to '{destination}'.")

    def copy_item(self, source, destination):
        current_dir = self.get_current_dir()

        if source not in current_dir:
            print(f"Error: Source item '{source}' not found.")
            return

        item = current_dir[source]
        current_dir[destination] = item
        print(f"Item '{source}' copied to '{destination}'.")

    def rename_item(self, old_name, new_name):
        current_dir = self.get_current_dir()
        if old_name in current_dir:
            current_dir[new_name] = current_dir.pop(old_name)
            print(f"Renamed '{old_name}' to '{new_name}'.")
        else:
            print(f"Error: '{old_name}' not found.")

    def rmdir(self, folder_name):
        current_dir = self.get_current_dir()
        if folder_name in current_dir and current_dir[folder_name]["type"] == "folder" and not current_dir[folder_name]["content"]:
            del current_dir[folder_name]
            print(f"Folder '{folder_name}' removed.")
        else:
            print(f"Error: Folder '{folder_name}' is not empty or does not exist.")

    def cat(self, file_name):
        current_dir = self.get_current_dir()
        item = current_dir.get(file_name)
        if item and item['type'] == 'file':
            return item['content']
        return "Error: File not found"


class TerminalApp:
    def __init__(self, root):
        self.vfs = VirtualFileSystem()
        self.root = root
        self.terminal_frame = tk.Frame(self.root, bg="black")
        self.terminal_frame.pack()

        self.output = tk.Text(self.terminal_frame, height=20, width=80, bg="black", fg="white", font=("Courier", 12))
        self.output.pack()

        # Creating the input field with a blinking cursor
        self.input_field = tk.Entry(self.terminal_frame, width=80, bg="black", fg="white", font=("Courier", 12), insertbackground="white")
        self.input_field.pack()
        self.input_field.bind("<Return>", self.execute_command)
        self.input_field.bind("<Tab>", self.autocomplete)

        self.command_history = []
        self.current_command_index = -1

        # Define list of valid commands for autocomplete
        self.commands = [
            "help", "mkdir", "touch", "ls", "cd", "pwd", "rm", "open", "edit", 
            "mv", "cp", "rename", "rmdir", "cat", "clear", "detail"
        ]

        # Show the welcome message
        self.show_welcome_message()

    def print_to_terminal(self, text):
        self.output.insert(tk.END, text + '\n')
        self.output.yview(tk.END)

    def show_welcome_message(self):
        welcome_text = """Welcome to the Virtual File System!
Type 'help' to get started with available commands.
"""
        self.print_to_terminal(welcome_text)

    def execute_command(self, event=None):
        command = self.input_field.get()
        if command.strip():
            self.print_to_terminal(f"$ {command}")  # Shows entered command
            self.command_history.append(command)
            self.current_command_index = len(self.command_history)

            self.process_command(command)
            self.input_field.delete(0, tk.END)  # Clear the input field after command is entered

    def process_command(self, command):
        parts = command.split()

        if parts[0] == "help":
            self.print_to_terminal(
                """Commands:
                - ls : List items in the current directory
                - mkdir <name>: Create a folder
                - touch <name>: Create a file
                - rm <name>: Delete a file or folder
                - cd <name>: Change the current directory
                - pwd : Print current directory path
                - open <file_name>: Open a file and view its contents
                - edit <file_name>: Edit a file's content
                - mv <source> <destination>: Move or rename a file/folder
                - cp <source> <destination>: Copy a file/folder
                - clear : Clear the terminal screen
                - cat <file_name>: Display the contents of a file
                - rename <old_name> <new_name>: Rename a file or folder
                - rmdir <folder_name>: Remove an empty folder
                - help : Show this help message
                - detail <command>: Show detailed information about a command"""
            )
        elif parts[0] == "detail":
            if len(parts) > 1:
                self.show_command_detail(parts[1])
            else:
                self.print_to_terminal("Error: 'detail' requires a command name.")
        elif parts[0] == "mkdir":
            self.vfs.create_item(parts[1], "", "folder", self.vfs.current_path)
            self.print_to_terminal(f"Folder '{parts[1]}' created.")
        elif parts[0] == "touch":
            self.vfs.create_item(parts[1], "This is a new file.", "file", self.vfs.current_path)
            self.print_to_terminal(f"File '{parts[1]}' created.")
        elif parts[0] == "ls":
            current_dir = self.vfs.get_current_dir()
            items = "\n".join(current_dir.keys())
            self.print_to_terminal(f"Items in the current directory:\n{items}")
        elif parts[0] == "cd":
            if parts[1] in self.vfs.get_current_dir():
                self.vfs.current_path.append(parts[1])
                self.print_to_terminal(f"Changed directory to '{'/'.join(self.vfs.current_path)}'.")
            else:
                self.print_to_terminal(f"Error: Directory '{parts[1]}' not found.")
        elif parts[0] == "pwd":
            self.print_to_terminal(f"Current directory: {'/'.join(self.vfs.current_path) if self.vfs.current_path else '/'}")
        elif parts[0] == "rm":
            self.vfs.remove_item(parts[1])
            self.print_to_terminal(f"Item '{parts[1]}' deleted.")
        elif parts[0] == "open":
            content = self.vfs.open_file(self.vfs.current_path + [parts[1]])
            self.print_to_terminal(f"File content:\n{content}")
        elif parts[0] == "edit":
            content = self.vfs.open_file(self.vfs.current_path + [parts[1]])
            self.print_to_terminal(f"Editing file '{parts[1]}'. Current content:\n{content}")
            new_content = input("Enter new content: ")
            result = self.vfs.edit_file(self.vfs.current_path + [parts[1]], new_content)
            self.print_to_terminal(result)
        elif parts[0] == "mv":
            if len(parts) < 3:
                self.print_to_terminal("Error: 'mv' command requires a source and a destination.")
            else:
                self.vfs.move_item(parts[1], parts[2])
        elif parts[0] == "cp":
            if len(parts) < 3:
                self.print_to_terminal("Error: 'cp' command requires a source and a destination.")
            else:
                self.vfs.copy_item(parts[1], parts[2])
        elif parts[0] == "rename":
            if len(parts) < 3:
                self.print_to_terminal("Error: 'rename' command requires an old and new name.")
            else:
                self.vfs.rename_item(parts[1], parts[2])
        elif parts[0] == "rmdir":
            self.vfs.rmdir(parts[1])
        elif parts[0] == "cat":
            content = self.vfs.cat(parts[1])
            self.print_to_terminal(content)
        elif parts[0] == "clear":
            self.output.delete(1.0, tk.END)
        else:
            self.print_to_terminal(f"Unknown command: {parts[0]}")

    def show_command_detail(self, command):
        details = {
            "mkdir":  "Usage: mkdir <folder_name>\n"
                "The 'mkdir' command creates a new directory (folder) in the current directory.\n"
                "The folder name is specified after the 'mkdir' keyword.\n"
                "Example:\n"
                "  mkdir new_folder\n"
                "This will create a new directory named 'new_folder' in the current path.\n",
            "touch":  "Usage: touch <file_name>\n"
                "The 'touch' command is used to create an empty file with the specified name.\n"
                "If the file already exists, the 'touch' command will update its timestamp.\n"
                "Example:\n"
                "  touch my_file.txt\n"
                "This will create a new empty file named 'my_file.txt' in the current directory.\n",
            "ls":  "Usage: ls\n"
                "The 'ls' command lists all files and directories in the current directory.\n"
                "It can be used to view the contents of the directory you are currently in.\n"
                "Example:\n"
                "  ls\n"
                "Output:\n"
                "  file1.txt\n"
                "  folder1\n"
                "  file2.txt\n",
            "cd": "Usage: cd <directory_name>\n"
                "The 'cd' command changes the current working directory.\n"
                "You can navigate through directories by specifying the directory name.\n"
                "Example:\n"
                "  cd my_folder\n"
                "This will change the current directory to 'my_folder'. If the directory doesn't exist, an error will be shown.\n",
            "pwd":  "Usage: pwd\n"
                "The 'pwd' command prints the full path of the current working directory.\n"
                "This is useful to know your exact location in the file system.\n"
                "Example:\n"
                "  pwd\n"
                "Output:\n"
                "  /home/user/my_folder\n",
            "rm": "Usage: rm <file_name> or rm -r <folder_name>\n"
                "The 'rm' command is used to delete files or directories.\n"
                "To delete a file, simply specify the file name after 'rm'. To delete a directory, use the '-r' flag.\n"
                "Example:\n"
                "  rm my_file.txt\n"
                "This will remove the file named 'my_file.txt' from the current directory.\n"
                "To remove a folder, use the following:\n"
                "  rm -r my_folder\n"
                "This will remove 'my_folder' and its contents.\n",
            "open": "Usage: open <file_name>\n"
                "The 'open' command is used to open a file and display its content.\n"
                "It is used for reading the contents of a file in the current directory.\n"
                "Example:\n"
                "  open my_file.txt\n"
                "This will open the file 'my_file.txt' and display its contents.\n",
            "edit": "Usage: edit <file_name>\n"
                "The 'edit' command opens a file for editing.\n"
                "It allows you to modify the contents of a file.\n"
                "Example:\n"
                "  edit my_file.txt\n"
                "This will allow you to edit the contents of 'my_file.txt'. After editing, the changes will be saved.\n",
            "mv":  "Usage: mv <source> <destination>\n"
                "The 'mv' command is used to move or rename files and directories.\n"
                "If the destination is an existing directory, the item is moved into that directory. If the destination is a new name, it renames the file or folder.\n"
                "Example:\n"
                "  mv my_file.txt new_folder/\n"
                "This will move 'my_file.txt' into the 'new_folder' directory.\n"
                "To rename a file, you can use:\n"
                "  mv old_name.txt new_name.txt\n",
            "cp": "Usage: cp <source> <destination>\n"
                "The 'cp' command is used to copy files and directories.\n"
                "You can copy a file or folder from one location to another.\n"
                "Example:\n"
                "  cp my_file.txt new_folder/\n"
                "This will copy 'my_file.txt' into the 'new_folder' directory.\n"
                "To copy a file with a new name:\n"
                "  cp old_file.txt new_file.txt\n",
            "rename": "Usage: rename <old_name> <new_name>\n"
                "The 'rename' command is used to rename a file or folder.\n"
                "You must specify both the old name and the new name.\n"
                "Example:\n"
                "  rename old_name.txt new_name.txt\n"
                "This will rename 'old_name.txt' to 'new_name.txt'.\n",
            "rmdir": "Usage: rmdir <folder_name>\n"
                "The 'rmdir' command is used to remove an empty folder.\n"
                "The folder must be empty for the command to succeed.\n"
                "Example:\n"
                "  rmdir empty_folder\n"
                "This will remove the folder 'empty_folder'.\n"
                "If the folder contains files or other folders, the command will fail.\n",
            "cat":  "Usage: cat <file_name>\n"
                "The 'cat' command is used to display the contents of a file.\n"
                "It prints the file's content to the terminal, which is helpful for viewing text files.\n"
                "Example:\n"
                "  cat my_file.txt\n"
                "This will display the contents of 'my_file.txt'.\n",
            "clear": "Clears the terminal screen.",
            "help": "Shows the available commands."
        }
        if command in details:
            self.print_to_terminal(f"Details for '{command}': {details[command]}")
        else:
            self.print_to_terminal(f"Error: No details found for command '{command}'.")
            
    def autocomplete(self, event):
        typed = self.input_field.get()
        suggestions = [cmd for cmd in self.commands if cmd.startswith(typed)]
        if suggestions:
            self.input_field.delete(0, tk.END)
            self.input_field.insert(0, suggestions[0])
        return "break"

if __name__ == "__main__":
    root = tk.Tk()
    app = TerminalApp(root)
    root.mainloop()
