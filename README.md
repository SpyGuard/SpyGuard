![title](https://user-images.githubusercontent.com/25131750/200111909-e0d10587-014a-410c-be05-e7e89cf6c9f5.gif)

### Description 

SpyGuard is a forked and enhanced version of [TinyCheck](https://github.com/KasperskyLab/TinyCheck), developed by the same author when he was working at Kaspersky. SpyGuard's main objective is to detect signs of compromise by monitoring network flows transmitted by a device. 

As it uses WiFi, SpyGuard can be used against a wide range of devices, such as smartphones, laptops, IOTs or workstations. To do its job, the analysis engine of SpyGuard is using Indicators of Compromise (IOCs), anomaly detection and is supported by [Suricata](https://suricata.io).

### Installation

You need a debian-like operating system to install it easly by using the provided bash script. Once you've cloned the repository, just launch `install.sh` as root. Here are the command lines to do that:

```
cd /tmp/ && git clone https://github.com/SpyGuard/spyguard
cd spyguard && sudo bash install.sh
```

Once installed, you can go to the backend interface located at `https://localhost:8443` to manage the device and setup the right network interfaces to get it working. Please look at the [dedicated wiki page](https://github.com/SpyGuard/spyguard/wiki/Installing-SpyGuard) to get some tips regarding it.

> Please check prior the installation that your Linux distribution is using `nmcli` to manage networks. If you want to install it on a Raspberry Pi
> you need to activate it via the `raspi-config` interface.

### Smartphone analysis best practices 

* Do the interception in a public place (library, restaurant...) or common place (office, home...); 
* Intercept the network communications of the device for at least 10 minutes; 
* Interact with the analysed device during the interception (reboot it, take a photo, send a message...);

### SpyGuard and Stalkerware threat

The indicators of compromise (IOCs) linked to stalkerware are now fully managed by [ECHAP](https://echap.eu.org), a French association working against  cyberviolence. Even though stalkerware still remains a threat, remember that most of digital violence and surveillance is done by using simple means, such as hacking cloud & mail accounts. Therefore, we encourage you to consult the [ECHAP guides](https://echap.eu.org/ressources/) and apply their advice to your digital life alongside of device checks.

> It is worth mentioning that the IOCs are distributed under the **Creative Common BY-NC-SA** licence.
> This imply a **non commercial use** of them. Please respect this licence and ask ECHAP for any question related to that.

### Commercial use

You can use SpyGuard in a commercial product. However, you can't use SpyGuard as the name of your product and you’re still required to follow the terms and conditions that the Apache License imposes, like refering to the SpyGuard project in customer documentation. Moreover, a sweet note to explain your use to the author is always appreciated, please see the contact below. 

### Contact

If you need an express help or have a specific demand/question, do not hesitate to contact [the author](https://twitter.com/felixaime) via Twitter or by sending an email at spyguard@protonmail.com. A bug? Do not hesitate to open a [new issue](https://github.com/SpyGuard/spyguard/issues).

### They have contributed to or helped this project

<p float="left">
  <a href="https://echap.eu.org"><img src="https://user-images.githubusercontent.com/25131750/200112980-80adc6e6-c922-471d-ab50-9821b2ed484c.png" width="150" /></a>&nbsp;&nbsp;
  <a href="https://www.sekoia.io"><img src="https://user-images.githubusercontent.com/25131750/200112989-f18c29a7-c947-4eb6-95e4-997fc97c5b4d.png" height="90" /></a>
  <a href="https://www.lapostegroupe.com"><img src="https://user-images.githubusercontent.com/25131750/200187728-d67c6139-01af-4e64-9f32-096c028db6e1.png" height="90" /></a>

</p>

To work, Spyguard is using a lot of awesome opensource projects, libraries, and fonts, kudos to them:

[Dumpcap](https://tshark.dev/capture/dumpcap/), 
[Dig](https://github.com/tigeli/bind-utils), 
[Suricata](https://suricata.io/), 
[NetworkManager](https://github.com/NetworkManager/NetworkManager),
[Python](https://www.python.org),
[VueJS](https://vuejs.org),
[Pip](https://github.com/pypa/pip), 
[pydig](https://pypi.org/project/pydig/), 
[pymisp](https://pypi.org/project/pymisp), 
[netaddr](https://pypi.org/project/netaddr), 
[pyyaml](https://pypi.org/project/pyyaml), 
[flask](https://pypi.org/project/flask), 
[flask_httpauth](https://pypi.org/project/flask_httpauth), 
[pyjwt](https://pypi.org/project/pyjwt), 
[sqlalchemy](https://pypi.org/project/sqlalchemy), 
[psutil](https://pypi.org/project/psutil), 
[pyudev](https://pypi.org/project/pyudev), 
[qrcode](https://pypi.org/project/qrcode), 
[netifaces](https://pypi.org/project/netifaces), 
[weasyprint](https://pypi.org/project/weasyprint), 
[python-whois](https://pypi.org/project/python-whois), 
[publicsuffix2](https://pypi.org/project/publicsuffix2), 
[six](https://pypi.org/project/six), 
[Exo2 font](https://github.com/NDISCOVER/Exo-2.0),
[Virtual Keyboard](https://virtual-keyboard.js.org/vuejs/),
[OpenSSL](https://www.openssl.org),
[Spectre CSS](https://picturepan2.github.io/spectre/).

Icons and design created via [Figma](https://www.figma.com).
