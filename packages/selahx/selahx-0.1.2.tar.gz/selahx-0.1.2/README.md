# selahx

[![Python](https://img.shields.io/badge/python-3.8%2B-blue.svg)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
---

## Features

![selahx logo](https://github.com/Haabiy/selahx/blob/main/Asset/selahx.png)

- Remotely access files on a local machine from another device
- Transfer files from EC2 to local machine  
- Lightweight and dependency-managed with Poetry  

---

## Usage

### Server

Start the server on a specific host and port:

```bash
selahx server --key-file key.pem --port 1221 --ssh-host ubuntu@ec2-xx-xx-xx-xx.compute-1.amazonaws.com
````

**Options:**

* `--key-file` — Path to the SSH private key
* `--port` — Local port for the server
* `--ssh-host` — SSH host (e.g., `ubuntu@ec2-instance`)

---

### Client

Start a client and connect to the server:

```bash
selahx client --username user --port 1221
```

**Options:**

* `--username` — Username for the client session
* `--port` — Server port to connect to

---

### Transfer files from EC2 to Local

Start saving files:

```bash
selahx save --key-file key.pem --user ubuntu --host ec2-xx-xx-xx-xx.compute-1.amazonaws.com --dest ~/Downloads/test
```

**Options:**

* `--key-file` — Path to the SSH private key
* `--user` — `ubuntu` (user for `ubuntu@ec2-xx-xx-xx-xx.compute-1.amazonaws.com`)
* `--host` — EC2 host (everything after `@`)
* `--dest` — Destination folder
* `~/Downloads/test` — Example local destination path

---

## Example Workflow

1. Launch the server on your EC2 instance:

```bash
selahx server --key-file key.pem --port 1221 --ssh-host ubuntu@ec2-xx-xx-xx-xx.compute-1.amazonaws.com
```

2. Connect a client from your local machine:

```bash
selahx client --username user --port 1221
```

Once connected, a reverse SSH tunnel is automatically established.

---

## Requirements

* Python 3.8+
* Dependencies are managed via Poetry (see `pyproject.toml`)

---