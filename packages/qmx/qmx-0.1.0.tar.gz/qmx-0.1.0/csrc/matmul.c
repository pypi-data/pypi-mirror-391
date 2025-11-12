#include "matmul.h"

void matmul_f32(const float* A, const float* B, float* C,
                int64_t M, int64_t N, int64_t K) {
    for (int64_t i = 0; i < M; i++) {
        for (int64_t j = 0; j < N; j++) {
            float sum = 0;
            for (int64_t k = 0; k < K; k++) {
                sum += A[i * K + k] * B[k * N + j];
            }
            C[i * N + j] = sum;
        }
    }
}

void matmul_f64(const double* A, const double* B, double* C,
                int64_t M, int64_t N, int64_t K) {
    for (int64_t i = 0; i < M; i++) {
        for (int64_t j = 0; j < N; j++) {
            double sum = 0;
            for (int64_t k = 0; k < K; k++) {
                sum += A[i * K + k] * B[k * N + j];
            }
            C[i * N + j] = sum;
        }
    }
}

void matmul_i32(const int32_t* A, const int32_t* B, int32_t* C,
                int64_t M, int64_t N, int64_t K) {
    for (int64_t i = 0; i < M; i++) {
        for (int64_t j = 0; j < N; j++) {
            int32_t sum = 0;
            for (int64_t k = 0; k < K; k++) {
                sum += A[i * K + k] * B[k * N + j];
            }
            C[i * N + j] = sum;
        }
    }
}

void matmul_i8(const int8_t* A, const int8_t* B, int32_t* C,
               int64_t M, int64_t N, int64_t K) {
    for (int64_t i = 0; i < M; i++) {
        for (int64_t j = 0; j < N; j++) {
            int32_t sum = 0;
            for (int64_t k = 0; k < K; k++) {
                sum += (int32_t)A[i * K + k] * (int32_t)B[k * N + j];
            }
            C[i * N + j] = sum;
        }
    }
}
