#include <FastLED.h>

#define N_LEDS 51 // Number of LEDs
#define BAUD_RATE 115200
#define PIN 4

// instantiation du tableau de LEDs
// cf. wiki pour plus d'infos https://github.com/FastLED/FastLED/wiki
CRGB led_strip[N_LEDS];

const byte num_bytes = (N_LEDS+1)*3;
byte received_bytes[num_bytes];

boolean dataReady = false;

int ledid, red, green, blue;

void setup() {
    // initilisation du lien série
    Serial.begin(BAUD_RATE);

    // initialisation de la bande de LEDs
    FastLED.addLeds<WS2812, PIN, GRB>(led_strip, N_LEDS);
}

void loop() {
    // on récupère les bytes entrant
    receiveData();
    // quand on a tout récupéré "dataReady" passe à true et on update les LEDs.
    if (dataReady == true) {
        for (int i = 0; i < num_bytes; i+=3) {
            // on traite 3 valeurs à la fois dans cette boucle (RGB)  
            ledid = (int)(i/3);
            red = received_bytes[i];
            green = received_bytes[i+1];
            blue = received_bytes[i+2];     

            // à partir des infos récupérées on set la couleur de la led
            led_strip[ledid] = CRGB(red, green, blue);
        }

        // Update de toute la bande de LEDs 
        FastLED.show();
        // on est prêts à avoir un nouveau batch de données
        dataReady = false;
    }
}

void receiveData() {
    static boolean recvInProgress = false;
    static byte idx = 0;
    byte start_byte = 0x01; // la valeur 1 ne peut pas être utilisée sur les LEDs
    byte end_byte = 0x02; // la valeur 2 ne peut pas être utilisée sur les LEDs
    byte datain;
   
    while (Serial.available() > 0 && dataReady == false) {
        datain = Serial.read();

        if (recvInProgress == true) {
            if (datain != end_byte) {
                received_bytes[idx] = datain;
                idx++;
                if (idx > num_bytes) {
                    idx = num_bytes;
                }
            }
            else {
                recvInProgress = false;
                idx = 0;
                dataReady = true;
            }
        }

        else if (datain == start_byte) {
            recvInProgress = true;
        }
    }
}
