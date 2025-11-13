# Project Setup - Development and Client

## Table of Contents 
<!-- TOC -->
* [Project Setup - Development and Client](#project-setup---development-and-client)
  * [Table of Contents](#table-of-contents-)
* [== PyCharm - INITIAL SETUP AFTER GITHUB PULL ==](#-pycharm---initial-setup-after-github-pull-)
    * [Create a clean repository](#create-a-clean-repository)
    * [Setup UV Virtual Environment](#setup-uv-virtual-environment)
* [== UV USAGE ==](#-uv-usage-)
    * [Development](#development)
  * [Client Machine Setup](#client-machine-setup)
    * [UV Global Setup](#uv-global-setup)
    * [Project Setup](#project-setup)
* [== SystemD SETUP ==](#-systemd-setup-)
  * [Initial Setup](#initial-setup)
  * [Useful Commands](#useful-commands)
  * [Update Script](#update-script)
<!-- TOC -->

# == PyCharm - INITIAL SETUP AFTER GITHUB PULL ==
### Create a clean repository
- In PyCharm project terminal
```bash
rm -rf .git
git init
```
- Setup new GitHub Repo on initial commit
### Setup UV Virtual Environment
- cd to project folder
```bash
uv venv
```

# == UV USAGE ==
### Development
- Add Python Packages with UV pip
```bash
uv pip install "package-name"
```

- Update requirements
```bash
uv pip compile -o requirements.lock requirements.txt
```

## Client Machine Setup
### UV Global Setup
- (If required) Install UV on client machine
- This will install UV as a global package 
1. Download latest UV release for linux
```bash
 curl -L https://github.com/astral-sh/uv/releases/latest/download/uv-x86_64-unknown-linux-gnu.tar.gz -o uv.tar.gz
```
2. extract it
```bash
tar -xzf uv.tar.gz
```
3. Go to extracted folder and find uv or uvx
```bash
ls
cd uv-*-x86_64-unknown-linux-gnu # May need to change directory name
ls
```
4. Move the uv binary to /usr/local/bin/ (This makes uv available globally on your server for any user.)
```bash
sudo mv uv /usr/local/bin/
```
5. Cleanup
```bash
cd ~
rm -rf uv-*-x86_64-unknown-linux-gnu uv.tar.gz # Change name as needed
```
6. Check UV version
```bash
uv --version
```

### Project Setup
1. Clone from GitHub
```bash
git clone https://github.com/yourname/my-program.git
```
- Or update if already installed
```bash
git pull
```
2. Navigate to project directory
```bash
cd my-program
```
3. Setup program
```bash
uv venv
uv pip sync requirements.lock
uv run python src/main.py
```

# == SystemD SETUP ==
## Initial Setup
1. Setup service script (see template)
2. Copy to machine
```bash
sudo nano /etc/systemd/system/myprogram.service
```
3. Enable and start the service
```bash
sudo systemctl daemon-reload
sudo systemctl enable myprogram.service
sudo systemctl start myprogram.service
```
## Useful Commands
- Status
```bash
sudo systemctl status myprogram.service
```
- View logs
```bash
journalctl -u myprogram.service -f
```
- Fix ownerships/permissions
```bash
sudo chown -R yourusername:yourusername /opt/my-program
```

## Update Script
- Create file
```bash
nano update_and_run.sh
```
- Paste Script
```bash
#!/bin/bash
set -e

echo "Pulling latest code..."
git pull

echo "Syncing Python dependencies..."
uv pip sync

echo "Running the app..."
uv run python main.py
```
- Make it executable
```bash
chmod +x update_and_run.sh
```
