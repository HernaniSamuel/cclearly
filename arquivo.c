#include <stdio.h>

int main() {
    int x = 1, y = 2;

    if (x > 0)
        printf("if sem chaves\n");

    else if (y > 0)
        printf("else if sem chaves\n");

    else
        printf("else sem chaves\n");

    while (x < 3)
        x++;

    do
        y++;
    while (y < 5);

    for (int i = 0; i < 3; i++)
        printf("for sem chaves: %d\n", i);

    switch (x)
        case 1:
            printf("case sem chaves\n");

    if (x > 0)
        if (y > 0)
            printf("nested if sem chaves\n");
        else
            printf("else do if interno\n");

    return 0;
}
