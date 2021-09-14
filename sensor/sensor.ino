#include "DHT.h"

int pin_10 = 7;
int pin_2_5 = 8;
unsigned long duration_10;
unsigned long duration_2_5;
unsigned long starttime;
unsigned long sampletime_ms = 30000; //sampe 30s ;
unsigned long lowpulseoccupancy_10 = 0;
unsigned long lowpulseoccupancy_2_5 = 0;
float ratio_10 = 0;
float ratio_2_5 = 0;
float concentration_10 = 0;
float concentraction_2_5 = 0;

#define DHTTYPE DHT11
#define DHTPIN 6
DHT dht(DHTPIN, DHTTYPE);

void setup() 
{
    Serial.begin(9600);
    dht.begin();
    pinMode(pin_10,INPUT);
    pinMode(pin_2_5, INPUT);
    starttime = millis(); //get the current time;
}

void loop() 
{
    duration_10 = pulseIn(pin_10, LOW);
    duration_2_5 = pulseIn(pin_2_5, LOW);
    lowpulseoccupancy_10 = lowpulseoccupancy_10 + duration_10;
    lowpulseoccupancy_2_5 = lowpulseoccupancy_2_5 + duration_2_5;

    if ((millis()-starttime) > sampletime_ms) //if the sampel time > 30s
    {
        ratio_10 = lowpulseoccupancy_10 / (sampletime_ms * 10.0);
        ratio_2_5 = lowpulseoccupancy_2_5 / (sampletime_ms * 10.0);
        
        concentration_10 = 1.1 * pow(ratio_10, 3) - 3.8 * pow(ratio_10, 2) + 520 * ratio_10 + 0.62; // using spec sheet curve
        concentraction_2_5 = 1.1 * pow(ratio_2_5, 3) - 3.8 * pow(ratio_2_5, 2) + 520 * ratio_2_5 + 0.62; // using spec sheet curve

        float humidity = dht.readHumidity();
        float temperature = dht.readTemperature();  
        
        Serial.print("{\"PM10\": ");
        Serial.print(concentration_10);
        Serial.print(", \"PM2.5\": ");
        Serial.print(lowpulseoccupancy_2_5);
        Serial.print(", \"Temp\": ");
        Serial.print(temperature);
        Serial.print(" , \"Humidity\": ");
        Serial.print(humidity);
        Serial.print("}");
        Serial.println();
        
        lowpulseoccupancy_10 = 0;
        lowpulseoccupancy_2_5 = 0;
        starttime = millis();
    }
}
