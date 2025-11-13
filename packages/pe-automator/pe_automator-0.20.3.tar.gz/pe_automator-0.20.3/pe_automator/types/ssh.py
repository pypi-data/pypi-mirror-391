# simple_ssh_client.py
import paramiko
import threading

class SimpleSSHClient:
    def __init__(self, name, hostname, username, password=None, port=22, key_filename=None, timeout=10):
        self.name = name
        self.hostname = hostname
        self.port = port
        self.username = username
        self.password = password
        self.key_filename = key_filename
        self.timeout = timeout
        self.client = None
        self.lock = threading.Lock()

    def connect(self):
        if self.client is None or not self.client.get_transport().is_active():
            self.client = paramiko.SSHClient()
            self.client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            if self.key_filename or self.password:
                self.client.connect(
                    hostname=self.hostname,
                    port=self.port,
                    username=self.username,
                    password=self.password,
                    key_filename=self.key_filename,
                    timeout=self.timeout
                )
            else:
                agent = paramiko.Agent()
                keys = agent.get_keys()
                if not keys:
                    raise ValueError("No SSH keys found in the agent.")
                for key in keys:
                    try:
                        self.client.connect(
                            hostname=self.hostname,
                            port=self.port,
                            username=self.username,
                            pkey=key,
                            timeout=self.timeout
                        )
                        break  # If connection is successful, exit the loop
                    except paramiko.AuthenticationException:
                        continue

    def execute(self, command, get_output=True):
        with self.lock:
            if self.client is None:
                raise Exception("SSH client not connected. Call connect() first.")

            stdin, stdout, stderr = self.client.exec_command(command)
            if get_output:
                out = stdout.read().decode()
                err = stderr.read().decode()
                return out.strip(), err.strip()
            return None, None

    def close(self):
        if self.client:
            self.client.close()
            self.client = None

    def __enter__(self):
        self.connect()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.close()


class MultiSSHManager:
    def __init__(self, server_configs = []):
        """
        server_configs: List of dicts with keys:
            - hostname, username, password or key_filename, port (optional)
        """
        self.clients = {}
        self.lock = threading.Lock()

        for config in server_configs:
            name = config['name']
            self.clients[name] = SimpleSSHClient(**config)

    def add_client(self, name, hostname, username, password=None, port=22, key_filename=None, timeout=10, skip_if_exists=False):
        if name in self.clients:
            if skip_if_exists:
                return
            raise ValueError(f"Client with name {name} already exists.")
        self.clients[name] = SimpleSSHClient(name, hostname, username, password, port, key_filename, timeout)
        self.clients[name].connect()

    def get_client(self, name):
        if name not in self.clients:
            raise KeyError(f"No such host: {name}")
        return self.clients[name]

    def is_client_connected(self, name):
        if name not in self.clients:
            raise KeyError(f"No such host: {name}")
        return self.clients[name].client is not None and self.clients[name].client.get_transport().is_active()

    def connect_all(self):
        threads = []
        for name, client in self.clients.items():
            t = threading.Thread(target=client.connect)
            t.start()
            threads.append(t)
        for t in threads:
            t.join()

    def execute_on(self, name, command):
        """
        Returns: (stdout, stderr) or raises KeyError
        """
        if name not in self.clients:
            raise KeyError(f"No such host: {name}")
        return self.clients[name].execute(command)

    def close_all(self):
        for client in self.clients.values():
            client.close()

    def __enter__(self):
        self.connect_all()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.close_all()