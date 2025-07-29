import os
from source.xml2clearly.translate import translate
from source.xml2clearly.xml_manager import generate_tag

def test_complex_variables():
    xml_path = os.path.join('tests', 'xml_samples', 'declarations', 'variables.xml')
    with open(xml_path, 'r', encoding='utf-8') as f:
        xml_content = f.read()

    expected_output = """
// Declaracoes simples
a: int
b: float = 3.14
c: char = 'x'   // char com comentario em linha

// Multiplas declaracoes
x: double, y: double = 2.71, z: double

// Modificadores variados
ci: const int = 10
ef: extern float
sc: static char
vui: volatile unsigned int = 0

// Arrays
arr1: array(5, int)
matrix: array(2, array(3, float))
str: array(_, char) = "clearly!"

// Inicializacao parcial (valido em C99+ ou gcc extension)
mixed: array(3, int) = [1, 2]

// Combinando modificadores e arrays
table: array(4, const static double) = [1.1, 2.2, 3.3, 4.4]

// Comentario em bloco
/*
 Declaracao complexa com tudo junto
*/
complex: const extern double = 9.81

// Multidecl modificado
u1: static unsigned char = 1, u2: static unsigned char, u3: static unsigned char = 3

    """.strip()

    tag = generate_tag(xml_path)
    actual_output = translate(tag).strip()

    assert actual_output == expected_output


# C code used as input:
"""
// Declaracoes simples
int a;
float b = 3.14;
char c = 'x';  // char com comentario em linha

// Multiplas declaracoes
double x, y = 2.71, z;

// Modificadores variados
const int ci = 10;
extern float ef;
static char sc;
volatile unsigned int vui = 0;

// Arrays
int arr1[5];
float matrix[2][3];
char str[] = "clearly!";

// Inicializacao parcial (valido em C99+ ou gcc extension)
int mixed[3] = {1, [2]=3};

// Combinando modificadores e arrays
const static double table[4] = {1.1, 2.2, 3.3, 4.4};

// Comentario em bloco
/*
 Declaracao complexa com tudo junto
*/
const extern double complex = 9.81;

// Multidecl modificado
static unsigned char u1 = 1, u2, u3 = 3;
"""