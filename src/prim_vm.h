#ifndef PRIM_VM_H
#define PRIM_VM_H

#include <stdint.h>
#include <stdbool.h>

// Opcode constants (matching prim_bytecode.prim)
typedef enum {
    OP_LOAD_CONST = 0,
    OP_LOAD_NAME = 1,
    OP_STORE_NAME = 2,
    OP_BINARY_ADD = 3,
    OP_BINARY_SUB = 4,
    OP_BINARY_MUL = 5,
    OP_BINARY_DIV = 6,
    OP_BINARY_MOD = 7,
    OP_BINARY_EQ = 8,
    OP_BINARY_NE = 9,
    OP_BINARY_LT = 10,
    OP_BINARY_GT = 11,
    OP_BINARY_LE = 12,
    OP_BINARY_GE = 13,
    OP_BINARY_AND = 14,
    OP_BINARY_OR = 15,
    OP_UNARY_NEG = 16,
    OP_UNARY_NOT = 17,
    OP_JUMP_ABSOLUTE = 18,
    OP_JUMP_IF_FALSE_OR_POP = 19,
    OP_POP_JUMP_IF_TRUE = 20,
    OP_POP_JUMP_IF_FALSE = 21,
    OP_CALL_FUNCTION = 22,
    OP_RETURN_VALUE = 23,
    OP_POP_TOP = 24,
    OP_HALT = 255
} OpCode;

typedef enum {
    VAL_NULL,
    VAL_BOOL,
    VAL_NUMBER,
    VAL_OBJ
} ValueType;

typedef struct Obj {
    ValueType type;
    bool is_marked;
    struct Obj* next;
} Obj;

typedef struct {
    ValueType type;
    union {
        bool boolean;
        double number;
        Obj* obj;
    } as;
} Value;

typedef struct {
    Obj obj;
    char* chars;
    int length;
} ObjString;

#define STACK_MAX 256

typedef struct {
    uint8_t* ip;
    Value stack[STACK_MAX];
    Value* stack_top;
    
    Obj* objects; // Linked list of all allocated objects
    int objects_count;
    int gc_threshold;
    
    Value* constants;
    int constants_count;
} VM;

void initVM(VM* vm);
void freeVM(VM* vm);
int runVM(VM* vm, uint8_t* bytecode);
void collectGarbage(VM* vm);

#endif
