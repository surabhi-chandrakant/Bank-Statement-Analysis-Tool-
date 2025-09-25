import streamlit as st
import pandas as pd
import os
import tempfile
from pdf_extractor import PDFExtractor
from analyzer import TransactionAnalyzer
from visualizer import StatementVisualizer
import pdfplumber

# Page configuration
st.set_page_config(
    page_title="Bank Statement Analyzer",
    page_icon="🏦",
    layout="wide"
)

def main():
    st.title("🏦 Bank Statement Analysis Tool")
    st.markdown("Upload your bank statement PDF to analyze transactions and detect patterns.")
    
    # Debug mode toggle
    debug_mode = st.sidebar.checkbox("Debug Mode", value=True)
    
    # File upload
    uploaded_file = st.file_uploader("Choose a PDF file", type="pdf")
    
    if uploaded_file is not None:
        # Create temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
            tmp_file.write(uploaded_file.getvalue())
            tmp_path = tmp_file.name
        
        try:
            # Initialize components
            extractor = PDFExtractor()
            analyzer = TransactionAnalyzer()
            visualizer = StatementVisualizer()
            
            # Extract raw text for debugging
            if debug_mode:
                with pdfplumber.open(tmp_path) as pdf:
                    debug_text = ""
                    for i, page in enumerate(pdf.pages):
                        text = page.extract_text()
                        if text:
                            debug_text += f"--- Page {i+1} ---\n{text}\n\n"
                
                with st.expander("🔍 Raw Text Preview (Debug)"):
                    st.text_area("Full Text", debug_text, height=300)
            
            # Extract data
            with st.spinner("Extracting data from PDF..."):
                account_df, transactions_df, bank_type = extractor.extract_from_pdf(tmp_path)
            
            st.success(f"✅ Successfully processed {bank_type} bank statement!")
            
            # Display account information
            st.subheader("📋 Account Information")
            col1, col2 = st.columns(2)
            
            with col1:
                st.info(f"**Bank:** {account_df['bank_name'].iloc[0]}")
                st.info(f"**Account Holder:** {account_df['account_holder_name'].iloc[0]}")
                st.info(f"**Account Number:** {account_df['account_number'].iloc[0]}")
            
            with col2:
                st.info(f"**Account Type:** {account_df['account_type'].iloc[0]}")
                st.info(f"**IFSC:** {account_df['ifsc'].iloc[0]}")
                st.info(f"**MICR:** {account_df['micr'].iloc[0]}")
            
            if debug_mode:
                st.subheader("🔧 Debug Information")
                st.write("**Account DataFrame:**")
                st.dataframe(account_df)
                st.write(f"**Transactions DataFrame shape:** {transactions_df.shape}")
                st.write(f"**Bank Type Detected:** {bank_type}")
            
            # Analyze transactions if we have them
            if not transactions_df.empty:
                analyzed_df, summary = analyzer.analyze_transactions(transactions_df)
                
                # Display summary metrics
                st.subheader("📊 Transaction Summary")
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    st.metric("Total Transactions", len(analyzed_df))
                
                with col2:
                    total_withdrawal = analyzed_df['withdrawal_amount'].sum()
                    st.metric("Total Withdrawal", f"₹{total_withdrawal:,.2f}")
                
                with col3:
                    total_deposit = analyzed_df['deposit_amount'].sum()
                    st.metric("Total Deposit", f"₹{total_deposit:,.2f}")
                
                with col4:
                    st.metric("Flagged Transactions", summary['flagged_transactions'])
                
                # Visualization
                st.subheader("📈 Transaction Timeline")
                timeline_fig = visualizer.create_timeline_plot(analyzed_df, bank_type)
                st.plotly_chart(timeline_fig, use_container_width=True)
                
                # Flagged transactions
                st.subheader("🚩 Flagged Transactions Analysis")
                flagged_df = analyzed_df[
                    analyzed_df['is_large_dd'] | 
                    analyzed_df['is_large_rtgs'] | 
                    analyzed_df['is_suspicious_entity']
                ]
                
                if not flagged_df.empty:
                    st.dataframe(flagged_df, use_container_width=True)
                else:
                    st.success("🎉 No suspicious transactions detected!")
                
                # Raw transactions data
                st.subheader("💾 All Transactions")
                st.dataframe(analyzed_df, use_container_width=True)
                
            else:
                st.warning("⚠️ No transactions found in the statement.")
                if debug_mode:
                    st.write("This might be due to:")
                    st.write("- PDF text extraction issues")
                    st.write("- Unrecognized transaction format")
                    st.write("- Empty statement period")
                    
                    # Show sample of what was extracted
                    if debug_mode:
                        st.write("**First few lines of raw text for analysis:**")
                        with pdfplumber.open(tmp_path) as pdf:
                            first_page_text = pdf.pages[0].extract_text()
                            lines = first_page_text.split('\n')
                            for i, line in enumerate(lines[:10]):
                                st.write(f"{i}: {line}")
                
        except Exception as e:
            st.error(f"❌ Error processing PDF: {str(e)}")
            if debug_mode:
                import traceback
                st.code(traceback.format_exc())
        
        finally:
            # Clean up temporary file
            if os.path.exists(tmp_path):
                os.remove(tmp_path)
    
    else:
        # Instructions
        st.info("👆 Please upload a bank statement PDF to get started")
        
        st.markdown("""
        ### 📋 Supported Banks:
        - ✅ **HDFC Bank** - Full support
        - ✅ **ICICI Bank** - Full support
        
        ### 🚀 Features:
        - **Automated PDF data extraction**
        - **Transaction analysis and flagging**
        - **Interactive visualizations** 
        - **Suspicious activity detection**
        - **CSV export capability**
        
        ### 🔧 Debug Mode:
        Enable **Debug Mode** in sidebar to see:
        - Raw extracted text
        - DataFrames during processing
        - Detailed error information
        """)

if __name__ == "__main__":
    main()