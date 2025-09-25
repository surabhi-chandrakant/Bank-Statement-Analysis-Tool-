import pandas as pd
import re
from typing import List, Dict, Tuple

class TransactionAnalyzer:
    def __init__(self):
        self.suspicious_entities = ['guddu', 'prabhat', 'arif', 'coal india']
    
    def flag_large_dd_withdrawals(self, transactions_df: pd.DataFrame, threshold: float = 10000) -> pd.DataFrame:
        """Flag DD withdrawals above threshold"""
        flagged = transactions_df.copy()
        
        def is_dd_withdrawal(description):
            desc_lower = str(description).lower()
            return ('dd' in desc_lower or 'demand draft' in desc_lower) and flagged['withdrawal_amount'] > 0
        
        flagged['is_large_dd'] = flagged.apply(
            lambda row: is_dd_withdrawal(row['description']) and row['withdrawal_amount'] > threshold, 
            axis=1
        )
        
        return flagged
    
    def flag_large_rtgs_deposits(self, transactions_df: pd.DataFrame, threshold: float = 50000) -> pd.DataFrame:
        """Flag RTGS deposits above threshold"""
        flagged = transactions_df.copy()
        
        def is_rtgs_deposit(description):
            desc_lower = str(description).lower()
            return 'rtgs' in desc_lower and flagged['deposit_amount'] > 0
        
        flagged['is_large_rtgs'] = flagged.apply(
            lambda row: is_rtgs_deposit(row['description']) and row['deposit_amount'] > threshold, 
            axis=1
        )
        
        return flagged
    
    def flag_specific_entities(self, transactions_df: pd.DataFrame) -> pd.DataFrame:
        """Flag transactions with specific entities"""
        flagged = transactions_df.copy()
        
        def contains_suspicious_entity(description):
            desc_lower = str(description).lower()
            return any(entity in desc_lower for entity in self.suspicious_entities)
        
        flagged['is_suspicious_entity'] = flagged['description'].apply(contains_suspicious_entity)
        
        return flagged
    
    def analyze_transactions(self, transactions_df: pd.DataFrame) -> Dict:
        """Complete analysis with all flags"""
        # Apply all flags
        analyzed_df = self.flag_large_dd_withdrawals(transactions_df)
        analyzed_df = self.flag_large_rtgs_deposits(analyzed_df)
        analyzed_df = self.flag_specific_entities(analyzed_df)
        
        # Generate summary statistics
        summary = {
            'total_transactions': len(analyzed_df),
            'total_withdrawals': analyzed_df['withdrawal_amount'].sum(),
            'total_deposits': analyzed_df['deposit_amount'].sum(),
            'large_dd_count': analyzed_df['is_large_dd'].sum(),
            'large_rtgs_count': analyzed_df['is_large_rtgs'].sum(),
            'suspicious_entity_count': analyzed_df['is_suspicious_entity'].sum(),
            'flagged_transactions': analyzed_df[
                analyzed_df['is_large_dd'] | 
                analyzed_df['is_large_rtgs'] | 
                analyzed_df['is_suspicious_entity']
            ].shape[0]
        }
        
        return analyzed_df, summary