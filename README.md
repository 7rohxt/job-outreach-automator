# Smart Cold Email Generator (with Streamlit + LangChain)
This project helps you **generate personalized cold emails** from a job posting and your resume.  
Simply:  
1. Paste a **job posting URL**  
2. Upload your **resume** (TXT or PDF)  
3. Get a **smartly crafted cold email** (few-shot optimized) ready to send 🚀  

---

## Demo
![Demo](assets/demo.gif)

---

## Features
- **Job description extraction**: automatically parses job postings  
- **Resume parsing**: supports both `.txt` and `.pdf` formats  
- **Zero-shot & Few-shot email generation**: compare and refine outputs  
- **Vector DB retrieval**: picks the most relevant example for few-shot prompting  
- **Streamlit UI**: clean, side-by-side workflow  
- **Download emails**: export generated emails as `.txt` files  

---

## Tech Stack
- [LangChain](https://www.langchain.com/) (Groq, HuggingFace, Chroma)  
- [Streamlit](https://streamlit.io/) (UI)  
- [PyPDF2](https://pypi.org/project/pypdf2/) (PDF parsing)  
- [Python Dotenv](https://pypi.org/project/python-dotenv/) (for secrets)  

---

## Project Structure
```
smart-cold-email-generator/
├── .gitignore
├── LICENSE
├── README.md
├── requirements.txt        # dependencies
├── app.py                  # Streamlit app (UI)
├── langchain_helper.py     # core logic (extraction, email gen, retrieval)
├── few_shots.py            # few-shot examples
├── my_resume.txt
├── email_generator.ipynb
└── assets/                 # screenshots / demo video
    └── demo.mp4
```

---

## Setup & Installation

1. **Clone the repo**
   ```bash
   git clone https://github.com/your-username/smart-cold-email-generator.git
   cd smart-cold-email-generator
   ```

2. **Create & activate venv**
   ```bash
   python -m venv .venv
   source .venv/bin/activate    # macOS/Linux
   .venv\Scripts\activate       # Windows
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Environment variables**
   Create a `.env` file in the root with:
   ```env
   GROQ_API_KEY=your_api_key_here
   ```

---

## Usage

Run the Streamlit app:
```bash
streamlit run app.py
```

Then open http://localhost:8501 in your browser.

---

## Acknowledgements
- LangChain for the powerful agent framework
- Hugging Face for embeddings
- Groq for LLM inference
- Streamlit for the UI

---

## License
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## Contributing
Contributions are welcome! Please feel free to submit a Pull Request.