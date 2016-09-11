    #include <stdio.h> 
    #define read(x) scanf("%d\n", &x) 
    #define write(x) printf("%d\n", x)
   // function foo 
    void cs512foo() { 
        int cs512a; 
        read(cs512a); 
        write(cs512a);
	cs512a = "fun!";
	if(cs512a>=0 && cs512a < 0 ||cs512a>2 ) {
        	read(cs512a);
        } 
    }

    int main() { 
        cs512foo(); 
    }
