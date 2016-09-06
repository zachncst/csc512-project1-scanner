#include <stdio.h>
#define read(x) scanf("%d",&x)
#define write(x) printf("%d\n",x)
#define print(x) printf(x)

int cs512array[16];

void cs512initialize_array(void)
{
    int cs512idx, cs512bound;
    cs512bound = 16;

    cs512idx = 0;
    while (cs512idx < cs512bound)
    {
	cs512array[cs512idx] = -1;
	cs512idx = cs512idx + 1;
    }
}

int cs512fib(int cs512val)
{
    if (cs512val < 2)
    {
	return 1;
    }
    if (cs512array[cs512val] == -1)
    {
	cs512array[cs512val] = cs512fib(cs512val - 1) + cs512fib(cs512val - 2);
    }

    return cs512array[cs512val];
}

int main(void)
{
    int cs512idx, cs512bound;
    cs512bound = 16;

    cs512initialize_array();
    
    cs512idx = 0;

    print("The first few digits of the Fibonacci sequence are:\n");
    while (cs512idx < cs512bound)
    {
	write(cs512fib(cs512idx));
	cs512idx = cs512idx + 1;
    }
}
