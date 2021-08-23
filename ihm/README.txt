==================================================================
==================================================================
================== TIMINGS METHODES SCREENSHOT ===================
==================================================================
==================================================================
(~85ms sur arduino pour traiter 45 leds - réception - calcul - envoi aux leds)

pyautogui
Temps de screen
0.051774323940277096
Temps récupération données
0.031855688095092774
Temps mise en forme données
7.403564453125e-05
Temps envoi des données en serial
0.05727665662765503

MOYENNE PYAUTOGUI : 141 ms
Conversion PIL.Image vers numpy array = 20 ms
==================================================================

mss
Temps de screen
0.048643184185028075
Temps récupération données
0.011036076545715333
Temps mise en forme données
6.401443481445312e-05
Temps envoi des données en serial
0.05722278213500977

MOYENNE MSS : 117 ms
Conversion mss.screenshot.ScreenShot vers numpy array = 4 ms


==================================================================
==================================================================
========================== PLAN DE TEST ==========================
==================================================================
==================================================================

1er test : script arduino "test_ledstrip" pour valider le controle des leds
2ème test : script arduino "screen_to_ledstrip_fast" et envoyer via moniteur série des données complètes au format id,r,g,b;...;!
3ème test : python testserial.py (surement des ajustements à faire sur le script pour test l'envoi de données format id,r,g,b; depuis python)
4ème test : python ambi_fixe.py, tester avec différentes couleurs que la bande de led est bien controlée
5ème test : python screencap.py pour valider le suivi de couleurs de l'écran (tester sur bande non collée/découpée à l'écran, en vérifiant bien que les premières LEDs correspondent aux bonnes valeurs attendues)
6ème test : jouer avec l'IHM pour valider le tout
7ème test (ou 6ème) : coller les bandes derrière l'écran et valider la bonne gestion de la position des LEDs

=> une fois tout ça OK, réaliser un .exe de l'IHM pour avoir un truc bien propre (cf ce lien : https://stackoverflow.com/questions/5888870/how-do-i-compile-a-pyqt-script-py-to-a-single-standalone-executable-file-for)



==================================================================
==================================================================
========================== TODO/TOTHINK ==========================
==================================================================
==================================================================

=> recoder screencap.py (et les funcs.py) en C pour aller plus vite.
code C comm sérial : https://batchloaf.wordpress.com/2013/02/13/writing-bytes-to-a-serial-port-in-c/

coder l'envoi des donnés en binaire ? 
6 à 8 bits pour l'ID, 8 bits pour R, 8 bits pour G, 8 bits pour B, etc...
nécessitera d'ajuster le code arduino (notamment réception.. comment faire ?)

peut-être tester en python d'abord ?
packet = bytearray()
packet.append(0x41)
packet.append(0x42)
packet.append(0x43)
ser.write(packet)

pour arduino, une fois le byte reçu : 
byte binary_data = 0b11000101;
byte ID_variable = (binary_data & 0xF0) >> 4; //will be equal to 0b1100
byte another_var =  binary_data & 0x0F;       //will be equal to 0b0101






