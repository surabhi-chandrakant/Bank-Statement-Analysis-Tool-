import pandas as pd
import os
from datetime import datetime

def save_to_csv(dataframe: pd.DataFrame, filename: str, output_dir: str = "output"):
    """Save DataFrame to CSV with timestamp"""
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{filename}_{timestamp}.csv"
    filepath = os.path.join(output_dir, filename)
    
    dataframe.to_csv(filepath, index=False)
    return filepath

def validate_transactions(transactions_df: pd.DataFrame) -> bool:
    """Basic validation of transactions DataFrame"""
    required_columns = ['transaction_date', 'description', 'withdrawal_amount', 'deposit_amount', 'balance']
    
    if not all(col in transactions_df.columns for col in required_columns):
        return False
    
    if transactions_df.empty:
        return False
    
    return True

def format_currency(amount: float) -> str:
    """Format amount as Indian currency"""
    if amount >= 10000000:  # 1 crore
        return f"₹{amount/10000000:.2f}Cr"
    elif amount >= 100000:  # 1 lakh
        return f"₹{amount/100000:.2f}L"
    else:
        return f"₹{amount:,.2f}"