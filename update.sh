# Checking rights.
if [[ $EUID -ne 0 ]]; then
    echo "The update must be run as root. Type in 'sudo bash $0' to run it as root."
	exit 1
fi

if [ $PWD = "/usr/share/spyguard" ]; then
    echo "[+] Cloning the current repository to /tmp/"
    rm -rf /tmp/spyguard/ &> /dev/null
    cd /tmp/ && git clone https://github.com/SpyGuard/spyguard
    cd /tmp/spyguard && bash update.sh
elif [ $PWD = "/tmp/spyguard" ]; then

    echo "[+] Saving SpyGuard backend's SSL configuration in /tmp/"
    mv /usr/share/spyguard/server/backend/*.pem /tmp/

    echo "[+] Deleting the current SpyGuard folders and files."
    rm -rf /usr/share/spyguard/app/
    rm -rf /usr/share/spyguard/server/
    rm -rf /usr/share/spyguard/analysis/
    rm /usr/share/spyguard/update.sh
    rm /usr/share/spyguard/uninstall.sh

    echo "[+] Copying the new SpyGuard version"
    cp -R app/ /usr/share/spyguard/app/
    cp -R server/ /usr/share/spyguard/server/
    cp -R analysis/ /usr/share/spyguard/analysis/
    cp update.sh /usr/share/spyguard/update.sh
    cp kiosk.sh /usr/share/spyguard/kiosk.sh
    cp uninstall.sh /usr/share/spyguard/uninstall.sh

    echo "[+] Retoring the backend's SSL configuration from /tmp/"
    mv /tmp/*.pem /usr/share/spyguard/server/backend/

    echo "[+] Checking possible new Python dependencies"
    python3 -m pip install -r assets/requirements.txt

    echo "[+] Updating the database scheme..."
    cd /usr/share/spyguard/
    sqlite3 database.sqlite3 < /tmp/spyguard/assets/scheme.sql 2>/dev/null

    echo "[+] Restarting services"
    service spyguard-backend restart
    service spyguard-frontend restart
    service spyguard-watchers restart

    echo "[+] Updating the SpyGuard version"
    cd /tmp/spyguard && git tag | tail -n 1 | xargs echo -n > /usr/share/spyguard/VERSION

    echo "[+] SpyGuard updated!"
fi
