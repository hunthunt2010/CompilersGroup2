// language example 0
const int a = 1;
int x = 1<<a;
int y, z = 3;

// Erroneously try to change a
a = 5;

y = z - x;
if ( y <= 0 ) {
   z = (x+2) + z*z ;
} else {
   z = z / y;
}

return z;
