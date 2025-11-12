#ifndef MATMUL_H
#define MATMUL_H

#include <stdint.h>

// Function declarations
void matmul_f32(const float* A, const float* B, float* C,
                int64_t M, int64_t N, int64_t K);

void matmul_f64(const double* A, const double* B, double* C,
                int64_t M, int64_t N, int64_t K);

void matmul_i32(const int32_t* A, const int32_t* B, int32_t* C,
                int64_t M, int64_t N, int64_t K);

void matmul_i8(const int8_t* A, const int8_t* B, int32_t* C,
               int64_t M, int64_t N, int64_t K);

#endif
