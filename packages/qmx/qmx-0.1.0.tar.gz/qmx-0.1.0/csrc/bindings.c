#define PY_SSIZE_T_CLEAN
#include <Python.h>
#include "matmul.h"
#include <stdlib.h>

// Helper to convert Python list to C array
static float* list_to_float_array(PyObject* list, Py_ssize_t* size) {
    *size = PyList_Size(list);
    float* arr = (float*)malloc(*size * sizeof(float));
    for (Py_ssize_t i = 0; i < *size; i++) {
        arr[i] = (float)PyFloat_AsDouble(PyList_GetItem(list, i));
    }
    return arr;
}

static double* list_to_double_array(PyObject* list, Py_ssize_t* size) {
    *size = PyList_Size(list);
    double* arr = (double*)malloc(*size * sizeof(double));
    for (Py_ssize_t i = 0; i < *size; i++) {
        arr[i] = PyFloat_AsDouble(PyList_GetItem(list, i));
    }
    return arr;
}

static int32_t* list_to_int32_array(PyObject* list, Py_ssize_t* size) {
    *size = PyList_Size(list);
    int32_t* arr = (int32_t*)malloc(*size * sizeof(int32_t));
    for (Py_ssize_t i = 0; i < *size; i++) {
        arr[i] = (int32_t)PyLong_AsLong(PyList_GetItem(list, i));
    }
    return arr;
}

static int8_t* list_to_int8_array(PyObject* list, Py_ssize_t* size) {
    *size = PyList_Size(list);
    int8_t* arr = (int8_t*)malloc(*size * sizeof(int8_t));
    for (Py_ssize_t i = 0; i < *size; i++) {
        arr[i] = (int8_t)PyLong_AsLong(PyList_GetItem(list, i));
    }
    return arr;
}

// Python wrapper for float32 matmul
static PyObject* py_matmul_f32(PyObject* self, PyObject* args) {
    PyObject *A_list, *B_list;
    int64_t M, N, K;
    
    if (!PyArg_ParseTuple(args, "OOlll", &A_list, &B_list, &M, &N, &K)) {
        return NULL;
    }
    
    Py_ssize_t size_a, size_b;
    float* A = list_to_float_array(A_list, &size_a);
    float* B = list_to_float_array(B_list, &size_b);
    float* C = (float*)malloc(M * N * sizeof(float));
    
    matmul_f32(A, B, C, M, N, K);
    
    PyObject* result = PyList_New(M * N);
    for (int64_t i = 0; i < M * N; i++) {
        PyList_SET_ITEM(result, i, PyFloat_FromDouble(C[i]));
    }
    
    free(A);
    free(B);
    free(C);
    
    return result;
}

// Python wrapper for float64 matmul
static PyObject* py_matmul_f64(PyObject* self, PyObject* args) {
    PyObject *A_list, *B_list;
    int64_t M, N, K;
    
    if (!PyArg_ParseTuple(args, "OOlll", &A_list, &B_list, &M, &N, &K)) {
        return NULL;
    }
    
    Py_ssize_t size_a, size_b;
    double* A = list_to_double_array(A_list, &size_a);
    double* B = list_to_double_array(B_list, &size_b);
    double* C = (double*)malloc(M * N * sizeof(double));
    
    matmul_f64(A, B, C, M, N, K);
    
    PyObject* result = PyList_New(M * N);
    for (int64_t i = 0; i < M * N; i++) {
        PyList_SET_ITEM(result, i, PyFloat_FromDouble(C[i]));
    }
    
    free(A);
    free(B);
    free(C);
    
    return result;
}

// Python wrapper for int32 matmul
static PyObject* py_matmul_i32(PyObject* self, PyObject* args) {
    PyObject *A_list, *B_list;
    int64_t M, N, K;
    
    if (!PyArg_ParseTuple(args, "OOlll", &A_list, &B_list, &M, &N, &K)) {
        return NULL;
    }
    
    Py_ssize_t size_a, size_b;
    int32_t* A = list_to_int32_array(A_list, &size_a);
    int32_t* B = list_to_int32_array(B_list, &size_b);
    int32_t* C = (int32_t*)malloc(M * N * sizeof(int32_t));
    
    matmul_i32(A, B, C, M, N, K);
    
    PyObject* result = PyList_New(M * N);
    for (int64_t i = 0; i < M * N; i++) {
        PyList_SET_ITEM(result, i, PyLong_FromLong(C[i]));
    }
    
    free(A);
    free(B);
    free(C);
    
    return result;
}

// Python wrapper for int8 matmul
static PyObject* py_matmul_i8(PyObject* self, PyObject* args) {
    PyObject *A_list, *B_list;
    int64_t M, N, K;
    
    if (!PyArg_ParseTuple(args, "OOlll", &A_list, &B_list, &M, &N, &K)) {
        return NULL;
    }
    
    Py_ssize_t size_a, size_b;
    int8_t* A = list_to_int8_array(A_list, &size_a);
    int8_t* B = list_to_int8_array(B_list, &size_b);
    int32_t* C = (int32_t*)malloc(M * N * sizeof(int32_t));
    
    matmul_i8(A, B, C, M, N, K);
    
    PyObject* result = PyList_New(M * N);
    for (int64_t i = 0; i < M * N; i++) {
        PyList_SET_ITEM(result, i, PyLong_FromLong(C[i]));
    }
    
    free(A);
    free(B);
    free(C);
    
    return result;
}

// Method definitions
static PyMethodDef MatmulMethods[] = {
    {"matmul_f32", py_matmul_f32, METH_VARARGS, "Float32 matrix multiplication"},
    {"matmul_f64", py_matmul_f64, METH_VARARGS, "Float64 matrix multiplication"},
    {"matmul_i32", py_matmul_i32, METH_VARARGS, "Int32 matrix multiplication"},
    {"matmul_i8", py_matmul_i8, METH_VARARGS, "Int8 matrix multiplication"},
    {NULL, NULL, 0, NULL}
};

// Module definition
static struct PyModuleDef matmulmodule = {
    PyModuleDef_HEAD_INIT,
    "c_matmul",
    "Pure C accelerated matrix multiplication",
    -1,
    MatmulMethods
};

// Module initialization
PyMODINIT_FUNC PyInit_c_matmul(void) {
    return PyModule_Create(&matmulmodule);
}
