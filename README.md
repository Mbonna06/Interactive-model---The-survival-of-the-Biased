# Interactive-model---The-survival-of-the-Biased
This repository includes an Interactive Simulation Dashboard designed to provide real-time sensitivity analysis of the Agent-Based Model (ABM) developed in the thesis. This tool allows researchers to move beyond static Monte Carlo averages and observe the high-frequency dynamics of market selection as they unfold.  

Technical Overview: the script utilizes Object-Oriented Matplotlib and the matplotlib.widgets.Slider module to create a dynamic playground for stress-testing the model's core hypotheses.  

Fixed Stochastic Reality: To achieve a true ceteris paribus analysis, the dashboard generates a fixed sequence of 500 stochastic market states. This ensures that any observed shift in wealth is caused by changes in agent psychology rather than random luck.  

Real-Time Evolutionary Toggles: The interface features two primary sliders that act as evolutionary toggles:  
- Rational Overreaction (λ): Adjusts the Bayesian agent's sensitivity to market noise from conservative (0.01) to hyper-active (0.40).  
- Anchoring Strength (γ): Adjusts the biased agent's cognitive inertia from zero bias (0.0) to complete rigidity (1.0).  

Instantaneous Feedback Loop: The implementation relies on a callback function that rapidly recalculates the 500-period economic engine. Using the .set_ydata() method, the dashboard updates the visual lines instantly without redrawing the entire plot, facilitating a seamless exploration of the fitness landscape.  

Key Scientific Utility: The dashboard is instrumental in identifying Tipping Points in market survival. It visually demonstrates how marginal increases in informational sensitivity can trigger a non-linear collapse in wealth share due to the compounding effect of the "Turnover Penalty". By interacting with the sliders, users can witness how psychological stubbornness effectively functions as a structural buffer against capital leakage.
