# ========================================================
# THESIS INTERACTIVE DASHBOARD: "The Survival of the Biased"
# 
# AUTHOR: Matteo Bonaghi
# SUPERVISOR: Prof. Daniele Giachini
#
# DESCRIPTION:
# This script provides an interactive, real-time visualization of the 
# evolutionary betting market simulation. It allows the user to manipulate 
# cognitive parameters (Rational Learning Rate and Anchoring Strength) via 
# slider controls and immediately observe the evolutionary impact on agent 
# survival across a fixed, identical sequence of stochastic market states.
# ========================================================

import numpy as np               # Used for high-performance mathematical arrays
import matplotlib.pyplot as plt  # Used to draw the graphs
from matplotlib.widgets import Slider # Used for the interactive slider bars

# =============================================
# 1. CORE MATH FUNCTIONS
# =============================================

def update_rational(current_belief, state, learning_rate):
    """
    Calculates the rational belief update based on the forecast error.
    """
    new_belief = current_belief + learning_rate * (state - current_belief)
    # np.clip ensures the belief stays within [0.05, 0.95] to prevent division by zero later.
    return np.clip(new_belief, 0.05, 0.95)

def update_anchored(current_belief, state, learning_rate, anchor, strength):
    """
    Calculates the biased belief by applying the anchoring heuristic.
    """
    rational_move = update_rational(current_belief, state, learning_rate)
    biased_belief = (1 - strength) * rational_move + (strength * anchor)
    return np.clip(biased_belief, 0.05, 0.95)

# =============================================
# 2. THE SIMULATION LOGIC
# =============================================

# We establish FEE_RATE as a global constant (thus uppercase)
FEE_RATE = 0.03

def run_simulation(states, rat_learning, anchor_val, anchor_str):
    """
    Runs the market simulation given a FIXED sequence of market states.
    We pass 'states' as an argument so the underlying "reality" remains constant
    while the user changes the psychological parameters with the sliders.
    """
    # How many days we are simulating
    T = len(states)
    
    # --- Initialize Data Collections (Numpy Arrays) ---
    wealth_rat = np.zeros(T)
    wealth_anc = np.zeros(T)
    wealth_rat[0] = 100.0  
    wealth_anc[0] = 100.0
    
    belief_rat = np.zeros(T)
    belief_anc = np.zeros(T)
    belief_rat[0] = 0.5
    belief_anc[0] = anchor_val

    # --- Time Progression (Repetition Statement) ---
    for t in range(T - 1):
        total_wealth = wealth_rat[t] + wealth_anc[t]
        if total_wealth <= 0: 
            break 
            
        # 1. Price formation (endogenous formation)
        price = ((wealth_rat[t] * belief_rat[t]) + (wealth_anc[t] * belief_anc[t])) / total_wealth
        
        # 2. Daily Returns
        if states[t] == 1: # good day
            ret_rat = belief_rat[t] / price
            ret_anc = belief_anc[t] / price
        else: # bad day and thus states[t] == 0
            ret_rat = (1 - belief_rat[t]) / (1 - price)
            ret_anc = (1 - belief_anc[t]) / (1 - price)
            
        # 3. Calculate Gross Wealth
        gross_w_rat = wealth_rat[t] * ret_rat
        gross_w_anc = wealth_anc[t] * ret_anc
        
        # 4. Calculate Trading Volume and Fees
        # We use a conditional to ensure Day 0 trading volume calculates correctly against initial priors
        trade_rat = abs(belief_rat[t] - (belief_rat[t-1] if t > 0 else 0.5))
        trade_anc = abs(belief_anc[t] - (belief_anc[t-1] if t > 0 else anchor_val))
        
        fee_paid_rat = gross_w_rat * (FEE_RATE * trade_rat)
        fee_paid_anc = gross_w_anc * (FEE_RATE * trade_anc)
        
        # 5. Fee Redistribution
        rebate = (fee_paid_rat + fee_paid_anc) / 2.0
        
        # 6. Final Wealth Update
        wealth_rat[t+1] = gross_w_rat - fee_paid_rat + rebate
        wealth_anc[t+1] = gross_w_anc - fee_paid_anc + rebate
        
        # 7. Learning/Updating Beliefs for Tomorrow
        belief_rat[t+1] = update_rational(belief_rat[t], states[t], rat_learning)
        belief_anc[t+1] = update_anchored(belief_anc[t], states[t], rat_learning, anchor_val, anchor_str)
        
    # --- Final Data Processing ---
    # Convert absolute wealth arrays into percentage share arrays.
    total_w = wealth_rat + wealth_anc
    share_rat = wealth_rat / total_w
    share_anc = wealth_anc / total_w
    
    return share_rat, share_anc

# =============================================
# 3. INTERACTIVE DASHBOARD SETUP (Object-Oriented Matplotlib)
# =============================================

TIME_STEPS = 500
# There is a 55% chance that the market will result in a 1.
TRUE_PROBABILITY = 0.55 # 1 - TRUE_PROBABILITY (0.45): There is a 45% chance that the market will result in a 0
ANCHOR_VALUE = 0.40

# --- ISOLATING THE STOCHASTIC ENVIRONMENT ---
# We generate the sequence of 1s and 0s outside the function using np.random.choice so that we freeze the reality of the market
fixed_market_states = np.random.choice([1, 0], size=TIME_STEPS, p=[TRUE_PROBABILITY, 1 - TRUE_PROBABILITY])

# Define the starting positions for the sliders when the application opens.
init_learning = 0.15
init_strength = 0.80

# Run the very first simulation to get the baseline data to draw the initial graph
s_rat, s_anc = run_simulation(fixed_market_states, init_learning, ANCHOR_VALUE, init_strength)

# --- GRAPH SETUP ---
# plt.subplots() is a constructor that creates two separate OOP objects:
# 1. 'fig' (Figure): The actual application window (the canvas itself).
# 2. 'ax' (Axes): The specific chart area where the data is drawn.
fig, ax = plt.subplots(figsize=(12, 7))

# plt.subplots_adjust compresses the bottom of the 'ax' chart area by 35%
# We must do this to create empty, physical white space at the bottom of the 
# 'fig' window so our sliders have a place to sit without overlapping the graph.
plt.subplots_adjust(bottom=0.35)

# --- CREATING THE LINE OBJECTS ---
# By adding the comma, we extract the actual Line2D object directly from that list 
# and save it to the variable 'line_rat'. 
line_rat, = ax.plot(s_rat, label='Rational Agent Share', color='blue', linewidth=2)
line_anc, = ax.plot(s_anc, label='Anchored Agent Share', color='red', linewidth=2)

# Draw the absolute 50% survival threshold line.
ax.axhline(0.5, color='black', linestyle='--', label='Survival Threshold (50%)')

# Format the 'ax' object with our labels and titles.
ax.set_ylim(0, 1) # Locks the vertical axis strictly between 0% and 100% wealth.
ax.set_title("Interactive Market Selection: Wealth Share Dynamics", fontsize=14, fontweight='bold')
ax.set_xlabel("Trading Days")
ax.set_ylabel("Relative Wealth Share")
ax.legend(loc="upper right")
ax.grid(alpha=0.3)

# =============================================
# 4. THE SLIDERS 
# =============================================

# --- UI AXES SETUP ---
# The sliders need their own boxes. plt.axes([left, bottom, width, height]) uses relative percentages of the 'fig' window.
# E.g., [0.15, 0.20, 0.70, 0.03] means: start 15% from the left, 20% from the bottom, make it 70% wide, and 3% tall.
ax_learning = plt.axes([0.15, 0.20, 0.70, 0.03], facecolor='lightgoldenrodyellow')
ax_strength = plt.axes([0.15, 0.10, 0.70, 0.03], facecolor='lightgoldenrodyellow')

# --- INSTANTIATING THE SLIDER OBJECTS ---
# We call the 'Slider' class we imported at the top of the script.
# We pass it its dedicated box (e.g., ax_learning), its title, its math limits (0.01 to 0.40), and where the dot should be when the program starts (valinit).
slider_learning = Slider(ax_learning, 'Rational Overreaction\n(Learning Rate)', 0.01, 0.40, valinit=init_learning)
slider_strength = Slider(ax_strength, 'Anchoring Strength\n(Stubbornness)', 0.0, 1.0, valinit=init_strength)

# --- THE CALLBACK FUNCTION (Interactivity with the sliders) ---
def update(val):
    """
    This is an 'Event Handler' or 'Callback' function.
    It does absolutely nothing until a specific event triggers it (the user clicking a slider).
    When triggered, it rapidly recalculates the market and updates the visual lines.
    """
    # STEP 1: Extract the new numeric values from the slider objects.
    # '.val' accesses the internal attribute of the Slider object where the current number is stored.
    current_learning = slider_learning.val
    current_strength = slider_strength.val
    
    # STEP 2: Rerun the economic engine.
    # We pass the NEW slider values, but we pass the EXACT SAME 'fixed_market_states'.
    new_s_rat, new_s_anc = run_simulation(fixed_market_states, current_learning, ANCHOR_VALUE, current_strength)
    
    # STEP 3: Injecting Data
    # INSTEAD of deleting the graph and using ax.plot() to draw a brand new one, we use '.set_ydata()'.
    # This finds the existing Line2D objects in the computer's memory and just swaps out the Y-coordinates instantly.
    line_rat.set_ydata(new_s_rat)
    line_anc.set_ydata(new_s_anc)
    
    # STEP 4: Request a GUI render.
    # This prevents the application from lagging while the user drags the mouse.
    fig.canvas.draw_idle()

# .on_changed() acts as a trigger wire. 
# We attach it to the sliders and tell it to execute the 'update' function we 
# just built every single time the slider's value changes
slider_learning.on_changed(update)
slider_strength.on_changed(update)

# plt.show() blocks the script from ending and opens the interactive GUI window.
plt.show()