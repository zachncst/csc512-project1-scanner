#include <stdio.h>
#define read(x) scanf("%d",&x)
#define write(x) printf("%d\n",x)

int add(int a) {
  int b;
  read(b);
  return a+b;
}

int main() {
  int a, b;
  read(a);
  write(add(a));
}
