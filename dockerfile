FROM ubuntu:22.04

#Install sudo
RUN apt-get update && apt-get -y install sudo

#We create a new user
ARG USER=foo
ARG PASS="qwerty1234"
RUN useradd -m -s /bin/bash $USER && echo "$USER:$PASS" | chpasswd
RUN usermod -aG sudo foo
RUN echo "ALL ALL=(ALL) NOPASSWD: ALL" >> /etc/sudoers
USER foo
WORKDIR /home/foo
RUN whoami
RUN sudo whoami

#We install software-properties-common so that we can use add-apt-repository
RUN sudo apt -y update
RUN sudo apt -y install software-properties-common
RUN sudo apt -y update

#Install openssh-server
RUN sudo apt-get -y install openssh-server

#Install GNOME
RUN sudo apt -y update
RUN sudo DEBIAN_FRONTEND=noninteractive apt install ubuntu-gnome-desktop -y

#Install Xfce4 init session
RUN sudo apt-get update
RUN sudo apt-get install apt-utils
RUN sudo DEBIAN_FRONTEND=noninteractive apt-get install xfce4 -y
RUN sudo apt-get install xfce4-goodies -y

#We change to root user
USER root

#We configure default login under Xfce4
RUN sudo printf "[InputSource0] \
\nxkb=us \
\n \
\n[User] \
\nXSession=xfce \
\nBackground=/usr/share/backgrounds/xfce/xfce-teal.jpg \
\nSystemAccount=false \n" > /var/lib/AccountsService/users/foo

#We change to foo's user
USER foo
WORKDIR /home/foo

#We configure openssh-server so that it does let us make X11 forwarding under ssh using 22 Port
RUN sudo sed -i 's/#Port 22/Port 22/g' /etc/ssh/sshd_config
RUN sudo sed -i 's/#PermitRootLogin prohibit-password/PermitRootLogin yes/g' /etc/ssh/sshd_config
RUN sudo sed -i 's/#PasswordAuthentication yes/PasswordAuthentication yes/g' /etc/ssh/sshd_config
RUN sudo sed -i 's/#X11DisplayOffset 10/X11DisplayOffset 10/g' /etc/ssh/sshd_config
RUN sudo sed -i 's/#X11UseLocalhost yes/X11UseLocalhost yes/g' /etc/ssh/sshd_config

#We change to root's user
USER root

#We prepare a ssh script so that the service can be run
RUN sudo printf "#!/bin/bash \
\nsudo ssh-keygen -A \
\nsudo service ssh start \n" > /init-ssh.sh

#We give to the script execution permissions
RUN chmod +x /init-ssh.sh

#We install TigerVNC as the VNC Server we will be using
RUN sudo apt -y install tigervnc-standalone-server tigervnc-xorg-extension tigervnc-viewer

RUN sudo printf "#!/bin/bash \
\nmypasswd="qwerty1234" \
\nsudo mkdir /root/.vnc \n" > /init-vncserver-config1.sh

RUN chmod +x /init-vncserver-config1.sh
RUN sudo /init-vncserver-config1.sh

RUN printf "qwerty1234\nqwerty1234\n\n" | vncpasswd
RUN sudo chmod 0600 /root/.vnc/passwd

RUN sudo touch ~/.Xauthority
RUN sudo touch ~/.Xresources

#We prepare Xstartup file
RUN sudo printf "#!/bin/bash \
\n/usr/bin/autocutsel -s CLIPBOARD -fork \
\nxrdb $HOME/.Xresources \
\nstartxfce4 & \n" > /root/.vnc/xstartup

#We give to the Xstartup file execution permissions
RUN chmod +x /root/.vnc/xstartup

#We prepare a script for VNC Session initialization when the container is up
RUN sudo printf "#!/bin/bash \
\ntigervncserver -xstartup /usr/bin/xfce4-session \n" > /init-vncserver.sh

RUN chmod +x /init-vncserver.sh

#Kivy and python3 Installation
RUN sudo add-apt-repository -y ppa:kivy-team/kivy
RUN sudo apt-get -y update
RUN sudo apt-get -y install python3-kivy
RUN sudo apt-get -y install kivy-examples

COPY /src /home/foo/src

#We set a ENV variable availabe for all users (root included)
RUN echo 'export DISPLAY=:1.0' >> ~/.bashrc

RUN sudo printf "#! /usr/bin/env bash \
\nexport DISPLAY=:1.0 \n" > /export.bash

#We prepare the script which will be launching the game and maximizing the window in which the game will be running into
RUN sudo printf "#!/bin/bash \
\nsource /export.bash \
\necho \$DISPLAY \
\ndevilspie & python3 /home/foo/src/main.py \n" > /init-kivy.sh

RUN sudo chmod 777 /export.bash
RUN chmod +x /init-kivy.sh

#We install devilspie so that our applications will be rendered at maximum size
RUN sudo apt-get -y install devilspie
RUN mkdir -p ~/.devilspie
RUN sudo printf "(begin\
\n    (maximize)(focus)\
\n)" > ~/.devilspie/maximize.ds

#We set the password to root user
RUN echo "root:qwerty1234" | chpasswd

ENTRYPOINT /init-ssh.sh && /init-vncserver.sh && /init-kivy.sh && bash