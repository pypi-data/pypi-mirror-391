#############
# Libraries #
#############

import numpy as np
import pandas as pd
import os
import ray
import time
import itertools
import cvxpy as cp
import random
from scipy.linalg import block_diag

#########################################
# Helper functions for estimating error #
#########################################

# Error between observed and estimated value
def e(X, Y, weights):
    Y= Y.ravel()
    return (Y-X.T @ weights.value)
# Mean error between observed and estimated value 
def e_mean(X, Y, weights):
    Y= Y.ravel()
    return np.mean(Y-X.T @ weights.value)
# Mean squared error between observed and estimated value 
def mse(X, Y, weights):
    Y= Y.ravel()
    return np.mean((Y-X.T @ weights.value)**2)

#############################
# Helper Functions for mlSC #
#############################

# Classical synthetic control: used as a warm-start
# Objective function
def obj_func_ss(weights: np.array, control_vals: np.array, target: np.array):
    data = cp.vstack((target, control_vals))
    return cp.pnorm(data[1:,:].T @ weights - data[0,:], p=2)**2

def synthetic_control(data: np.array, vals: float, t: float):
    """
    We use the classical SC to find a solution.

    data: (N_agg, T) - array of outcomes
    vals: integer indicating which aggregated unit is treated
    t: integer indicating the period in which treatment is assigned 
    """
  
    " Define target and control "
    target_mat = data[vals,]
    data_small = np.delete(data, vals,axis = 0) 
    num_controls = data_small.shape[0]
    
    weights = cp.Variable(num_controls)
    X_train = data_small[:,:t]
    Y_train = np.array([target_mat[:t]])
    X_test = data_small[:,t:]
    Y_test = target_mat[t:]

    # Define optimization problem
    constraints = [cp.sum(weights) == 1, 0<= weights, weights <= 1] # convexity constraints
    objective = cp.Minimize(obj_func_ss(weights, X_train, Y_train))
    problem = cp.Problem(objective,constraints)
    problem.solve(solver = cp.SCS)

    # Save results
    tau_est = e_mean(X_test, Y_test, weights) # average estimate over time
    w_star = weights.value
    
    return (tau_est,w_star)

# Synthetic control state-county
def obj_func_sc_sc(weights: np.array, control_vals: np.array, target: np.array):
    data = cp.vstack((target, control_vals))
    lambda_reg = 1e-8
    return cp.pnorm(data[1:,:].T @ weights - data[0,:], p=2)**2+lambda_reg*cp.norm(weights)**2
    
def synthetic_control_counties(data: np.array, vals, t: float):
    """
    We use SC to find a solution.
    """
    
    """
    Synthetic Control: State-county
    """
  
    # Obtain the target matrix and control matrix as well as the number of controls
    " Define target and control "
    target_mat = data[vals,]
    data_small = np.delete(data, vals,axis = 0)
    num_controls = data_small.shape[0]

    # Define training and test set
    weights = cp.Variable(num_controls)
    X_train = data_small[:,:t]
    Y_train = np.array([target_mat[:t]])
    X_test = data_small[:,t:]
    Y_test = target_mat[t:]

    # Define optimization problem
    constraints = [cp.sum(weights) == 1, 0<= weights, weights <= 1]
    objective = cp.Minimize(obj_func_sc_sc(weights, X_train, Y_train)) # add small L2 norm to vector to ensure uniqueness
    problem = cp.Problem(objective,constraints)
        
    problem.solve(solver = cp.SCS)

    # Save results
    tau_est = e_mean(X_test, Y_test, weights)
    w_star = weights.value
    
    return (tau_est,w_star)

# Loss function
def loss_fn(control_vals, target, weights):
    """
    Standard squared error loss.
    control_vals: (num_controls, T)
    target: (T,)
    weights: cvxpy variable of shape (num_controls,)
    """
    pred = control_vals.T @ weights  # shape (T,)
    return cp.sum_squares(target - pred)

# Constrained objective function
def obj_func_constr(weights, control_vals, target, lambd, Q, var_y_est):
    """
    Full SC objective with vectorized penalty.
    lambd: nonnegative scalar (cvxpy Parameter or float)
    Q: precomputed penalty matrix
    """
    return loss_fn(control_vals, target, weights) + lambd *var_y_est* cp.quad_form(weights, Q)

# Build matrix for penalty term
def build_penalty_matrix(v_sc_list):
    """
    Precompute block-diagonal penalty matrix Q for all states.

    v_sc_list: list of arrays, each array is v_s for an aggregate unit s, where v_s are the population weights for units within aggregate unit s
    Returns: Q (numpy array)
    """
    blocks = []
    for v in v_sc_list:
        v = v.reshape(-1, 1)  # column vector
        ones = np.ones((1, len(v)))
        M_s = np.eye(len(v)) - v @ ones
        Q_s = M_s.T @ M_s
        blocks.append(Q_s)
    return block_diag(*blocks)

# Obtain estimates for noise variance and outcome variance using hierarchical effects model
def get_hierarchical_effects_decomposition(data_disagg: np.array, n_c: np.array, t: float, vals: float):
    """
    Obtain hierarchical effects through simple hierarchical random effects decomposition.

    data_disagg: (N_disagg, T) - array of outcomes for all disaggregated units
    n_c: (N_agg,) - each entry represents the number of disaggregated units in each aggregated unit
    t: integer indicating the period in which treatment is assigned 
    vals: integer indicating which aggregated unit is treated
    
    Returns: 
    var_eps: estimated noise variance
    var_y: estimated outcome variance
    """

    N_agg = len(n_c)
    
    # Get mu_hat_sc
    data_disagg_averages = np.mean(data_disagg[:,:t], axis = 1)

    # Get alpha_hat_s
    cumulative_sum = np.cumsum(n_c)
    alpha_hat_s = []
    for s in range(N_agg):
        if s ==0:
            ind_start = 0
        else:
            ind_start = cumulative_sum[s-1]
                
        ind_end = cumulative_sum[s]
        alpha_hat_s.append(np.mean(data_disagg_averages[ind_start:ind_end]))

    # Get eta_hat_sc
    eta_hat_sc = []
    for s in range(N_agg):
            if s ==0:
                ind_start = 0
            else:
                ind_start = cumulative_sum[s-1]
            ind_end = cumulative_sum[s]
            eta_hat_sc.append(data_disagg_averages[ind_start:ind_end]-alpha_hat_s[s])
    eta_hat_sc = np.concatenate(eta_hat_sc, axis = 0)

    # Variances
    var_a = np.var(np.array(alpha_hat_s))
    var_eta = []
    for s in range(N_agg):
        if s ==0:
            ind_start = 0
        else:
            ind_start = cumulative_sum[s-1]
        ind_end = cumulative_sum[s]
        eta_hat_sc_s = eta_hat_sc[ind_start:ind_end]
        var_eta.append(np.mean([eta**2 for eta in eta_hat_sc_s]))
    var_eps_all = []
    var_ys = []
    for s in range(N_agg):
        if s ==0:
                ind_start = 0
        else:
                ind_start = cumulative_sum[s-1]
        ind_end = cumulative_sum[s]
        mu_hat_sc = np.array(data_disagg_averages[ind_start:ind_end])
        var_eps_all.append(np.mean((np.array(data_disagg[ind_start:ind_end,:t])-mu_hat_sc[:, np.newaxis])**2))
        var_ys.append(np.var(data_disagg[ind_start:ind_end,:t]))

    var_eps = np.mean(np.delete(var_eps_all,vals))
    var_y = np.mean(np.delete(var_ys,vals))

    return (var_eps, var_y)

# Heuristic lambda
def get_lambda_heuristic(var_eps: float, var_y: float):
    """
    Obtain lambda through the heuristic proposed in the paper.

    var_eps: estimated noise variance
    var_y: estimated outcome variance
    
    Returns: l_h
    """
    
    l_h = 2*var_eps/var_y # l_h = 2*sigma^2_eps/sigma^2_y
        
    return l_h

# Cross-validation lambda
def get_lambda_cv(target_mat: np.array, control_mat: np.array, control_mat_agg: np.array, nc_c: np.array, Q: np.array, var_y: float, t_cv: float, t: float, lambda_grid: np.array):
    """
    Obtain lambda through cross-validation proposed in the paper.

    target_mat: (T,) - array of outcomes for treated aggregated unit
    control_mat: (N_disagg, T) - array of outcomes for control disaggregated units
    control_mat_agg: (N_agg, T) - arrays of outcomes for control aggregated units
    nc_c: (N_agg-1,) - array of number of disaggregated units for all control units
    Q: penalty matrix
    var_y: estimated outcome variance
    t_cv: integer indicating first cross-validation period
    t: integer indicating treated period
    lambda_grid: lambda grid the estimator is searching over
    
    Returns: l_cv
    """

    # Restrict data matrices to t_cv set only
    X_train = control_mat[:,:t_cv]
    Y_train = target_mat[:t_cv]
    X_test = control_mat[:,t_cv:t]
    Y_test = target_mat[t_cv:t]
    num_controls = control_mat.shape[0]

    # Define weights for the optimization problem, lambda and constraints and Q
    weights = cp.Variable(num_controls)
    lambd = cp.Parameter(nonneg = True)
    constraints = [cp.sum(weights) == 1, weights >= 0] # convexity constraints
    
    # Initialize weights as SC solution for a warm start
    data_agg_new = np.vstack((target_mat,control_mat_agg))
    data_agg_cv = data_agg_new[:,:t]
    sc_agg_cv = synthetic_control(data_agg_cv, 0, t_cv)
    w_sc = sc_agg_cv[1]
    weights.value = np.repeat(w_sc / nc_c, nc_c)

    # Define optimization problem
    objective = cp.Minimize(obj_func_constr(weights, X_train, Y_train, lambd, Q, var_y))
    problem = cp.Problem(objective,constraints)

    # Loop over time periods
    cv_error = []
    for v in lambda_grid:
        if v ==0: # Run sc_counties if v=0
            data_agg_disagg_new = np.vstack((target_mat,control_mat)) # target: state, control: counties
            data_agg_disagg_cv = data_agg_disagg_new[:,:t]
            sc_sc = synthetic_control_counties(data_agg_disagg_cv,0,t_cv)
            cv_error.append(float(np.mean((Y_test-X_test.T@sc_sc[1])**2)))
        else:
            lambd.value = v
            problem.solve(solver = cp.SCS)
            cv_error.append(mse(X_test, Y_test, weights))
    
    # Find lambda with minimum error
    min_index = np.argmin(cv_error) 
    l_cv = lambda_grid[min_index] # set lambda to optimally picked lambda

    return l_cv
    

# mlSC estimator
def mlSC_estimator(data_agg: np.array,data_disagg: np.array, vals: float, n_c: np.array, t: float, w_c: np.array, lambda_est = None, lambda_val = 0.0001, lambda_grid = np.concatenate(([0], np.logspace(np.log10(1e-8), np.log10(5), 50),np.logspace(np.log10(10), np.log10(1000), 5))), t_cv_periods = 1):
    """
    Finds a vector for aggregated-disaggregated data (penalized) using a heuristic or cross-validation over time.

    data_agg: (N_agg, T) - array of outcomes
    data_disagg: (N_disagg, T) - array of outcomes
    vals: integer indicating which aggregated unit is treated
    n_c: (N_agg,) - each entry represents the number of disaggregated units in each aggregated unit
    t: integer indicating the period in which treatment is assigned 
    w_c: list of arrays, each array is v_s for an aggregate unit s, where v_s are the population weights for units within aggregate unit s 
    lambda_est: method to estimate lambda: "heuristic", "cross-validation" or None
    lambda_val: lambda value for penalty in case estimation method = None
    lambda_grid: grid specified for lambda for cross-validation
    t_cv_periods: specify the number of cross-validation periods

    Returns:
    tau_est: avgerage estimated treatment effect over time
    l_star: estimated penalty parameter
    w_star: estimated weight vector
    
    Note:
    Data_agg, data_disagg and n_c need to be in the same order!
    Treatment is assumed to be absorbing, so once treatment is assigned, the unit will be treated forever
    
    """

    " Define target and control"
    target_mat = data_agg[vals,] # target matrix
    cumulative_sum = np.cumsum(n_c)
    if vals ==0:
        ind_start = 0
    else:
        ind_start = cumulative_sum[vals-1]
    ind_end = cumulative_sum[vals]
    control_mat = np.delete(data_disagg, list(range(ind_start,ind_end)),axis = 0) # control matrix: drops counties for treated state
    nc_control = np.delete(n_c,vals) # Array with number of disaggregated units for all control units
    num_controls,T = control_mat.shape # Number of controls and total time periods
    control_mat_agg = np.delete(data_agg, vals, axis = 0)
    
    " Define weights for optimization problem, lambda and constraints and block penalty matrix Q "
    weights = cp.Variable(num_controls)
    lambd = cp.Parameter(nonneg = True)
    constraints = [cp.sum(weights) == 1, weights >= 0] # convexity constraints
    w_c_c = [w for i, w in enumerate(w_c) if i != vals] # population weights for all control units
    Q = build_penalty_matrix(w_c_c)  # Build penalty matrix
    if T>2:
        est_variances = get_hierarchical_effects_decomposition(data_disagg, n_c, t, vals)
        var_eps = est_variances[0]
        var_y = est_variances[1]
    else:
        print("T needs to be bigger than 2 to estimate the variance of epsilon and y.")
    
    " Estimate lambda "
    if lambda_est == None:
        l_star= lambda_val
    elif lambda_est == "heuristic":
        l_star = get_lambda_heuristic(var_eps, var_y)
    elif lambda_est == "cross-validation":
        l_star = get_lambda_cv(target_mat, control_mat, control_mat_agg, nc_control, Q, var_y, t-t_cv_periods, t, lambda_grid)
    else:
        raise ValueError(
            'Invalid lambda_est value. Please specify "heuristic", "cross-validation", '
            'or set lambda_est=None and provide a numeric lambda_val.'
        )

    " Obtain final estimates "

    if l_star == 0: # if l_star =0, repeat synthetic control counties
        data_new = np.vstack((target_mat,control_mat))
        sc_sc = synthetic_control_counties(data_new,0,t)

        # Save results
        tau_est = sc_sc[0]
        w_star = sc_sc[1]
        lstar = 0
    else:
        " Define weights for optimization problem, lambda and constraints and block penalty matrix Q "
        weights = cp.Variable(num_controls)
        lambd = cp.Parameter(nonneg = True)
        constraints = [cp.sum(weights) == 1, weights >= 0] # convexity constraints
    
        " Define warm-start "
        sc_state = synthetic_control(data_agg, vals, t) 
        w_ss = sc_state[1]
        weights.value = np.repeat(w_ss / nc_control, nc_control) # initialize weights to classical SC solution for a warm start
        
        " Define target and control matrices "
        X_train = control_mat[:,:t]
        Y_train = target_mat[:t]
        X_test = control_mat[:,t:]
        Y_test = target_mat[t:] 
    
        " Run optimization problem "
        
        lambd.value = l_star    
        objective = cp.Minimize(obj_func_constr(weights, X_train, Y_train, lambd, Q, var_y))
        problem = cp.Problem(objective,constraints)
        problem.solve(solver = cp.SCS)
        
        " Save results "
        tau_est = e_mean(X_test, Y_test, weights) # averaged over treated period
        w_star = weights.value
        
    return (tau_est,l_star, w_star)
