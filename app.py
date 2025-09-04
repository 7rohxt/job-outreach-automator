import streamlit as st
from langchain_helper import (
    extract_job_description,
    resume_to_json,
    setup_vector_db,
    retrieve_example,
    generate_few_shot_email
)
from few_shots import few_shots

# ------------------------------------------------------------------------------------

# Streamlit Layout 
st.set_page_config(page_title="Smart Cold Email Generator", layout="wide")

st.title("📧 SmartApply - Cold Email Generator")
st.write("From job post + resume → to a smart, personalized email.")

# ------------------------------------------------------------------------------------

# Job description and Resume Side by Side
with st.container():
    col1, col2 = st.columns([1, 1], gap="large")

    # Extract Job Decsription
    with col1:
        st.markdown("### Step 1: Job Posting URL")
        job_url = st.text_input("Paste the job posting URL here:")

        if "job_description" not in st.session_state:
            st.session_state.job_description = None

        if st.button("Extract Job Description", use_container_width=True) and job_url:
            with st.spinner("Extracting job description..."):
                st.session_state.job_description = extract_job_description(job_url)
                st.success("✅ Job description extracted!")

    # Extract Resume
    with col2:
        st.markdown("### Step 2: Upload Resume")
        uploaded_resume = st.file_uploader("Upload your resume (.txt)", type=["txt"])

        if "resume" not in st.session_state:
            st.session_state.resume = None
        if "resume_file" not in st.session_state:
            st.session_state.resume_file = None

        if uploaded_resume is not None:
            if uploaded_resume.name != st.session_state.resume_file:
                with st.spinner("Parsing resume..."):
                    resume_text = uploaded_resume.read().decode("utf-8")
                    st.session_state.resume = resume_to_json(resume_text)
                    st.session_state.resume_file = uploaded_resume.name
                    st.success("✅ Resume parsed!")

# ------------------------------------------------------------------------------------

# Parsed outputs 
with st.container():
    col1, col2 = st.columns([1, 1], gap="large")

    with col1:
        with st.expander("👀 View Parsed Job Description", expanded=False):
            st.json(st.session_state.job_description)

    with col2:
        with st.expander("👀 View Parsed Resume", expanded=False):
            st.json(st.session_state.resume)
# ------------------------------------------------------------------------------------

# Generate Few-Shot Email 
if "email_few_shot" not in st.session_state:
    st.session_state.email_few_shot = None

if st.button("Generate Cold Email") and st.session_state.job_description and st.session_state.resume:
    with st.spinner("Generating personalized email..."):
        # Setup & retrieve example for Few-Shot
        setup_vector_db(few_shots)
        retrieved_example = retrieve_example("AI/ML Engineer with AWS and Python")
        st.session_state.email_few_shot = generate_few_shot_email(
            st.session_state.job_description, 
            st.session_state.resume, 
            retrieved_example
        )

# Display Few-Shot Email if generated
if st.session_state.email_few_shot:
    st.subheader("Personalized Few-Shot Email")
    st.text_area("Generated Email", st.session_state.email_few_shot, height=500)
    st.download_button(
        "📥 Download Email",
        st.session_state.email_few_shot,
        file_name="personalized_email.txt",
        key="download_few"
    )
