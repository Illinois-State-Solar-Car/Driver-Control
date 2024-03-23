
/**
 * The code for the driver control unit of the ISU Solar Car.
 * Used for:
 *  - Reading in canbus data from the motor controller
 *  - Displaying power usage information to the driver
 *  - Reading the analog input from the throttle pedal to send to the motor controller
 * 
 * 
 * Hopefully we can implement Cruise Control later...
 *  need to figure out how to find out when the mechanical brakes are pressed
 *  can probably do that with tapping into the brake lights
 *  
 */

/**
 * PIN INFORMATION :
 * A0 - reads in the throttle input from the driver
 * D4 - checks if regen is active
 * D5 - Value of True here will activate the forward gear
 * D6 - Value of True will activate the reverse gear
 * 17 - canbus pin
 * Don't need to specify neutral if both forward and reverse read false
 * If (for some reason) both forward and reverse would read as true, the car will just stay in forward
 */

//canbus imports
#include <mcp_can.h>
#include <mcp_can_dfs.h>

//more canbus stuff
const int SPI_CS_PIN = 17;

MCP_CAN CAN(SPI_CS_PIN);

//pin definitions
const int pedalPin = A0;
const int regenPin = 9;
const int forwardPin = 8;
const int reversePin = 3;

//variable definitions
int pedalInValue;
float pedalPercent;
bool regen;
bool forward;
bool reverse;

double mph;
double rpm;

//please have relevant variable names, or the only relevant name will be the one on your tombstone
double maxRPM;
double maxRpmPercent;
double thrust;

void setup() {
  // put your setup code here, to run once

  //pin setups
  pinMode(regenPin, INPUT);
  pinMode(forwardPin, INPUT);
  pinMode(reversePin, INPUT);
}


unsigned char data[8];

void loop() {
  // put your main code here, to run repeatedly:

  //read in the driver inputs:
  pedalInValue = analogRead(pedalPin);    //get the raw value of the pedal input
  pedalPercent = (pedalInValue / 63500);  //turn that value into a percentage for later use
  if (pedalPercent < 0.05) {              //if pedal percent is minimal
    pedalPercent = 0;                     //assign it as zero
  }                                       //here to prevent any possible issues with the potentiometer and in case the driver is accidentally resting their foot on the pedal it provides a small buffer

  regen = digitalRead(regenPin);
  forward = digitalRead(forwardPin);
  if (forward) {  //the code to prevent both forward and reverse being true at the same time
    reverse = false;

  } else {
    reverse = digitalRead(reversePin);
  }


  //the power function makes the thrust into an exponential nonlinear curve
  //the *.9 prevents overloading the motor controller with amperage that would make it unhappy
  thrust = (pow(pedalPercent, 1.75)) * .9;

  if (regen) {  //regen should have highest priority 
    maxRPM = 0;
    maxRpmPercent = thrust;
  } else if (forward) {  //next we test forward
    maxRPM = 1000;
    maxRpmPercent = thrust;
  }

  else if (reverse) {  //then reverse
    maxRPM = -1000;
    maxRpmPercent = thrust;
  }

  else {  //if regen is off, and forward and negative are false, we are in neutral
    maxRPM = 0;
    maxRpmPercent = 0;
  }


  //float to byte arrays
  byte rpmBytes[sizeof(float)];
  byte percentBytes[sizeof(float)];
  memcpy(&rpmBytes, &maxRPM, sizeof(float));
  memcpy(&percentBytes, &maxRpmPercent, sizeof(float));

  //put the bytes into the data array
  data[0] = rpmBytes[0];
  data[1] = rpmBytes[1];
  data[2] = rpmBytes[2];
  data[3] = rpmBytes[3];
  data[4] = percentBytes[0];
  data[5] = percentBytes[1];
  data[6] = percentBytes[2];
  data[7] = percentBytes[3];


  CAN.sendMsgBuf(0x501, 0, 8, data);


  //wait a little bit
  delay(100);
}
