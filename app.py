import streamlit as st
import google.generativeai as genai
import os
import PyPDF2 as pdf
from docx import Document
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

# Gemini Pro Response
def get_gemini_response(input_text):
    model = genai.GenerativeModel("gemini-2.0-flash-lite")
    response = model.generate_content(input_text)
    return response.text

# Extract text from PDF
def input_pdf_text(uploaded_file):
    reader = pdf.PdfReader(uploaded_file)
    text = ""
    for page in reader.pages:
        text += page.extract_text() + "\n"
    return text

# Extract text from DOCX
def input_docx_text(uploaded_file):
    doc = Document(uploaded_file)
    text = ""
    for paragraph in doc.paragraphs:
        text += paragraph.text + "\n"
    return text

# Streamlit UI
st.title("📄 Smart ATS")
st.text("Improve Your Resume with AI-Powered ATS Insights")

jd = st.text_area("📌 Paste the Job Description")

uploaded_file = st.file_uploader(
    "📤 Upload your resume",
    type=["pdf", "docx"],
    help="Please upload a PDF or Word (.docx) document."
)

resume_text = ""
if uploaded_file is not None:
    if uploaded_file.name.endswith('.pdf'):
        resume_text = input_pdf_text(uploaded_file)
    elif uploaded_file.name.endswith('.docx'):
        resume_text = input_docx_text(uploaded_file)
    else:
        st.error("Unsupported file type. Please upload a PDF or Word document.")

if st.button("🔍 Submit"):
    if resume_text and jd:
        input_prompt = f"""
        Act like a highly intelligent and experienced ATS (Applicant Tracking System) specialized in tech roles like Software Engineering, Data Science, Data Analytics, and Big Data.
        
        Evaluate the resume below against the provided Job Description (JD). Output must be in the following structure:
        JD Match: <percentage>%
        Missing Keywords: keyword1, keyword2, keyword3
        Profile Summary: <concise summary>

        Resume:
        {resume_text}

        Job Description:
        {jd}
        """

        response = get_gemini_response(input_prompt)

        st.subheader("🤖 AI ATS Evaluation")

        # Split the response into parts for cleaner display
        try:
            lines = response.split('\n')
            match_score = ""
            missing_keywords = ""
            profile_summary = ""
            for line in lines:
                if "JD Match" in line:
                    match_score = line.split(":", 1)[1].strip()
                elif "Missing Keywords" in line:
                    missing_keywords = line.split(":", 1)[1].strip()
                elif "Profile Summary" in line:
                    profile_summary = line.split(":", 1)[1].strip()

            st.markdown(f"📊 Job Description Match:** {match_score}")
            st.markdown(f"❌ Missing Keywords:** {missing_keywords}")
            st.markdown(f"📝 Profile Summary:** {profile_summary}")

        except Exception as e:
            st.text("⚠ Could not parse the AI response properly. Here's the raw response:")
            st.text(response)
    else:
        st.warning("Please upload a resume and provide the Job Description.")