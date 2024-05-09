#!/bin/bash
CURRENT_USER="${SUDO_USER}"
SCRIPT_PATH="$( cd "$(dirname "$0")" ; pwd -P )"
HOST="$( hostname )"
LOCALES=(de en es fr it pl pt ru)

welcome_screen() {
cat << "EOF"
   __   _         __              _    _
  (_   |_)  \_/  /__  | |   /\   |_)  | \
  __)  |     |   \_|  |_|  /--\  | \  |_/

SpyGuard is a fork of TinyCheck, developped by Kaspersky.
-----

EOF
}

set_userlang() {
    # Set the user language.
    echo -e "\e[39m[+] Setting the user language...\e[39m"
    printf -v joined '%s/' "${LOCALES[@]}"
    echo -n "    Please choose a language for the reports and the user interface (${joined%/}): "
    read lang

    if [[ " ${LOCALES[@]} " =~ " ${lang} " ]]; then
        sed -i "s/userlang/${lang}/g" /usr/share/spyguard/config.yaml
        echo -e "\e[92m    [✔] User language settled!\e[39m"
    else
        echo -e "\e[91m    [✘] You must choose between the languages proposed, let's retry.\e[39m"
        set_userlang
    fi
}

testing_distro() {
    # Check if the package manager is apt
    if [[ ! -f "/usr/bin/apt"  ]]; then
            echo -e "\e[91m    [✘] You must run this script on a system with apt package management system, like Debian.\e[39m"
            echo -e "\e[91m        Exiting...\e[39m"
            exit
    fi
}

set_credentials() {
    # Set the credentials to access to the backend.
    echo -e "\e[39m[+] Setting the backend credentials...\e[39m"
    echo -n "    Please choose a username for SpyGuard's backend: "
    read login
    echo -n "    Please choose a password for SpyGuard's backend: "
    read -s password1
    echo ""
    echo -n "    Please confirm the password: "
    read -s password2
    echo ""

    if [ $password1 = $password2 ]; then
        password=$(echo -n "$password1" | sha256sum | cut -d" " -f1)
        sed -i "s/userlogin/$login/g" /usr/share/spyguard/config.yaml
        sed -i "s/userpassword/$password/g" /usr/share/spyguard/config.yaml
        echo -e "\e[92m    [✔] Credentials saved successfully!\e[39m"
    else
        echo -e "\e[91m    [✘] The passwords aren't equal, please retry.\e[39m"
        set_credentials
    fi
}

create_directory() {
    # Create the SpyGuard directory and move the whole stuff there.
    echo -e "[+] Creating SpyGuard folder under /usr/share/"
    mkdir /usr/share/spyguard
    cp -Rf ./* /usr/share/spyguard
}

generate_certificate() {
    # Generating SSL certificate for the backend.
    echo -e "[+] Generating SSL certificate for the backend"
    openssl req -x509 -subj '/CN=spyguard.local/O=Spyguard Backend' -newkey rsa:4096 -nodes -keyout /usr/share/spyguard/server/backend/key.pem -out /usr/share/spyguard/server/backend/cert.pem -days 3650
}

create_services() {
    # Create services to launch the two servers.
    echo -e "\e[39m[+] Creating services\e[39m"

    echo -e "\e[92m    [✔] Creating frontend service\e[39m"
    cat >/lib/systemd/system/spyguard-frontend.service <<EOL
[Unit]
Description=Spyguard frontend service

[Service]
Type=simple
ExecStart=/usr/share/spyguard/spyguard-venv/bin/python3 /usr/share/spyguard/server/frontend/main.py
Restart=on-abort
KillMode=process

[Install]
WantedBy=multi-user.target
EOL

    echo -e "\e[92m    [✔] Creating backend service\e[39m"
    cat >/lib/systemd/system/spyguard-backend.service <<EOL
[Unit]
Description=Spyguard backend service

[Service]
Type=simple
ExecStart=/usr/share/spyguard/spyguard-venv/bin/python3 /usr/share/spyguard/server/backend/main.py
Restart=on-abort
KillMode=process

[Install]
WantedBy=multi-user.target
EOL

    echo -e "\e[92m    [✔] Creating watchers service\e[39m"
    cat >/lib/systemd/system/spyguard-watchers.service <<EOL
[Unit]
Description=spyguard watchers service
Wants=network-online.target
After=network-online.target

[Service]
Type=simple
ExecStart=/usr/share/spyguard/spyguard-venv/bin/python3 /usr/share/spyguard/server/backend/watchers.py
Restart=on-abort
KillMode=process

[Install]
WantedBy=multi-user.target
EOL

   echo -e "\e[92m    [✔] Enabling services\e[39m"
   systemctl enable spyguard-frontend &> /dev/null
   systemctl enable spyguard-backend &> /dev/null
   systemctl enable spyguard-watchers &> /dev/null

   echo -e "\e[92m    [✔] Starting services\e[39m"
   systemctl start spyguard-frontend
   systemctl start spyguard-backend
}

change_hostname() {
   # Changing the hostname to spyguard
   echo -e "[+] Changing the hostname to spyguard"
   echo "spyguard" > /etc/hostname
   sed -i "s/$HOST/spyguard/g" /etc/hosts

   # Adding spyguard.local to the /etc/hosts.
   echo "127.0.0.1  spyguard.local" >> /etc/hosts
}

install_packages() {
# Install associated packages by using aptitude.
packages=("tshark"
	   "sqlite3"
	   "suricata"
	   "dnsutils"
	   "python3-pip"
	   "python3-venv"
	   "net-tools"
           "python3-pil"
	   "libpango-1.0"
           "libpangoft2-1.0-0")
 
echo -e "\e[39m[+] Checking dependencies...\e[39m"
for package in "${packages[@]}"
do
    if dpkg-query -W -f='${Status}' "$package" 2>/dev/null | grep -q -P '^install ok installed$'; then
        echo -e "\e[92m    [✔] $package is already installed\e[39m"
    else
        echo -e "\e[93m    [✘] $package is not installed, lets install it\e[39m"
        apt-get install -y "$package"
        if [ $? -eq 0 ]; then
            echo -e "\e[92m    [✔] $package was successfully installed\e[39m"
        else
            echo -e "\e[91m    [✘] $package has an error during the installation\e[39m"
        fi
    fi
done
}

create_venv() {
   echo -e "\e[39m[+] Create and activate Virtual Environment for Python packages\e[39m"
   python3 -m venv /usr/share/spyguard/spyguard-venv
   source /usr/share/spyguard/spyguard-venv/bin/activate
   echo -e "\e[39m[+] Install Python packages...\e[39m"
   python3 -m pip install -r "$SCRIPT_PATH/assets/requirements.txt" --no-cache-dir
}

get_version() {
    # Get the actual SpyGuard version
    git tag | tail -n 1 | xargs echo -n > /usr/share/spyguard/VERSION
}

cleaning() {
    # Removing some files and useless directories
    rm /usr/share/spyguard/install.sh
    rm /usr/share/spyguard/README.md
    rm /usr/share/spyguard/LICENSE.txt
    rm /usr/share/spyguard/NOTICE.txt
    rm -rf /usr/share/spyguard/assets/

    # Disabling the suricata service
    systemctl disable suricata.service &> /dev/null

    # Removing some useless dependencies.
    apt autoremove -y &> /dev/null

    echo -e "\e[92m[+] Installation finished! You can open https://localhost:8443 to configure network settings.\e[39m"
}

create_database() {
    # Create the database. This base will be provisioned in IOCs by the watchers
    sqlite3 "/usr/share/spyguard/database.sqlite3" < "$SCRIPT_PATH/assets/scheme.sql"
}

feeding_iocs() {
    echo -e "\e[39m[+] Feeding your SpyGuard instance with fresh IOCs and whitelist, please wait."
    python3 /usr/share/spyguard/server/backend/watchers.py 2>/dev/null

    # Then, let's activate watchers service
    systemctl start spyguard-watchers
}

if [[ $EUID -ne 0 ]]; then
    echo "This must be run as root. Type in 'sudo bash $0' to run."
    exit 1
elif [[ -f /usr/share/spyguard/config.yaml ]]; then
    echo "You have a Spyguard instance already installed on this box."
    echo "  - If you want to update the instance, please execute:"
    echo "      sudo bash /usr/share/spyguard/update.sh"
    echo "  - If you want to uninstall the instance, please execute:"
    echo "      sudo bash /usr/share/spyguard/uninstall.sh"
    exit 1
else
    welcome_screen
    testing_distro
    create_directory
    get_version
    set_userlang
    set_credentials
    install_packages
    create_venv
    change_hostname
    generate_certificate
    create_database
    create_services
    feeding_iocs
    cleaning
fi
