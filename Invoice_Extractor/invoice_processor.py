import json
import PyPDF2
from langchain_ollama import OllamaLLM
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from typing import Dict, List


class InvoiceProcessor:
    def __init__(self):
        # Initialize Ollama with Llama2 model
        self.llm = OllamaLLM(
            model="llama2",
            temperature=0.1,
            max_tokens=1000
        )
        
        # Define the extraction prompt template
        self.prompt_template = PromptTemplate(
            input_variables=["invoice_text"],
            template="""
            Extract the following information from the invoice text below and return it as a JSON object:
            
            Required fields:
            - invoice_number: The invoice number
            - invoice_date: The date of the invoice
            - company_name: The company issuing the invoice
            - company_address: The company's address
            - customer_name: The customer/client name
            - customer_address: The customer's address
            - items: List of items with description, quantity, unit_price, and total
            - subtotal: Subtotal amount
            - tax_amount: Tax amount
            - total_amount: Final total amount
            - phone: Company phone number (if available)
            - email: Company email (if available)
            
            Invoice text:
            {invoice_text}
            
            Example output format:
            {{
                "invoice_number": "INV-001",
                "invoice_date": "2024-01-15",
                "company_name": "ABC Corp",
                "company_address": "123 Main St, City, State 12345",
                "customer_name": "John Doe",
                "customer_address": "456 Oak Ave, Town, State 67890",
                "items": [
                    {{
                        "description": "Product A",
                        "quantity": 2,
                        "unit_price": 50.00,
                        "total": 100.00
                    }}
                ],
                "subtotal": 100.00,
                "tax_amount": 8.50,
                "total_amount": 108.50,
                "phone": "555-123-4567",
                "email": "info@abc.com"
            }}
            
            Please return only the JSON object, no additional text.
            """
        )
        
        # Create the LangChain chain
        self.chain = LLMChain(
            llm=self.llm,
            prompt=self.prompt_template
        )
    
    def extract_text_from_pdf(self, pdf_file) -> str:
        """Extract text content from PDF file"""
        try:
            pdf_reader = PyPDF2.PdfReader(pdf_file)
            text = ""
            
            for page in pdf_reader.pages:
                text += page.extract_text() + "\n"
            
            return text.strip()
        except Exception as e:
            raise Exception(f"Error extracting text from PDF: {str(e)}")
    
    def extract_invoice_data(self, pdf_file) -> Dict:
        """Process PDF and extract invoice data"""
        try:
            # Extract text from PDF
            invoice_text = self.extract_text_from_pdf(pdf_file)
            
            if not invoice_text:
                raise Exception("No text found in the PDF file")
            
            # Process with LLM
            response = self.chain.run(invoice_text=invoice_text)
            
            # Parse JSON response
            try:
                # Clean the response to extract JSON
                response = response.strip()
                if response.startswith("```\n"):
                    response = response[7:-3]
                elif response.startswith("```"):
                    response = response[3:-3]
                
                extracted_data = json.loads(response)
                return extracted_data
            
            except json.JSONDecodeError:
                # Fallback: try to extract JSON from response
                import re
                json_match = re.search(r'\{.*\}', response, re.DOTALL)
                if json_match:
                    extracted_data = json.loads(json_match.group())
                    return extracted_data
                else:
                    raise Exception("Unable to parse JSON from model response")
        
        except Exception as e:
            raise Exception(f"Error processing invoice: {str(e)}")
    
    def process_multiple_files(self, pdf_files: List) -> List[Dict]:
        """Process multiple PDF files"""
        results = []
        
        for pdf_file in pdf_files:
            try:
                data = self.extract_invoice_data(pdf_file)
                data['filename'] = pdf_file.name
                results.append(data)
            except Exception as e:
                results.append({
                    'filename': pdf_file.name,
                    'error': str(e)
                })
        
        return results
