#include <FastLED.h>

#define N_LEDS 52 // Number of LEDs
#define BAUD_RATE 115200
#define PIN 4
#define PRINTSERIAL 0 // mettre à 1 pour print les infos de LEDs, 0 sinon

// instantiation du tableau de LEDs
// cf. wiki pour plus d'infos https://github.com/FastLED/FastLED/wiki
CRGB led_strip[N_LEDS];

// initialisation de la String qui va encapsuler les messages reçus
String read_string="";

// variables dans lesquelles on va récupérer les valeurs de couleurs et l'ID d'une LED
int ledid, blue, green, red;

// les variables ci-dessous contiendront les positions des délimiteurs dans les strings
// prev_semi_column_0 et semicolumn_0 délimitent le début et la fin d'une LED
// les comma permettent de séparer l'ID de LED ainsi que le R, G et B
int prev_semicolumn_0;
int semicolumn_0;
int comma_0, comma_1, comma_2;

void setup()
{
 // initilisation du lien série (baud rate et timeout)
 Serial.begin(BAUD_RATE);
 Serial.setTimeout(60); // modifier ça si on veut que ça aille encore plus vite la boucle. Mais attention à la valeur limite (TBD).

 // initialisation de la bande de LEDs
 FastLED.addLeds<WS2812, PIN, GRB>(led_strip, N_LEDS);
}

void loop(){

  // on lit le message reçu jusqu'au délimiteur "!" (TBC : si le message ne contient pas de délimiteur ça marche aussi ?)
  String read_string = Serial.readStringUntil('!');
  if (PRINTSERIAL){
    Serial.println(read_string);
  }
  // Message format: LED_ID,R,G,B;LED_ID,R,G,B;LED_ID,R,G,B;...;LED_ID,R,G,B;
  if (read_string.length() > 1) {
    prev_semicolumn_0 = 0;
    comma_2 = -1;
    int i = 0;
    while (i < N_LEDS){
      // on trouve la position des délimiteurs qui suivent (1 ; et 3 ,) pour décoder la LED suivante
      semicolumn_0 = read_string.indexOf(";",prev_semicolumn_0+1);
      comma_0 = read_string.indexOf(",",comma_2+1);
      comma_1 = read_string.indexOf(",",comma_0+1);
      comma_2 = read_string.indexOf(",",comma_1+1);
      if (prev_semicolumn_0 != 0) {
        prev_semicolumn_0 += 1;
      }
      
      // à partir de la position des délimiteurs on récupère le numéro de LED et son RGB
      ledid = read_string.substring(prev_semicolumn_0, comma_0).toInt();
      red = read_string.substring(comma_0 + 1, comma_1).toInt();
      green = read_string.substring(comma_1 + 1, comma_2).toInt();
      blue = read_string.substring(comma_2 + 1, semicolumn_0).toInt();

      // à partir des infos récupérées on set la couleur de la led
      led_strip[ledid] = CRGB(red, green, blue);

      if (PRINTSERIAL) {
        Serial.print(i);
        Serial.print(' ');
        Serial.print(ledid);
        Serial.print(' ');
        Serial.print(red);
        Serial.print(' ');
        Serial.print(green);
        Serial.print(' ');
        Serial.print(blue);
        Serial.print(' ');
        Serial.println("SPLIT ");
      }
      
      prev_semicolumn_0 = semicolumn_0;
      i+=1;
    }
    
  }
  read_string="";
  // Update de toute la bande de LEDs 
  led_strip[ledid] = CRGB(0,0,0);
  FastLED.show();
}
