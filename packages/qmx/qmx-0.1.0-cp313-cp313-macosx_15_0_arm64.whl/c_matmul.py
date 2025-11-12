# mtrx/c_matmul.py
try:
    from c_matmul import matmul_f32, matmul_f64, matmul_i32, matmul_i8
    C_BACKEND_AVAILABLE = True
except ImportError:
    C_BACKEND_AVAILABLE = False
    print("Warning: C++ backend not available. Build with: cd mtrx && pip install -e .")

def matmul(A, B, M, N, K, dtype='float32'):
    """
    Dispatch to appropriate C++ matmul based on dtype
    """
    if not C_BACKEND_AVAILABLE:
        raise RuntimeError("C++ backend not built. Run: cd mtrx && pip install -e .")
    
    # Flatten if needed
    if hasattr(A, 'tensor'):
        A = flatten_tensor(A)
    if hasattr(B, 'tensor'):
        B = flatten_tensor(B)
    
    dispatch = {
        'float32': matmul_f32,
        'float64': matmul_f64,
        'int32': matmul_i32,
        'int8': matmul_i8,
    }
    
    if dtype not in dispatch:
        raise ValueError(f"Unsupported dtype: {dtype}")
    
    return dispatch[dtype](A, B, M, N, K)

def flatten_tensor(tensor):
    """Flatten nested list tensor"""
    result = []
    def flatten(lst):
        for item in lst:
            if isinstance(item, list):
                flatten(item)
            else:
                result.append(item)
    flatten(tensor.tensor if hasattr(tensor, 'tensor') else tensor)
    return result