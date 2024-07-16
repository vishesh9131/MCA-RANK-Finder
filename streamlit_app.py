import streamlit as st
import pandas as pd
import plotly.express as px

# Set page configuration to force light mode
st.set_page_config(
    page_title="MCA Rank Explorer",
    layout="centered",
    initial_sidebar_state="auto"
)

# Load the data
df = pd.read_csv('TGPA.csv')

# Clean the data
df.columns = df.columns.str.strip()
df['Regd No.'] = df['Regd No.'].astype(str)
df['Name'] = df['Name'].str.strip()

# Calculate rank based on CGPA
df['Rank'] = df['Cgpa'].rank(ascending=False, method='min').astype(int)

# Function to get name suggestions
def get_name_suggestions(input_text, df, num_suggestions=5):
    if input_text:
        suggestions = df[df['Name'].str.contains(input_text, case=False, na=False)]['Name'].head(num_suggestions).tolist()
        return suggestions
    return []

# Streamlit app
st.title('MCA Rank Explorer: Discover Top Students')

# Sidebar for navigation
st.sidebar.title("Navigation")
page = st.sidebar.radio("Choose a page", ["Home", "Top Students", "State Distribution", "About Me"])

if page == "Home":
    # Input for registration number or name
    search_term = st.text_input('Enter Registration Number or Name')
    if search_term:
        # Display name suggestions
        suggestions = get_name_suggestions(search_term, df)
        if suggestions:
            cols = st.columns(len(suggestions))
            for col, suggestion in zip(cols, suggestions):
                if col.button(suggestion, key=suggestion, help="Click to search"):
                    st.session_state.search_term = suggestion
                    st.rerun()

        # Use the updated search term from session state
        search_term = st.session_state.get('search_term', search_term)

        # Search by registration number or name
        result = df[(df['Regd No.'] == search_term) | (df['Name'].str.contains(search_term, case=False, na=False))]
        
        if not result.empty:
            st.write('### Student Details')
            for index, row in result.iterrows():
                st.markdown(f"""
                    <div style="background-color: #50586C; padding: 20px; border-radius: 10px;margin-top: 10px; border: 1px solid #DCE2F0;">
                        <h2 style="color: #DCE2F0;">Rank: {row['Rank']}</h2>
                        <p style="font-size: 18px; color: #DCE2F0;">
                            <strong>Registration Number:</strong> {row['Regd No.']}<br>
                            <strong>Name:</strong> {row['Name']}<br>
                            <strong>CGPA:</strong> {row['Cgpa']}
                        </p>
                    </div>
                """, unsafe_allow_html=True)    
        else:
            st.write('No student found with the given registration number or name.')

    # About information at the bottom of the Home page
    # st.info("Welcome to the ultimate student snooping app! 🔍 Find students by registration number or name, check out the top CGPA brainiacs, and see where they’re from. Created by Vishesh Yadav...")
    st.markdown("""
        <div style="margin-top: 20px;">
            <div style="background-color: #dce2f0; padding: 10px; border-radius: 10px;">
                Welcome to the ultimate student snooping app! 🔍 Find students by registration number or name, check out the top CGPA brainiacs, and see where they’re from. Created by Vishesh Yadav...
            </div>
        </div>
    """, unsafe_allow_html=True)


elif page == "DataStudy":
    st.write("### Data Study")
    st.write("Explore the data and gain insights.")

elif page == "Top Students":
    st.write("### Top 10 Students by CGPA")
    top_10_students = df.nsmallest(10, 'Rank')
    fig = px.bar(top_10_students, x='Name', y='Cgpa', color='Cgpa', 
                 labels={'Cgpa': 'CGPA', 'Name': 'Student Name'},
                 title='Top 10 Students by CGPA')
    st.plotly_chart(fig)

elif page == "State Distribution":
    st.write("### Number of Students by State")
    state_counts = df['State'].value_counts()
    st.bar_chart(state_counts)

elif page == "About Me":
    st.write("### About Me")
    st.markdown("""
        <div style="background-color: #f0f0f5; padding: 20px; border-radius: 10px; margin-top: 10px; border: 1px solid #dce2f0;">
            <h2 style="color: #50586c;">Vishesh Yadav / विशेष यादव</h2>
            <p style="font-size: 18px; color: #50586c;">
                I am Vishesh Yadav, currently pursuing MCA Hons in AI & ML from Lovely Professional University (LPU). 
                My passion lies in exploring the vast field of Artificial Intelligence and Machine Learning, 
                and I am dedicated to leveraging these technologies to solve real-world problems.
            </p>
            <p style="font-size: 18px; color: #50586c;">
                Feel free to explore the data and gain insights. If you have any questions or suggestions, 
                please do not hesitate to reach out.
            </p>
            <p style="font-size: 18px; color: #50586c;">
                Connect with me:
                <ul>
                    <li><a href="https://github.com/vishesh9131" style="color: #50586c;">GitHub</a></li>
                    <li><a href="https://www.linkedin.com/in/vishesh-yadav-aa7333192/" style="color: #50586c;">LinkedIn</a></li>
                    <li><a href="https://www.instagram.com/vishesh.yadav_" style="color: #50586c;">Instagram</a></li>
                </ul>
            </p>
        </div>
    """, unsafe_allow_html=True)