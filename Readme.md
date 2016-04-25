# Hello and welcome to vAlfred's project #

![vAlfred_logo.png](https://googledrive.com/host/0B-f5ycVRULLQMVR4MEFxWjZueGM/vAlfred_project_logo_half.png)

# Sections #
1. [Description](#Description)
2. [Not too remote future (I hope)](#Not)
3. [Instalation](#Instalation)
4. [Dependencies](#Dependencies)
5. [Screenshots](#Screenshots)
6. [Licence](#Licence)
7. [Contact](#Contact)
8. [Legal](#Legal)

# <a name="Description"></a> Description #

This is a virtual butler that will help you making your house more awesome.

How? It lets you to remote turn on your pc (i.e. for resuming your torrent downloads or accessing it through VNC), use your Pi Camera to take a picture to see who is in your house (or if your dog is biting again your USB wires), add notification capabilities for your scripts right to your hand, send emails etc.

vAlfred is a python application that wraps around a Command-line interface for Telegram called [Telegram messenger CLI](https://github.com/vysheng/tg).
It allows you to interact with your virtual butler just sending messages through Telegram, right from your hand with your cell or using the web version. Everywhere you can access Telegram, Alfred will be there for you.

This application is designed for Linux environments and it suits perfect with the fabulous Raspberry Pi. Furthermore, vAlfred has been developed and tested in a Raspberry Pi model B.

# <a name="Not"></a> Not too remote future (I hope) #

My intention is to add AI capabilities to unleash its potential. I want to add [NLP](https://en.wikipedia.org/wiki/Natural_language_processing) (Natural Language Processing) so its interface will become much more simpler: no more strict pre-defined commands but something looser. Also, my intention is to make Alfred into a powerful security system capable to recognize faces using [OpenCV](https://en.wikipedia.org/wiki/OpenCV). This way, each non-recognized face can trigger an alert sending that picture to a remote server (to ensure it's integrity) and to its landlord to evaluate any potential trouble.

What I want to achieve can be reflected in the following situation:
I'm in the hall of my house ready to leave, the PIR sensor detects movement and the face recognizer engine detects my face. Alfred check my appointments on Google Calendar, the [Yahoo Weather](https://weather.yahoo.com/) API and after some seconds I get a Telegram message:

- Alfred: My lord, it seems that you are going to have a nice party tonight. I have checked the forecast for this whole night in Madrid and the temperature is going to fall down about 7 degrees at the end of the night. Will be a nice idea to carry a jacket.

# <a name="Instalation"></a> Instalation #

First you need to have [Telegram messenger CLI](https://github.com/vysheng/tg) running on your system. Currently I'm working with the [release 1.0.5.1](https://github.com/vysheng/tg/releases/tag/1.0.5.1) Newer versions were not tested with vAlfred, but will probably work.

After sending some messages using Telegram messenger CLI to test that is properly working, you need to install the dependencies stated in the *Dependencies* section.

I will provide soon a `python setup.py install` method, but right now the only way you have is download vAlfred's code in a folder, unpack it and manually update the paths in the code to your preferences. I know, I know, this is tedious, but this is not yet a Release Candidate version, it still need some improvements (like this).

# <a name="Dependencies"></a> Dependencies #

- [picam library](https://github.com/ashtons/picam)
- [pexpect library](http://pexpect.readthedocs.org/en/latest/install.html)
- WakeOnLan tool: `sudo apt-get install wakeonlan`
- Curl: `sudo apt-get install curl`

# <a name="Screenshots"></a> Screenshots #

![screen1_sm.png](https://googledrive.com/host/0B-f5ycVRULLQMVR4MEFxWjZueGM/screen1_sm.png)
![screen2_sm.png](https://googledrive.com/host/0B-f5ycVRULLQMVR4MEFxWjZueGM/screen2_sm.png)

# <a name="Licence"></a> Licence #

This code is released under [LGPL v3 License](https://tldrlegal.com/license/gnu-lesser-general-public-license-v3-%28lgpl-3%29)

You can do whatever you want with this code as long as you include my full name (Ricardo Guerrero Gómez-Olmedo), my email (ricgu8086@gmail.com) and a link to this repo ([https://github.com/ricgu8086/vAlfred-2.0](https://github.com/ricgu8086/vAlfred-2.)).

# <a name="Contact"></a> Contact #
If you have any question or you want to contact me, just send me an email to ricgu8086@gmail.com and I will answer you asap.

You can find me on Twitter at [@ricgu8086](https://twitter.com/ricgu8086)


# <a name="Legal"></a> Legal #

As the logo of this project is a derivative work of others I want to credit the autorship of the sources to: 


- Freepik from [www.flaticon.com](www.flaticon.com)
- Raspberry Pi by stating that “Raspberry Pi is a trademark of the Raspberry Pi Foundation”. I'm not related with Raspberry Pi Foundation, nor this software does.