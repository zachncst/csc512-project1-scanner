    #include <stdio.h> 
    #define read(x) scanf("%d\n", &x) 
    #define write(x) printf("%d\n", x)
   // function foo 
    void foo() { 
        int a; 
        read(a); 
        write(a);
	a = "fun!";
	if(a>=0 && a < 0 ||a>2 ) {
        	read(a);
        } 
    }

    int main() { 
        foo(); 
    }
