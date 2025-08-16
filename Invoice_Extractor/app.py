import streamlit as st
import pandas as pd
import json
from invoice_processor import InvoiceProcessor
from io import BytesIO

def main():
    st.set_page_config(
        page_title="Invoice Extraction Bot",
        page_icon="📄",
        layout="wide"
    )
    
    st.title("📄 Invoice Extraction Bot")
    st.markdown("### Extract structured data from invoices using LangChain and Ollama Llama2")
    
    # Initialize the processor
    if 'processor' not in st.session_state:
        with st.spinner("Initializing Llama2 model..."):
            st.session_state.processor = InvoiceProcessor()
    
    # File upload section
    st.header("Upload Invoice Files")
    uploaded_files = st.file_uploader(
        "Choose PDF files",
        type=['pdf'],
        accept_multiple_files=True,
        help="Upload one or more PDF invoice files"
    )
    
    if uploaded_files:
        st.success(f"Uploaded {len(uploaded_files)} file(s)")
        
        # Display uploaded files
        with st.expander("Uploaded Files"):
            for file in uploaded_files:
                st.write(f"• {file.name} ({file.size} bytes)")
        
        # Extract data button
        if st.button("🚀 Extract Data", type="primary"):
            with st.spinner("Processing invoices... This may take a few minutes."):
                try:
                    # Process files
                    results = st.session_state.processor.process_multiple_files(uploaded_files)
                    
                    # Store results in session state
                    st.session_state.extraction_results = results
                    
                    st.success("✅ Data extraction completed!")
                    
                except Exception as e:
                    st.error(f"Error during processing: {str(e)}")
    
    # Display results
    if 'extraction_results' in st.session_state:
        st.header("📊 Extraction Results")
        
        results = st.session_state.extraction_results
        
        # Summary metrics
        col1, col2, col3 = st.columns(3)
        
        successful = len([r for r in results if 'error' not in r])
        failed = len([r for r in results if 'error' in r])
        
        with col1:
            st.metric("Total Files", len(results))
        with col2:
            st.metric("Successful", successful, delta=successful)
        with col3:
            st.metric("Failed", failed, delta=-failed if failed > 0 else 0)
        
        # Detailed results
        for i, result in enumerate(results):
            filename = result.get('filename', f'File {i+1}')
            
            with st.expander(f"📄 {filename}"):
                if 'error' in result:
                    st.error(f"Error: {result['error']}")
                else:
                    # Display extracted data
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.subheader("Invoice Information")
                        st.write(f"**Invoice Number:** {result.get('invoice_number', 'N/A')}")
                        st.write(f"**Date:** {result.get('invoice_date', 'N/A')}")
                        st.write(f"**Total Amount:** {result.get('total_amount', 'N/A')}")
                        st.write(f"**Subtotal:** {result.get('subtotal', 'N/A')}")
                        st.write(f"**Tax:** {result.get('tax_amount', 'N/A')}")
                    
                    with col2:
                        st.subheader("Company & Customer")
                        st.write(f"**Company:** {result.get('company_name', 'N/A')}")
                        st.write(f"**Customer:** {result.get('customer_name', 'N/A')}")
                        st.write(f"**Phone:** {result.get('phone', 'N/A')}")
                        st.write(f"**Email:** {result.get('email', 'N/A')}")
                    
                    # Items table
                    if 'items' in result and result['items']:
                        st.subheader("Invoice Items")
                        items_df = pd.DataFrame(result['items'])
                        st.dataframe(items_df, use_container_width=True)
                    
                    # Raw JSON
                    with st.expander("Raw JSON Data"):
                        st.json(result)
        
        # Download CSV functionality
        if successful > 0:
            st.header("📥 Download Results")
            
            # Prepare data for CSV
            csv_data = []
            for result in results:
                if 'error' not in result:
                    # Flatten the data for CSV
                    flat_data = {
                        'filename': result.get('filename', ''),
                        'invoice_number': result.get('invoice_number', ''),
                        'invoice_date': result.get('invoice_date', ''),
                        'company_name': result.get('company_name', ''),
                        'customer_name': result.get('customer_name', ''),
                        'total_amount': result.get('total_amount', ''),
                        'subtotal': result.get('subtotal', ''),
                        'tax_amount': result.get('tax_amount', ''),
                        'phone': result.get('phone', ''),
                        'email': result.get('email', ''),
                        'items_count': len(result.get('items', []))
                    }
                    csv_data.append(flat_data)
            
            if csv_data:
                df = pd.DataFrame(csv_data)
                csv_buffer = BytesIO()
                df.to_csv(csv_buffer, index=False)
                
                st.download_button(
                    label="📊 Download CSV",
                    data=csv_buffer.getvalue(),
                    file_name="invoice_extraction_results.csv",
                    mime="text/csv"
                )
    
    # Information sidebar
    with st.sidebar:
        st.header("ℹ️ About")
        st.markdown("""
        This invoice extraction bot uses:
        - **LangChain** for LLM orchestration
        - **Ollama Llama2** for text processing
        - **Streamlit** for the web interface
        - **PyPDF2** for PDF text extraction
        
        ### Features:
        - ✅ Batch processing of multiple PDFs
        - ✅ Structured data extraction
        - ✅ CSV export functionality
        - ✅ Error handling and validation
        - ✅ Real-time processing status
        """)
        
        st.header("🔧 Configuration")
        st.markdown("""
        **Model:** Llama2  
        **Temperature:** 0.1  
        **Max Tokens:** 1000  
        """)

if __name__ == "__main__":
    main()
