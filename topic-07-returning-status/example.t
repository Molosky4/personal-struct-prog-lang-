print 2+2;
print 3+3;
print 4+4;
y = 5;
x = 6;
print x+y;
if (1==1) { 
    print 2+2;
    x = 5
};
if (1==2) { 
    x = 5
}
else {
    x = 6
};
print x;
x = 0;
while (x < 14) {
    x = x + 1
};
print x;
print "Hello!";
print "My dog is " + "Dorothy";

x = 1;
while (x < 10) {
    x = x + 1;
    print(x);
    if (x == 5) {
        break
    }
};
print("should see 5");
print x;

y = 0;
x = 0;
                                 while (x < 10) {
    x = x + 1;
    if (x > 8) {
        continue;
    };
    y = y + 1
};
print("Should see 8");
print y;

assert true, "this should not appear";
assert false, "this should appear";
