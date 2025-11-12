import os
import socket
from readchar import readkey, key
from tabulate import tabulate

class Colors:
    BRIGHT_GREEN = "\033[92m"
    GREEN = "\033[32m"
    RESET = "\033[0m"

def require_connection(func):
    """Decorator to ensure a client connection is established before running the function."""
    def wrapper(self, *args, **kwargs):
        if not self.ensure_client_connection():
            return ""
        return func(self, *args, **kwargs)
    return wrapper

class EC2Instance:
    def __init__(self, server_ip):
        self.server_ip = server_ip
        self.client_socket = None
        self.current_client_id = None
        self.client_mapping = {}  # Mapping of CLIENT_ID -> PORT

    def ensure_client_connection(self):
        """Ensure a client connection is established."""
        if not self.client_socket:
            print("\033[91m⚠️  No client connection established.\033[0m")
            print("\033[37mUse <lscl> to view and connect to a client.\033[0m")
            return False
        return True

    def create_tmp(self, client_name, port):
        """Create or update the local /tmp/{user}.connected file."""
        identification = f"{client_name}:{port}"
        connected_file = f"/tmp/{client_name}.connected"
        try:
            if os.path.exists(connected_file):
                os.remove(connected_file)  # Remove if file exists
            with open(connected_file, "w") as f:
                f.write(identification)
            #print(f"{connected_file} with '{client_name}:{port}'")
        except Exception as e:
            print(f"Error creating or updating local file: {e}")

    def list_connected_clients(self):
        """List connected clients by reading registration files."""
        client_dir = "/tmp"
        self.client_mapping = {}

        try:
            for file in os.listdir(client_dir):
                if file.endswith(".connected"):
                    with open(os.path.join(client_dir, file), "r") as f:
                        client_id, port = f.read().strip().split(":")
                        self.client_mapping[client_id] = int(port)
        except Exception as e:
            print(f"Error reading connected clients: {e}")

        if not self.client_mapping:
            print("No clients are currently connected.")
            return False
        else:
            print("\nConnected Clients:")
            headers = ["#", "Client ID", "Port"]
            data = [
                (idx, f"{Colors.GREEN}{client_id}{Colors.RESET}", port)
                for idx, (client_id, port) in enumerate(self.client_mapping.items(), start=1)
            ]
            print(tabulate(data, headers=headers, tablefmt="grid"))
            return True
    
    def connect_to_client(self, client_id):
        """Connect to a specific client using its assigned port."""
        # Close any existing connection first
        if self.client_socket:
            try:
                self.client_socket.close()
            except:
                pass

        if client_id not in self.client_mapping:
            print(f"Client {client_id} is not connected.")
            return False

        port = self.client_mapping[client_id]
        try:
            print(f"Connecting to {client_id} at {self.server_ip}:{port}...")
            self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.client_socket.connect((self.server_ip, port))
            self.current_client_id = client_id
            print(f"Successfully connected to {client_id}. Type 'exit' to disconnect.")
            return True
        except Exception as e:
            print(f"Error connecting to client {client_id}: {e}")
            self.client_socket = None
            self.current_client_id = None
            return False

    @require_connection
    def send_command(self, command):
        """Send a general command to the current client and return the response."""
        try:
            self.client_socket.send(command.encode())
            response = self.client_socket.recv(4096).decode()
            return response
        except ConnectionResetError:
            print("Server has closed the connection.")
            self.client_socket = None
            self.current_client_id = None
            return "CONNECTION_CLOSED"

    @require_connection
    def receive_file_from_server(self, file_name, command_inital, extra=''):
        """Receive a file from the server."""
        try:
            file_name = file_name.strip()
            # Construct command, removing extra spaces
            command = f"{command_inital} {file_name}"
            if extra:
                command = f"{command} {extra}"
            command = command.strip()

            self.client_socket.send(command.encode())
            response = self.client_socket.recv(4096).decode()
            if response.startswith("ERROR"):
                print(f"Server Response: {response}")
                return

            file_size = int(response.strip())
            print(f"File size is {file_size} bytes.")

            # Notify the server that the client is ready to receive
            self.client_socket.send(b"READY")

            # Receive file content
            bytes_received = 0
            with open(file_name, "wb") as file:
                while bytes_received < file_size:
                    chunk = self.client_socket.recv(4096)
                    if chunk.endswith(b"END"):
                        file.write(chunk[:-3])  # Exclude "END" marker
                        bytes_received += len(chunk) - 3
                        progress = (bytes_received / file_size) * 100
                        print(f"\rProgress: {progress:.1f}% ⦿ ", end="")
                        break
                    file.write(chunk)
                    bytes_received += len(chunk)

            print(f"File '{file_name}' received successfully. Size: {bytes_received} bytes.")
        except ValueError as e:
            print(f"Error receiving file: {e}")
        except Exception as e:
            print(f"Unexpected error: {e}")

    @require_connection
    def receive_folder_from_server(self, folder_name):
        """Receive a folder and its contents from the server."""
        try:
            command = f"cpdir {folder_name}".strip()
            self.client_socket.send(command.encode())
            
            response = self.client_socket.recv(4096).decode()
            if response.startswith("ERROR"):
                print(f"Server Response: {response}")
                return

            # Receive metadata
            metadata_size = int(response)
            self.client_socket.send(b"READY")
            
            metadata_str = ""
            bytes_received = 0
            while bytes_received < metadata_size:
                chunk = self.client_socket.recv(4096).decode()
                metadata_str += chunk
                bytes_received += len(chunk)

            metadata = eval(metadata_str)
            self.client_socket.send(b"METADATA_RECEIVED")

            # Create all directories first
            for file_info in metadata['files']:
                if file_info['type'] == 'DIR':
                    os.makedirs(file_info['path'], exist_ok=True)

            # Then receive all files
            total_received = 0
            for file_info in metadata['files']:
                if file_info['type'] == 'FILE':
                    print(f"Receiving: {file_info['path']}")
                    
                    # Ensure directory exists
                    os.makedirs(os.path.dirname(file_info['path']), exist_ok=True)
                    
                    bytes_received = 0
                    with open(file_info['path'], "wb") as file:
                        while bytes_received < file_info['size']:
                            remaining = file_info['size'] - bytes_received
                            chunk_size = min(4096, remaining)
                            chunk = self.client_socket.recv(chunk_size)
                            if not chunk:
                                raise Exception(f"Connection lost while receiving {file_info['path']}")
                            file.write(chunk)
                            bytes_received += len(chunk)
                            
                            # Update progress
                            total_received += len(chunk)
                            progress = (total_received / metadata['total_size']) * 100
                            print(f"\rOverall Progress: {progress:.1f}% ", end="", flush=True)
                    
                    self.client_socket.send(b"FILE_RECEIVED")

            print(f"\nFolder '{folder_name}' received successfully.")
        except Exception as e:
            print(f"Error receiving folder: {e}")
            # Create error log
            with open("cpdir_error.log", "a") as log:
                log.write(f"{folder_name}: {str(e)}\n")

    @require_connection
    def receive_screenshot(self, file_name='screenshot'):
        """Take a picture and save it as a .png file."""
        file_name = f"{file_name}.png"
        try:
            print(f"Taking a screenshot - {file_name}")
            self.receive_file_from_server(file_name, 'shot')
        except Exception as e:
            print(f"Error recording voice: {e}")

    @require_connection
    def receive_picture(self, file_name='picture'):
        """Take a picture and save it as a .jpg file."""
        file_name = f"{file_name}.jpg"
        try:
            print(f"Taking a picture - {file_name}")
            self.receive_file_from_server(file_name, 'picture')
        except Exception as e:
            print(f"Error recording voice: {e}")

    @require_connection
    def receive_voice(self, file_name="recording", duration=5):
        """Record a voice message and save it as a .wav file."""
        file_name = f"{file_name}.wav"
        try:
            self.receive_file_from_server(file_name, 'voice', duration)
            print(f"Recording saved as '{file_name}'.")
        except Exception as e:
            print(f"Error recording voice: {e}")

    @require_connection
    def receive_screen_recording(self, file_name="scrnrec", duration=10):
        """Receive a screen recording file from server."""
        file_name = f"{file_name}.mp4"
        try:
            self.receive_file_from_server(file_name, 'scrnrec', duration)
            print(f"Screen recording saved as '{file_name}'.")
        except Exception as e:
            print(f"Error receiving screen recording: {e}")

    @require_connection
    def receive_system_control_command(self, ins):
        """Receive a screen recording file from server."""
        try:
            self.client_socket.send(str(ins).encode())
            print(f"{ins} initialised...")
        except Exception as e:
            print(f"Error receiving screen recording: {e}")
    
    @require_connection
    def receive_internet_search(self, search):
        """Receive a screen recording file from server."""
        try:
            self.client_socket.send(str(search).encode())
        except Exception as e:
            print(f"Error googling: {e}")

    @require_connection
    def receive_delete_folder_or_file(self, rm_command):
        """rm >> file_path | rm >> -r >> file_path"""
        try:
            self.client_socket.send(str(rm_command).encode())
            response = self.client_socket.recv(4096).decode()
            print(response)
        except Exception as e:
            print(f"Error receiving screen recording: {e}")

    def display_home(self):
        print("""
                \033[93mBasic Commands:\033[0m
                ---
                slx                           : Home
                ls                            : List directory contents
                cd <dir>                      : Change directory
                pwd                           : Print working directory
                clear                         : Clear terminal
                exit                          : Exit terminal
                terminate                     : Kill session
                     
                \033[92mFile Operations:\033[0m
                ---
                cp <file>                     : Copy file
                cpdir <folder>                : Copy folder
                rm >> <file path>             : Remove file
                rm >> -r >> <folder path>     : Remove folder

                \033[94mMedia Commands:\033[0m
                ---
                shot                          : Take screenshot
                picture                       : Capture webcam image
                voice                         : Record audio
                scrnrec                       : Record screen
                
                \033[91mSystem Commands:\033[0m
                ---
                sys <command>                 : Sleep, Lock 
                sys vol <command>             : Volume up/down
              
                \033[96mInternet :\033[0m
                ---
                slx <type>: <query>           : Perform a web search via google | youtube
                slx yt: <link>                : Search via YouTube link
        """)

    def get_command_with_history(self):
        command = ""
        command_list = ["slx", "ls", "cd", "pwd", "cp", "cpdir", "rm", "shot", "picture", 
                        "voice", "scrnrec", "sys", "clear", "exit", "terminate"]
        current_suggestion = -1

        print("\033[96mselahx>\033[0m ", end="", flush=True)
        
        while True:
            k = readkey()
            if k == key.UP:
                current_suggestion = min(current_suggestion + 1, len(command_list) - 1)
                command = command_list[current_suggestion]
            elif k == key.DOWN:
                current_suggestion = max(current_suggestion - 1, -1)
                command = command_list[current_suggestion] if current_suggestion >= 0 else ""
            elif k == key.ENTER:
                print()
                return command
            elif k == key.BACKSPACE:
                command = command[:-1]
            elif k.isprintable():
                command += k
            
            print(f"\r\033[K\033[96mselahx>\033[0m {command}", end="", flush=True)

    def start_client(self):
        """Start the EC2Instance command loop."""
        self.display_home()
        last_command = None
        
        while True:
            try:
                command = self.get_command_with_history().strip()

                if command.lower().startswith("clear"):
                    os.system('cls' if os.name == 'nt' else 'clear')
                    last_command = None
                    continue

                if command.lower().startswith("lscl"):
                    # List clients and prompt for connection
                    if self.list_connected_clients():
                        client_id = input("Enter the Client ID to connect (or press Enter to cancel): ").strip()
                        if client_id:
                            # Disconnect from current client if connected
                            if self.current_client_id:
                                print(f"Disconnecting from {self.current_client_id}")
                            
                            # Attempt to connect to new client
                            if not self.connect_to_client(client_id):
                                print("Failed to connect. Try again.")
                    last_command = None
                    continue
                
                if command.lower() == "slx":
                    self.display_home()
                    last_command = None
                    continue
                
                if command and not command.lower().startswith("clear"):
                    last_command = command
                
                if command.lower().startswith("cp "):
                    file_name = command.split(maxsplit=1)[1].strip()
                    self.receive_file_from_server(file_name, 'cp')
                
                elif command.lower().startswith("cpdir "):
                    folder_name = command.split(maxsplit=1)[1].strip()
                    self.receive_folder_from_server(folder_name)
                
                elif command.lower() == "shot":
                    file_name = input("Enter filename for the screenshot (default: screenshot.png): ").strip()
                    if not file_name:
                        file_name = "screenshot"
                    self.receive_screenshot(file_name)

                elif command.lower() == "picture":
                    file_name = input("Enter filename for the picture (default: picture.jpg): ").strip()
                    if not file_name:
                        file_name = "picture"
                    self.receive_picture(file_name)
                
                elif command.lower() == "voice":
                    file_name = input("Enter filename for the recording (default: recording.wav): ").strip()
                    if not file_name:
                        file_name = "recording"
                    duration = input("Enter duration for the recording in seconds (default: 5): ").strip()
                    duration = int(duration) if duration.isdigit() else 5
                    self.receive_voice(file_name, duration)
                
                elif command.lower() == "scrnrec":
                    file_name = input("Enter filename for the screen recording (default: scrnrec.mp4): ").strip()
                    if not file_name:
                        file_name = "scrnrec"
                    duration = input("Enter duration for the screen recording in seconds (default: 5): ").strip()
                    duration = int(duration) if duration.isdigit() else 5
                    self.receive_screen_recording(file_name, duration)
                
                elif command.lower().startswith("sys "):
                    self.receive_system_control_command(command.lower())
                
                elif command.lower().startswith("slx "):
                    self.receive_internet_search(command)

                elif command.lower().startswith("rm "):
                    self.receive_delete_folder_or_file(command.lower())
                
                elif command.lower() == "terminate":
                    if not self.ensure_client_connection():
                        return ""
                    print("Sending FORCE EXIT command to the server.")
                    self.client_socket.send("terminate".encode())
                    print("Server shut down. Closing client.")
                    break
                
                elif command.lower() == "exit":
                    if not self.ensure_client_connection():
                        return ""
                    print("Exiting...")
                    self.client_socket.send("EXIT".encode())
                    break

                elif command or (last_command and not command.lower().startswith("clear")):
                    cmd_to_send = command if command else last_command
                    response = self.send_command(cmd_to_send)
                    if response:
                        if response == "CONNECTION_CLOSED":
                            print("Connection to the server was closed.")
                            break
                        print(f"Server Response: {response}")

            except (ConnectionResetError, BrokenPipeError):
                print("Connection to the server was lost. Exiting.")
                break
        
        if self.client_socket:
            self.client_socket.close()

def client_cli(username: str, port: int):
    """Run the selahx client terminal."""

    logo = rf"""{Colors.GREEN}
   _____      _       _    __   __
  / ____|    | |     | |   \ \ / /
 | (___   ___| | __ _| |__  \ V / 
  \___ \ / _ \ |/ _` | '_ \  > <  
  ____) |  __/ | (_| | | | |/ . \ 
 |_____/ \___|_|\__,_|_| |_/_/ \_\\
        
        TERMINAL - VERSION 1.0 
    {Colors.RESET}"""

    print(logo)

    server_ip = "127.0.0.1"
    client = EC2Instance(server_ip)

    print(f"{Colors.BRIGHT_GREEN}Initializing connection for user '{username}' on port {port}...{Colors.RESET}")
    client.create_tmp(username, port)
    client.start_client()
