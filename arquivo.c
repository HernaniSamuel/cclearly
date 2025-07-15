#include <stdio.h>
#include <stdlib.h>

#define MAX 10

typedef struct {
    int id;
    char nome[50];
} Pessoa;

void imprimir(Pessoa *p) {
    printf("ID: %d, Nome: %s\n", p->id, p->nome);
}

int fatorial(int n) {
    if (n <= 1) return 1;
    return n * fatorial(n - 1);
}

int main() {
    Pessoa *p = malloc(sizeof(Pessoa));
    if (!p) goto erro;

    p->id = 42;
    snprintf(p->nome, 50, "Zé do Ponteiro");

    imprimir(p);

    for (int i = 0; i < MAX; i++) {
        printf("%d! = %d\n", i, fatorial(i));
    }

    int opcao = 2;
    switch (opcao) {
        case 1:
            printf("Escolheu 1\n");
            break;
        case 2:
            printf("Escolheu 2\n");
            break;
        default:
            printf("Outra opção\n");
    }

    free(p);
    return 0;

erro:
    fprintf(stderr, "Erro de alocação!\n");
    return 1;
}
