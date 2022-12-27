#include <iostream>
#include <string>
#include <cmath>
#include <sndfile.hh>
#include <fstream>


using namespace std;

// Sum of two numbers
extern "C" int add(int a, int b) {
  return a + b;
}

// Concatenate two strings
extern "C" string concat(string a, string b) {
  return a + b;
}




