import streamlit as st
import random

def main():
    st.title("Random Number Generator")
    st.write("Select the range of numbers to generate a random integer from:")

    # Get user input for the range of random numbers
    start_num = st.number_input("Start number", value=0)
    end_num = st.number_input("End number", value=10)

    # Check if start_num is less than end_num
    if start_num >= end_num:
        st.error("Error: Start number should be less than end number.")
    else:
        # Generate and display the random integer
        random_num = random.randint(start_num, end_num)
        st.write(f"Random integer between {start_num} and {end_num}: {random_num}")

if __name__ == "__main__":
    main()
