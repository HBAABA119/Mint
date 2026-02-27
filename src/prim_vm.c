#include "prim_vm.h"
#include <stdio.h>
#include <stdlib.h>
#include <stdbool.h>
#include <string.h>

void initVM(VM* vm) {
    vm->stack_top = vm->stack;
    vm->objects = NULL;
    vm->objects_count = 0;
    vm->gc_threshold = 1024; // Simple threshold
    vm->constants = NULL;
    vm->constants_count = 0;
}

void freeObject(Obj* object) {
    switch (object->type) {
        case VAL_OBJ: {
            ObjString* string = (ObjString*)object;
            free(string->chars);
            free(string);
            break;
        }
        default:
            break;
    }
}

void freeVM(VM* vm) {
    Obj* object = vm->objects;
    while (object != NULL) {
        Obj* next = object->next;
        freeObject(object);
        object = next;
    }
    
    if (vm->constants != NULL) {
        free(vm->constants);
    }
}

void markObject(Obj* object) {
    if (object == NULL || object->is_marked) return;
    object->is_marked = true;
}

void markValue(Value value) {
    if (value.type == VAL_OBJ) {
        markObject(value.as.obj);
    }
}

void markRoots(VM* vm) {
    // Mark stack
    for (Value* slot = vm->stack; slot < vm->stack_top; slot++) {
        markValue(*slot);
    }
    
    // Mark constants
    for (int i = 0; i < vm->constants_count; i++) {
        markValue(vm->constants[i]);
    }
}

void traceReferences(VM* vm) {
    // In a more complex VM, we would trace objects inside other objects
}

void sweep(VM* vm) {
    Obj* previous = NULL;
    Obj* object = vm->objects;
    while (object != NULL) {
        if (object->is_marked) {
            object->is_marked = false;
            previous = object;
            object = object->next;
        } else {
            Obj* unreached = object;
            object = object->next;
            if (previous != NULL) {
                previous->next = object;
            } else {
                vm->objects = object;
            }
            freeObject(unreached);
            vm->objects_count--;
        }
    }
}

void collectGarbage(VM* vm) {
    printf("-- GC start\n");
    markRoots(vm);
    traceReferences(vm);
    sweep(vm);
    vm->gc_threshold = vm->objects_count * 2;
    printf("-- GC end\n");
}

Obj* allocateObject(VM* vm, size_t size, ValueType type) {
    if (vm->objects_count >= vm->gc_threshold) {
        collectGarbage(vm);
    }
    
    Obj* object = (Obj*)malloc(size);
    object->type = type;
    object->is_marked = false;
    object->next = vm->objects;
    vm->objects = object;
    vm->objects_count++;
    return object;
}

ObjString* copyString(VM* vm, const char* chars, int length) {
    char* heapChars = malloc(length + 1);
    memcpy(heapChars, chars, length);
    heapChars[length] = '\0';
    
    ObjString* string = (ObjString*)allocateObject(vm, sizeof(ObjString), VAL_OBJ);
    string->chars = heapChars;
    string->length = length;
    return string;
}

void push(VM* vm, Value value) {
    *vm->stack_top = value;
    vm->stack_top++;
}

Value pop(VM* vm) {
    vm->stack_top--;
    return *vm->stack_top;
}

int runVM(VM* vm, uint8_t* bytecode) {
    vm->ip = bytecode;
    
    for (;;) {
        uint8_t instruction = *vm->ip++;
        switch (instruction) {
            case OP_LOAD_CONST: {
                uint8_t const_idx = *vm->ip++;
                push(vm, vm->constants[const_idx]);
                break;
            }
            case OP_BINARY_ADD: {
                Value b = pop(vm);
                Value a = pop(vm);
                if (a.type == VAL_NUMBER && b.type == VAL_NUMBER) {
                    push(vm, (Value){VAL_NUMBER, {.number = a.as.number + b.as.number}});
                } else {
                    printf("Runtime Error: Invalid operands for +\n");
                    return 1;
                }
                break;
            }
            case OP_BINARY_SUB: {
                Value b = pop(vm);
                Value a = pop(vm);
                if (a.type == VAL_NUMBER && b.type == VAL_NUMBER) {
                    push(vm, (Value){VAL_NUMBER, {.number = a.as.number - b.as.number}});
                } else {
                    printf("Runtime Error: Invalid operands for -\n");
                    return 1;
                }
                break;
            }
            case OP_BINARY_MUL: {
                Value b = pop(vm);
                Value a = pop(vm);
                if (a.type == VAL_NUMBER && b.type == VAL_NUMBER) {
                    push(vm, (Value){VAL_NUMBER, {.number = a.as.number * b.as.number}});
                } else {
                    printf("Runtime Error: Invalid operands for *\n");
                    return 1;
                }
                break;
            }
            case OP_BINARY_DIV: {
                Value b = pop(vm);
                Value a = pop(vm);
                if (a.type == VAL_NUMBER && b.type == VAL_NUMBER) {
                    if (b.as.number == 0) {
                        printf("Runtime Error: Division by zero\n");
                        return 1;
                    }
                    push(vm, (Value){VAL_NUMBER, {.number = a.as.number / b.as.number}});
                } else {
                    printf("Runtime Error: Invalid operands for /\n");
                    return 1;
                }
                break;
            }
            case OP_HALT:
            case OP_RETURN_VALUE: {
                Value result = pop(vm);
                if (result.type == VAL_NUMBER) {
                    printf("Final result: %g\n", result.as.number);
                } else if (result.type == VAL_BOOL) {
                    printf("Final result: %s\n", result.as.boolean ? "true" : "false");
                } else if (result.type == VAL_OBJ) {
                    printf("Final result: %s\n", ((ObjString*)result.as.obj)->chars);
                } else {
                    printf("Final result: null\n");
                }
                return 0;
            }
            default:
                printf("Runtime Error: Unknown opcode %d\n", instruction);
                return 1;
        }
    }
}

int main(int argc, char* argv[]) {
    VM vm;
    initVM(&vm);
    
    // Setup constants
    vm.constants = malloc(sizeof(Value) * 3);
    vm.constants[0] = (Value){VAL_NUMBER, {.number = 10.0}};
    vm.constants[1] = (Value){VAL_NUMBER, {.number = 20.0}};
    
    // Allocate a string object via copyString
    ObjString* str = copyString(&vm, "Prim VM Test Success!", 21);
    vm.constants[2] = (Value){VAL_OBJ, {.obj = (Obj*)str}};
    vm.constants_count = 3;
    
    uint8_t bytecode[] = {
        OP_LOAD_CONST, 0,
        OP_LOAD_CONST, 1,
        OP_BINARY_ADD,
        OP_POP_TOP,
        OP_LOAD_CONST, 2,
        OP_HALT
    };
    
    int result = runVM(&vm, bytecode);
    
    freeVM(&vm);
    return result;
}
