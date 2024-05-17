from pdf2image import convert_from_bytes
import pytesseract
import streamlit as st
import requests
import urllib.parse
import json

 
def text_recognition(file): 
    if file:    
        pdf_document = file.read()
        pages = convert_from_bytes(pdf_document)
        result_str = ""
        # Perform OCR on each page
        for i, page in enumerate(pages):
            # Perform OCR on the page image
            text = pytesseract.image_to_string(page)
            # Print or process the extracted text
            result_str += f"Page {i+1}:\n{text}\n"
        return result_str
    else:
        return "Error: Please upload a file."
 
    
def store_document(file):
    url = "https://mistral.agreeabledune-08a9cefb.switzerlandnorth.azurecontainerapps.io/create_document_store_txt/?llm_model=mistral&ocr_language=eng&chunk_size=1000&chunk_overlap=20&batch_size=10&index_name=death_cert"
    payload = json.dumps({ "text_input": file})
    headers = {
    'accept': 'application/json',
    'Content-Type': 'application/json'
    }
    response = requests.request("POST", url, headers=headers, data=payload)
    st.session_state['ocr_result'] = response
    # st.write("store document response", response.text)


def query(question):
    encoded_query = urllib.parse.quote(question)
    url = f"https://mistral.agreeabledune-08a9cefb.switzerlandnorth.azurecontainerapps.io/query-nana/?query={encoded_query}&temperature=1&faiss_index=death_cert&number_of_sources=2"
    payload = {}
    headers = { 'accept': 'application/json'}
    # st.write(url)
    response = requests.request("POST", url, headers=headers, data=payload)
    # st.write("query status code", response.text)
    return response.json()

    
def main():
    
    st.header("Death Certificate Analyser")
    st.write("----")  
    
    st.subheader("Document Upload")
    ocr_file = st.file_uploader("Kindly upload your document below:", type='pdf')
    submit_ocr = st.button('Submit', key='ocr')
    
    # Initialize session state variables
    if 'ocr_result' not in st.session_state:
        st.session_state['ocr_result'] = None
            
    if submit_ocr and ocr_file is not None:
        with st.spinner("Uploading..."):
            try:
                result = text_recognition(ocr_file)
                st.write("debug")
                # st.session_state['ocr_result'] = result
                st.success("Document uploaded successfully!")
            except:
                st.error("There was an error uploading your document. Please try again.")
        with st.spinner("Processing..."):
            try:
                store_document(result)
                st.success("Document processed successfully!")
            except:
                st.error("There was an error processing your document. Please try again.")
        
    st.write("----")  

    if st.session_state['ocr_result']:
        st.subheader("What would you like to know?")
        question = st.text_area("Question", label_visibility="hidden")
        question_submit = st.button("Submit")
        
        if question_submit:
            with st.spinner("Fetching results..."):
                try:
                    result = query(question)
                    # st.markdown('***Results:***')
                    st.subheader('Results:')            
                    st.write(result)
                except Exception as e:
                    st.error(f"There was an error fetching the results: {e}")

if __name__ == "__main__":
    main()
