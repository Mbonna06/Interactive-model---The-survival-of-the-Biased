import streamlit as st
import numpy as np
import matplotlib.pyplot as plt

# =============================================
# 1. CONSTANTS & CACHED MARKET STATES
# =============================================
FEE_RATE = 0.03
TIME_STEPS = 500
TRUE_PROBABILITY = 0.55
ANCHOR_VALUE = 0.40

# This @st.cache_data decorator is crucial for Streamlit. 
# It ensures the random sequence is only generated ONCE when the app starts.
# Otherwise, the lines would jump chaotically every time you move a slider!
@st.cache_data
def generate_fixed_market():
    return np.random.choice([1, 0], size=TIME_STEPS, p=[TRUE_PROBABILITY, 1 - TRUE_PROBABILITY])

fixed_market_states = generate_fixed_market()

# =============================================
# 2. CORE MATH FUNCTIONS (From your original script)
# =============================================
def update_rational(current_belief, state, learning_rate):
    new_belief = current_belief + learning_rate * (state - current_belief)
    return np.clip(new_belief, 0.05, 0.95)

def update_anchored(current_belief, state, learning_rate, anchor, strength):
    rational_move = update_rational(current_belief, state, learning_rate)
    biased_belief = (1 - strength) * rational_move + (strength * anchor)
    return np.clip(biased_belief, 0.05, 0.95)

def run_simulation(states, rat_learning, anchor_val, anchor_str):
    T = len(states)
    
    wealth_rat = np.zeros(T)
    wealth_anc = np.zeros(T)
    wealth_rat[0] = 100.0  
    wealth_anc[0] = 100.0
    
    belief_rat = np.zeros(T)
    belief_anc = np.zeros(T)
    belief_rat[0] = 0.5
    belief_anc[0] = anchor_val

    for t in range(T - 1):
        total_wealth = wealth_rat[t] + wealth_anc[t]
        if total_wealth <= 0: 
            break 
            
        price = ((wealth_rat[t] * belief_rat[t]) + (wealth_anc[t] * belief_anc[t])) / total_wealth
        
        if states[t] == 1: 
            ret_rat = belief_rat[t] / price
            ret_anc = belief_anc[t] / price
        else: 
            ret_rat = (1 - belief_rat[t]) / (1 - price)
            ret_anc = (1 - belief_anc[t]) / (1 - price)
            
        gross_w_rat = wealth_rat[t] * ret_rat
        gross_w_anc = wealth_anc[t] * ret_anc
        
        trade_rat = abs(belief_rat[t] - (belief_rat[t-1] if t > 0 else 0.5))
        trade_anc = abs(belief_anc[t] - (belief_anc[t-1] if t > 0 else anchor_val))
        
        fee_paid_rat = gross_w_rat * (FEE_RATE * trade_rat)
        fee_paid_anc = gross_w_anc * (FEE_RATE * trade_anc)
        
        rebate = (fee_paid_rat + fee_paid_anc) / 2.0
        
        wealth_rat[t+1] = gross_w_rat - fee_paid_rat + rebate
        wealth_anc[t+1] = gross_w_anc - fee_paid_anc + rebate
        
        belief_rat[t+1] = update_rational(belief_rat[t], states[t], rat_learning)
        belief_anc[t+1] = update_anchored(belief_anc[t], states[t], rat_learning, anchor_val, anchor_str)
        
    total_w = wealth_rat + wealth_anc
    share_rat = wealth_rat / total_w
    share_anc = wealth_anc / total_w
    
    return share_rat, share_anc

# =============================================
# 3. STREAMLIT UI & GRAPHING
# =============================================
st.title("The Survival of the Biased: Interactive Model")
st.write("Adjust the cognitive parameters below to see how transaction friction and learning speed trigger the evolutionary inversion.")

# Create the sliders
current_learning = st.slider("Rational Overreaction (Learning Rate)", min_value=0.01, max_value=0.40, value=0.15, step=0.01)
current_strength = st.slider("Anchoring Strength (Stubbornness)", min_value=0.0, max_value=1.0, value=0.80, step=0.05)

# Run the simulation with the exact slider values
s_rat, s_anc = run_simulation(fixed_market_states, current_learning, ANCHOR_VALUE, current_strength)

# Draw the graph
fig, ax = plt.subplots(figsize=(10, 5))
ax.plot(s_rat, label='Rational Agent Share', color='blue', linewidth=2)
ax.plot(s_anc, label='Anchored Agent Share', color='red', linewidth=2)
ax.axhline(0.5, color='black', linestyle='--', label='Survival Threshold (50%)')

# Format the graph
ax.set_ylim(0, 1) 
ax.set_title("Interactive Market Selection: Wealth Share Dynamics", fontsize=14, fontweight='bold')
ax.set_xlabel("Trading Days")
ax.set_ylabel("Relative Wealth Share")
ax.legend(loc="upper right")
ax.grid(alpha=0.3)

# Render the graph in the web app
st.pyplot(fig)
