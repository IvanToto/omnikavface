#include <Wire.h> 
#include "DHT.h"
#include <VL53L0X.h>

VL53L0X sensor;
DHT dht(4, DHT22);

int incoming = 0;
int counter = 0;
int button = 0;
float dist = 0;  
float temp = 0; 
float tempc = 0; 
float senal = 0;
float ambhum = 0;
float ambtemp = 0;  

void setup()
{
  Wire.begin();
  Serial.begin(115200);
  sensor.init();
  sensor.setTimeout(500);
  dht.begin();
  //sensor.setMeasurementTimingBudget(50000);//Para incrementar la presición (reducir ruido) del sensor subir hasta 200ms (200000us)
  pinMode(3,OUTPUT); //Buzzer
  analogWrite(3,0);
  pinMode(2,OUTPUT);//Rele
  digitalWrite(2,1);
  pinMode(5,OUTPUT);//PWM LUCES
  analogWrite(5,0);
  pinMode(6,OUTPUT);//PWM BOMBA
  analogWrite(6,0);
  
  delay(500);
  }
 
void loop(){
  
  dist = sensor.readRangeSingleMillimeters()/10-1; //Toma 50ms segun lo programado. 
  //if (sensor.timeoutOccurred()) {dist = 99;}
  if (dist>99){dist = 99;}
  if (dist<10){//se añade esta condición para verificar que el laser fue bloqueado y no es ruido.
    delay(100);
    dist = 99;
    dist = sensor.readRangeSingleMillimeters()/10-1; //Toma 50ms segun lo programado. 
    } 
  if (dist<8 && button == 0){ 
   button = 1;
   //(0,temp,button,dist,senal,ambtemp,ambhum,0)
   String orden = (String)"(0,"+temp+","+button+","+dist+","+senal+","+ambtemp+","+ambhum;
   Serial.println(orden);
   counter = 0;  
   tone(3,2536,500);
    }   
  if (dist>8){button = 0;}

  if (Serial.available()>0){
    incoming = Serial.read();
    } else {incoming = 0;}
    
  if (incoming == 97){
    tempget(5000);
    //(0,temp,button,dist,senal,ambtemp,ambhum,0)
    incoming = 0;
    String orden = (String)"(0,"+temp+","+button+","+dist+","+senal+","+ambtemp+","+ambhum;
    Serial.println(orden);
    }//Toma temperatura
  if (incoming == 98){tone(3,2536,500);incoming = 0;}//Enciende buzzer ,b
  if (incoming == 99){digitalWrite(2,0); counter = 10;incoming = 0;}//Enciende Rele ,c
  if (incoming == 100){analogWrite(5,200); counter = 0;incoming = 0;}//Enciende Luz LV1 ,d
  if (incoming == 101){analogWrite(5,200); counter = -20;incoming = 0;}//Enciende Luz LV2 ,e
  if (incoming == 102){analogWrite(6,250); counter = 0;incoming = 0;}//Enciende Bomba LV1 ,f
  if (incoming == 103){analogWrite(6,250); counter = 10;incoming = 0;}//Enciende Bomba LV2 ,g
  if (incoming == 104){analogWrite(6,250); counter = 15;incoming = 0;}//Enciende Bomba LV2 ,h
  if (incoming == 105){analogWrite(5,250); incoming = 0;}//Enciende Fijo Lampara LV1 ,i
  if (incoming == 106){analogWrite(5,100); incoming = 0;}//Enciende Fijo Lampara LV2 ,j
  if (incoming == 107){analogWrite(5,20); incoming = 0;}//Enciende Fijo Lampara LV3, k
  if (incoming == 108){analogWrite(5,0); incoming = 0;}//Apaga Lampara ,l
  
  if(counter>19){
    counter = 0;
    digitalWrite(2,1); //Apaga Rele
    //analogWrite(5,0); //Apaga Luz
    analogWrite(6,0); //Apaga Bomba
    }
  counter++;
  delay(100);
}

void tempget(int sensibilidad){
  float raw = 0.0; 
  senal = 0.0;
  
  for (int i=0;i<sensibilidad;i++){raw = analogRead(3) + raw;}    
  senal = raw/sensibilidad + senal;
  raw = 0;
  delay(200);

  for (int i=0;i<sensibilidad;i++){raw = analogRead(3) + raw;}     
  senal = raw/sensibilidad + senal;
  raw = 0;
  delay(200);  

  for (int i=0;i<sensibilidad;i++){raw = analogRead(3) + raw;}    
  senal = raw/sensibilidad + senal;
  raw = 0;
  delay(200);
  
  senal = senal/3;
  temp = 0.6559*senal-132.04;
  tempc = 0.05*senal - 20;
  ambhum = dht.readHumidity();
  ambtemp = dht.readTemperature();
  //temp = 0.0375*senal - 3.75;
  //temp = 0.0375*senal - 5;
  //temp = ambcalib1*senal - ambcalib2;
  //temp = 0.05*senal - 17.5;
  //tempc = 0.05*senal - 17.5;
  //if(temp<35.9){temp = 35.9;}
  //if(temp>41){temp = 40.9;}
  //if(tempc<35.9){tempc = 35.9;}
  //if(tempc>41){tempc = 40.9;}
  //tempc = 0.11*senal - 82; 
  //temp = 0.12*senal - 92; 
  //temp = 0.1*senal - 71; 
  //temp = 0.119*senal - 85.835;
  //temp = 0.0709*senal-40;
  //temp = 0.0709*senal-40.496; //Modelo de temperatura para 12bits 3.3V
  //tempc = 0.0709*senal-40.496 + (0.1*dist-1); //Modelo de temperatura para 12bits 3.3V con compensacion de distancia
  //temp = 0.6559*senal-132.04; //Modelo de temperatura para 10bits 5V
  }
