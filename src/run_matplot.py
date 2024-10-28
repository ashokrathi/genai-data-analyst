import streamlit as st
import matplotlib.pyplot as plt

# Streamlit app title
st.title("Matplotlib Chart in Streamlit")

# Create some example data
x = np.linspace(0, 10, 100)
y = np.sin(x)

# Create a simple line plot using Matplotlib
fig, ax = plt.subplots()
ax.plot(x, y, label='Sine Wave')
ax.set_title('Sine Wave Plot')
ax.set_xlabel('X Axis')
ax.set_ylabel('Y Axis')
ax.legend()

# Display the plot using st.pyplot
st.pyplot(fig)
