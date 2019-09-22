#include <stdio.h>
#include <unistd.h>
#include <stdlib.h>
#include <string.h>

#ifndef ADMIN_KEY
#define ADMIN_KEY "misconfigured"
#endif

typedef struct {
  char yeet[0x13];
  int id;
} Result;

char* blue;
int blue_dead;
char* red;
int red_dead;
int size = 0x80;

void kill_blue() {
  if (blue != NULL) {
    free(blue);
    blue_dead = 1;
  }
}

void kill_red() {
  if (red != NULL) {
    free(red);
    red_dead = 1;
  }
}

void erase() {
  blue = NULL;
  red = NULL;
}

void give_me_blue_data() {
  if (blue == NULL) { blue = malloc(size); blue_dead = 0; }
  if (blue_dead == 1) return;
  puts("Give me blue data");
  int n_read = read(0, blue, size - 1);
  blue[n_read] = 0;
}

void give_me_red_data() {
  if (red == NULL) { red = malloc(size); red_dead = 0; }
  if (red_dead == 1) return;

  puts("Give me red data");
  int n_read = read(0, red, size - 1);
  red[n_read] = 0;
}

void show_data() {
  if (red) puts(red);
  if (blue) puts(blue);
}


int main() {
  setvbuf(stdout, NULL, _IONBF, 0);
  setvbuf(stdin, NULL, _IONBF, 0);
  setvbuf(stderr, NULL, _IONBF, 0);

  char buf[0xff];
  int n_read;

  puts("This is a mysql server");
  n_read = read(0, buf, strlen(ADMIN_KEY));
  buf[n_read] = 0;
  if (strcmp(buf, ADMIN_KEY) != 0) {
    puts("You don't belong here.");
    exit(1);
  };

  puts("Welcome to the actual server! CTF 2Fort Instant Respawn 24/7!");

  char* user_data = malloc(0x50);

  for(;;) {
    puts("Give me a choice:");
    n_read = read(0, user_data, 0x50 - 1);
    int choice = atoi(user_data);

    switch(choice) {
    case 0:
      erase();
      break;
    case 1:
      give_me_red_data();
      give_me_blue_data();
      break;
    case 2:
      give_me_blue_data();
      give_me_red_data();
      break;
    case 3:
      kill_blue();
      kill_red();
      break;
    case 4:
      kill_red();
      kill_blue();
      break;
    case 5:
      show_data();
      break;
    case 6:
      size = 0x50;
      break;
    default:
      puts("Bye!");
      exit(0);
    }
  }
}

/**
 * Double free
 * do 1
 * read random into both
 * do 3 twice
 * then do 1 
 **/