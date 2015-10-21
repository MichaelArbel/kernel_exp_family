from kernel_exp_family.estimators.finite.gaussian import feature_map,\
    feature_map_derivative2_d, feature_map_derivative_d
import numpy as np


def feature_map_derivatives_loop(X, omega, u):
    m = 1 if np.isscalar(u) else len(u)
    N = X.shape[0]
    D = X.shape[1]
    
    projections = np.zeros((D, N, m))
    projection = np.dot(X, omega) + u
    np.sin(projection, projection)
    for d in range(D):
        projections[d, :, :] = projection
        projections[d, :, :] *= omega[d, :]
    
    projections *= -np.sqrt(2. / m)
    return projections

def feature_map_derivatives2_loop(X, omega, u):
    m = 1 if np.isscalar(u) else len(u)
    N = X.shape[0]
    D = X.shape[1]
    
    projections = np.zeros((D, N, m))
    Phi2 = feature_map(X, omega, u)
    for d in range(D):
        projections[d, :, :] = -Phi2
        projections[d, :, :] *= omega[d, :] ** 2
        
    return projections

def feature_map_derivatives(X, omega, u):
    return feature_map_derivatives_loop(X, omega, u)

def feature_map_derivatives2(X, omega, u):
    return feature_map_derivatives2_loop(X, omega, u)

def _objective_sym_completely_manual(X, theta, lmbda, omega, u):
    N = X.shape[0]
    D = X.shape[1]
    m = len(theta)
    
    J_manual = 0.
     
    for n in range(N):
        for d in range(D):
            b_term_manual = -np.sqrt(2. / m) * np.cos(np.dot(X[n], omega) + u) * (omega[d, :] ** 2)
            J_manual -= -np.dot(b_term_manual, theta)
             
            c_vec_manual = -np.sqrt(2. / m) * np.sin(np.dot(X[n], omega) + u) * omega[d, :]
            C_term_manual = np.outer(c_vec_manual, c_vec_manual)
            J_manual += 0.5 * np.dot(theta, np.dot(C_term_manual, theta))
    
    J_manual /= N
    J_manual += 0.5 * lmbda * np.dot(theta, theta)
    return J_manual

def _objective_sym_half_manual(X, theta, lmbda, omega, u):
    N = X.shape[0]
    D = X.shape[1]
    
    J_manual = 0.
     
    for n in range(N):
        for d in range(D):
            b_term = -feature_map_derivative2_d(X[n], omega, u, d)
            J_manual -= np.dot(b_term, theta)

            c_vec = feature_map_derivative_d(X[n], omega, u, d)
            C_term_manual = np.outer(c_vec, c_vec)
            J_manual += 0.5 * np.dot(theta, np.dot(C_term_manual, theta))
    
    J_manual /= N
    J_manual += 0.5 * lmbda * np.dot(theta, theta)
    return J_manual

def compute_b_memory(X, omega, u):
    assert len(X.shape) == 2
    Phi1 = feature_map_derivatives2(X, omega, u)
    return -np.mean(np.sum(Phi1, 0), 0)

def compute_C_memory(X, omega, u):
    assert len(X.shape) == 2
    Phi2 = feature_map_derivatives(X, omega, u)
    d = X.shape[1]
    N = X.shape[0]
    m = Phi2.shape[2]
    
#     ## bottleneck! use np.einsum
#     C = np.zeros((m, m))
#     t = time.time()
#     for i in range(N):
#         for ell in range(d):
#             phi2 = Phi2[ell, i]
#             C += np.outer(phi2, phi2)
#     print("loop", time.time()-t)
#      
#     #roughly 5x faster than the above loop
#     t = time.time()
#     Phi2_reshaped = Phi2.reshape(N*d, m)
#     C2=np.einsum('ij,ik->jk', Phi2_reshaped, Phi2_reshaped)
#     print("einsum", time.time()-t)
#
#     #cython implementation, is slowest
#     t = time.time()
#     Phi2_reshaped = Phi2.reshape(N*d, m)
#     C3 = outer_sum_cython(Phi2_reshaped)
#     print("cython", time.time()-t)
    
#     t = time.time()
    Phi2_reshaped = Phi2.reshape(N * d, m)
    C4 = np.tensordot(Phi2_reshaped, Phi2_reshaped, [0, 0])
#     print("tensordot", time.time()-t)

    return C4 / N
