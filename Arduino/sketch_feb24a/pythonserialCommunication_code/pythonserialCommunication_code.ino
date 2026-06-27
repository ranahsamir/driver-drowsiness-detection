#include <Wire.h>
#include <LiquidCrystal_I2C.h>

LiquidCrystal_I2C lcd(0x27, 16, 2);

char state = '0';
char lastState = ' ';

// Pin Definitions
const int GREEN_LED = 13;
const int RED_LED = 12;
const int BUZZER_1 = 11;
const int BUZZER_2 = 10;  //Buzzer for customized-frequency tone 
const int GREEN_2 = 9;   // Added to match GREEN_LED functionality
const int RED_2 = 6;     // Added to match RED_LED functionality

unsigned long drowsyStartTime = 0; 
const unsigned long DANGER_THRESHOLD = 5000;

void setup() {
  lcd.init();
  lcd.backlight();

  pinMode(GREEN_LED, OUTPUT);
  pinMode(RED_LED, OUTPUT);
  pinMode(BUZZER_1, OUTPUT);
  pinMode(BUZZER_2, OUTPUT);
  pinMode(GREEN_2, OUTPUT);
  pinMode(RED_2, OUTPUT);

  Serial.begin(115200);

  lcd.setCursor(0, 0);
  lcd.print("System Ready");
  
  // Initialize both green LEDs to HIGH
  digitalWrite(GREEN_LED, HIGH); 
  digitalWrite(GREEN_2, HIGH);
}

void loop() {
  if (Serial.available() > 0) {
    state = Serial.read();
  }

  if (state != lastState) {
    lcd.clear();

    if (state == '1') {
      drowsyStartTime = millis();
      lcd.setCursor(0, 0);
      lcd.print("DROWSY ALERT!");
      
      // Turn off both green LEDs when drowsy
      digitalWrite(GREEN_LED, LOW);
      digitalWrite(GREEN_2, LOW);
    } 
    else if (state == '0') {
      lcd.setCursor(0, 0);
      lcd.print("Driver Active");
      
      //Green LEDs ON, Red LEDs OFF, Alerts OFF
      digitalWrite(GREEN_LED, HIGH);
      digitalWrite(GREEN_2, HIGH);
      digitalWrite(RED_LED, LOW);
      digitalWrite(RED_2, LOW);
      noTone(BUZZER_1);
      digitalWrite(BUZZER_2, LOW); 
    }
    lastState = state;
  }

  if (state == '1') {
    unsigned long duration = millis() - drowsyStartTime;
    
    if (duration > DANGER_THRESHOLD) {
      criticalAlert();
    } else {
      drowsyAlert();
    }
  }
}

void drowsyAlert() {
  // Blinking cycle for both red LEDs and buzzers
  digitalWrite(RED_LED, HIGH);
  digitalWrite(RED_2, HIGH);
  tone(BUZZER_1, 1000);
  digitalWrite(BUZZER_2, HIGH);
  delay(200);
  
  digitalWrite(RED_LED, LOW);
  digitalWrite(RED_2, LOW);
  noTone(BUZZER_1);
  digitalWrite(BUZZER_2, LOW);
  delay(200);
}

void criticalAlert() {
  lcd.setCursor(0, 1);
  lcd.print("!!! DANGER !!!");
  
  // Constant high alert for both red LEDs and buzzers when drowsy exceeded 5seconds 
  digitalWrite(RED_LED, HIGH);
  digitalWrite(RED_2, HIGH);
  tone(BUZZER_1, 3000);
  digitalWrite(BUZZER_2, HIGH);
}
