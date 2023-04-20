import streamlit as st
import random

def main():
    st.title("Tilfeldig tall")
    st.write("Velg laveste og høyeste tall:")

    # Get user input for the range of random numbers
    start_num = st.number_input("Nedre grense", value=0)
    end_num = st.number_input("Øvre grense", value=10)

    # Check if start_num is less than end_num
    if start_num >= end_num:
        st.error("Error: Nedre grense må være lavere enn øvre grense.")
    else:
        # Generate and display the random integer
        random_num = random.randint(start_num, end_num)
        st.write(f"Tilfeldig tall mellom {start_num} and {end_num}: ")
        st.title(random_num)

if __name__ == "__main__":
    main()
