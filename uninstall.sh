
delete_folder(){
    echo "[+] Deleting SpyGuard folders"
    rm -rf /usr/share/spyguard/
}

delete_services(){
    echo "[+] Deleting SpyGuard services"

    systemctl disable spyguard-frontend &> /dev/null
    systemctl disable spyguard-backend &> /dev/null
    systemctl disable spyguard-watchers &> /dev/null

    rm /lib/systemd/system/spyguard-frontend.service
    rm /lib/systemd/system/spyguard-backend.service
    rm /lib/systemd/system/spyguard-watchers.service
}

delete_packages(){
    pkgs=("tshark"
          "dnsutils"
          "suricata"
          "sqlite3")

    echo -n "[?] Do you want to remove the installed packages? (Yes/no) "
    read answer
    if [[ "$answer" =~ ^([yY][eE][sS]|[yY])$ ]]
    then
        rm -rf /var/log/suricata
        for pkg in "${pkgs[@]}"
        do
            apt -y remove $pkg && apt -y purge $pkg
        done
    fi
    apt autoremove &> /dev/null -y
}

update_hostname(){
   echo -n "[?] Please provide a new hostname: "
   read hostname
   echo "$hostname" > /etc/hostname
   sed -i "s/spyguard/$hostname/g" /etc/hosts
}

reboot_box() {
    echo -e "\e[92m[+] SpyGuard uninstalled, let's reboot.\e[39m"
    sleep 5
    reboot
}

# Checking rights.
if [[ $EUID -ne 0 ]]; then
    echo "The update must be run as root. Type in 'sudo bash $0' to run it as root."
	exit 1
else
    delete_folder
    delete_services
    update_hostname
    delete_packages
    reboot_box
fi
