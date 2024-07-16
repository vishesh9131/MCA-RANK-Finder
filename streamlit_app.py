import streamlit as st
import pandas as pd
import plotly.express as px
from fuzzywuzzy import process
import random

st.set_page_config(
    page_title="RankDekho",
    layout="centered",
    initial_sidebar_state="auto"
)

@st.cache_data
def load_data():
    df = pd.read_csv('TGPA.csv')
    df.columns = df.columns.str.strip()
    df['Regd No.'] = df['Regd No.'].astype(str)
    df['Name'] = df['Name'].str.strip()
    df['Rank'] = df['Cgpa'].rank(ascending=False, method='min').astype(int)
    return df

df = load_data()

def get_name_suggestions(input_text, df, num_suggestions=5):
    if input_text:
        names = df['Name'].tolist()
        suggestions = process.extract(input_text, names, limit=num_suggestions)
        return [suggestion[0] for suggestion in suggestions]
    return []

st.title('Rank Dekho : MCA Rank Explorer')

st.sidebar.title("Navigation")
page = st.sidebar.radio("Choose a page", ["Home", "Top Students", "State Distribution", "Student Comparison", "Shoutout to...", "CGPA Distribution", "About Me"])

if page == "Home":
    search_term = st.text_input('Enter Registration Number or Name')
    if search_term:
        suggestions = get_name_suggestions(search_term, df)
        if suggestions:
            cols = st.columns(len(suggestions))
            for idx, (col, suggestion) in enumerate(zip(cols, suggestions)):
                if col.button(suggestion, key=f"{suggestion}_{idx}", help="Click to search"):
                    st.session_state.search_term = suggestion
                    st.experimental_rerun()

        search_term = st.session_state.get('search_term', search_term)

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

    st.markdown("""
        <div style="margin-top: 20px;">
            <div style="background-color: #dce2f0; padding: 10px; border-radius: 10px;">
                Welcome to the ultimate student snooping app! 🔍 Find students by registration number or name, check out the top CGPA brainiacs, and see where they're from. Created by Vishesh Yadav...
            </div>
        </div>
    """, unsafe_allow_html=True)

elif page == "Top Students":
    num_students = st.slider("Select number of top students to display", 1, 50, 10)
    st.write(f"### Top {num_students} Students by CGPA")
    top_students = df.nsmallest(num_students, 'Rank')
    fig = px.bar(top_students, x='Name', y='Cgpa', color='Cgpa', 
                 labels={'Cgpa': 'CGPA', 'Name': 'Student Name'},
                 title=f'Top {num_students} Students by CGPA')
    st.plotly_chart(fig)

elif page == "State Distribution":
    state = st.selectbox("Select a state to filter", options=["All"] + df['State'].unique().tolist())
    cgpa_range = st.slider("Select CGPA range", 0.0, 10.0, (0.0, 10.0), 0.1)
    
    st.write("### Number of Students by State")
    if state == "All":
        filtered_df = df[(df['Cgpa'] >= cgpa_range[0]) & (df['Cgpa'] <= cgpa_range[1])]
        state_counts = filtered_df['State'].value_counts()
    else:
        filtered_df = df[(df['State'] == state) & (df['Cgpa'] >= cgpa_range[0]) & (df['Cgpa'] <= cgpa_range[1])]
        state_counts = filtered_df['State'].value_counts()
    
    st.bar_chart(state_counts)
    
    st.write("### State Distribution Pie Chart")
    fig = px.pie(filtered_df, names='State', title='State Distribution')
    st.plotly_chart(fig)
    
    if state != "All":
        st.write(f"### Detailed Statistics for {state}")
        num_students = filtered_df.shape[0]
        avg_cgpa = filtered_df['Cgpa'].mean()
        top_students = filtered_df.nsmallest(5, 'Rank')
        
        st.write(f"Number of Students: {num_students}")
        st.write(f"Average CGPA: {avg_cgpa:.2f}")
        st.write("Top 5 Students:")
        for index, row in top_students.iterrows():
            st.markdown(f"""
                <div style="background-color: #50586C; padding: 10px; border-radius: 5px; margin-top: 10px; border: 1px solid #DCE2F0;">
                    <h4 style="color: #DCE2F0;">Rank: {row['Rank']}</h4>
                    <p style="font-size: 14px; color: #DCE2F0;">
                        <strong>Registration Number:</strong> {row['Regd No.']}<br>
                        <strong>Name:</strong> {row['Name']}<br>
                        <strong>CGPA:</strong> {row['Cgpa']}
                    </p>
                </div>
            """, unsafe_allow_html=True)
        
        # Download filtered data
        st.write("### Download Data")
        csv = filtered_df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="Download data as CSV",
            data=csv,
            file_name='filtered_data.csv',
            mime='text/csv',
        )
        
        # Interactive map
        st.write("### Interactive Map")
        fig_map = px.scatter_geo(filtered_df, locations="State", locationmode='USA-states', 
                                 hover_name="Name", size="Cgpa", 
                                 projection="albers usa", title="Student Distribution by State")
        st.plotly_chart(fig_map)

elif page == "Student Comparison":
    st.write("### Student Comparison Tool")
    student1 = st.selectbox("Select first student", df['Name'].unique())
    student2 = st.selectbox("Select second student", df['Name'].unique())
    
    if student1 and student2:
        st.write(f"Comparing {student1} and {student2}")
        student1_data = df[df['Name'] == student1].iloc[0]
        student2_data = df[df['Name'] == student2].iloc[0]
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader(f"{student1}")
            st.markdown(f"**Registration Number:** {student1_data['Regd No.']}")
            st.markdown(f"**CGPA:** {student1_data['Cgpa']}")
            st.markdown(f"**Rank:** {student1_data['Rank']}")
        
        with col2:
            st.subheader(f"{student2}")
            st.markdown(f"**Registration Number:** {student2_data['Regd No.']}")
            st.markdown(f"**CGPA:** {student2_data['Cgpa']}")
            st.markdown(f"**Rank:** {student2_data['Rank']}")

elif page == "Shoutout to...":
    st.write("### Shoutout to...")
    random_student = df.sample(1).iloc[0]
    st.markdown(f"""
        <div style="background-color: #50586C; padding: 20px; border-radius: 10px;margin-top: 10px; border: 1px solid #DCE2F0;">
            <h2 style="color: #DCE2F0;">Rank: {random_student['Rank']}</h2>
            <p style="font-size: 18px; color: #DCE2F0;">
                <strong>Registration Number:</strong> {random_student['Regd No.']}<br>
                <strong>Name:</strong> {random_student['Name']}<br>
                <strong>CGPA:</strong> {random_student['Cgpa']}
            </p>
        </div>
    """, unsafe_allow_html=True)

elif page == "CGPA Distribution":
    st.write("### CGPA Distribution Histogram")
    fig = px.histogram(df, x='Cgpa', nbins=20, title='CGPA Distribution')
    st.plotly_chart(fig)

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