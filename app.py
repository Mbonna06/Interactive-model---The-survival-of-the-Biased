import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
# (Import your core math functions here)

st.title("The Survival of the Biased: Interactive Model")

# 1. Create Web Sliders
current_learning = st.slider("Learning Rate (λ)", min_value=0.01, max_value=0.40, value=0.15, step=0.01)
current_friction = st.slider("Transaction Friction (c)", min_value=0.00, max_value=0.05, value=0.01, step=0.005)

# 2. Run the simulation with the slider values
new_s_rat, new_s_anc = run_simulation(fixed_market_states, current_learning, 0.40, current_friction)

# 3. Draw the Plot
fig, ax = plt.subplots(figsize=(10, 5))
ax.plot(new_s_rat, label="Rational Wealth", color="blue")
ax.plot(new_s_anc, label="Anchored Wealth", color="red")
ax.legend()

# 4. Display the plot on the web page
st.pyplot(fig)
