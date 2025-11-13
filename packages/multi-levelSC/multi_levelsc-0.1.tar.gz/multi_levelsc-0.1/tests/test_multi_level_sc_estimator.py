from multi_level_sc_estimator.mlSC import mlSC_estimator
import pandas as pd
import numpy as np

import pytest

def generate_equal_state_weights(n_states, n_counties_per_state):
    """
    Generate equal weights for counties within each state.

    Parameters:
    - n_states: number of states
    - n_counties_per_state: int or list of ints for counties per state

    Returns:
    - weights: list of arrays of weights for each state (each array sums to 1)
    """
    weights = []
    for i in range(n_states):
        n_counties = n_counties_per_state if isinstance(n_counties_per_state, int) else n_counties_per_state[i]
        w = np.full(n_counties, 1.0 / n_counties)
        weights.append(w)
    return weights

def test_mlSC_estimator_functionality():
    # Read data
    url = 'https://raw.githubusercontent.com/leabottmer/multi-level-sc-estimator/refs/heads/main/tests/ia_emp_app_teen_empl.csv'
    datamat_county = pd.read_csv(url)
    
    states = datamat_county.iloc[:, -1].unique()
    states = sorted(states)
    N_states = len(states)
    T = datamat_county.shape[1]-2
    
    # Create state data sets for urate: delete all counties with NaN values
    data_state_county = {}
    for s in range(0,N_states):
        state = states[s]
        ind_state = datamat_county.index[datamat_county.iloc[:, -1] == state]
        rows_to_delete = ~((ind_state < 3145) & (datamat_county.iloc[ind_state, 1:-1].isna().sum(axis=1) == 0))
        ind_state = ind_state[~rows_to_delete]
        data_state_county[s] = datamat_county.iloc[ind_state, 1:-1]
    
    # Next, we create an aggregate data set
    data_states = np.zeros((N_states, T))
    n_c = np.zeros(N_states)
    for s in range(N_states):
        data_states[s, :] = data_state_county[s].mean()
        n_c[s] = data_state_county[s].shape[0]
    
    n_c = n_c.astype(int)
        
    data_counties = np.concatenate(list(data_state_county.values()), axis=0)
    
    # Overall parameters
    
    # Treated unit
    idx = 1 # Iowa
    # Treated time
    t = 24 # T-1 since index starts at 0
    
    data_c = data_counties*100 # convert data to percentage points
    data_s = data_states*100
    
    # Define county weights
    county_weights = generate_equal_state_weights(N_states, n_c)
    
    mlSC_results = mlSC_estimator(data_s,data_c, idx, n_c, t, county_weights, lambda_est = "heuristic")

    # Add assertions to check mlSC_results here
    assert mlSC_results is not None  # Check for some expected outcome

