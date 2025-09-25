import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
from datetime import datetime

class StatementVisualizer:
    def __init__(self):
        self.color_scheme = {
            'withdrawal': '#EF553B',
            'deposit': '#00CC96',
            'balance': '#636EFA'
        }
    
    def create_timeline_plot(self, transactions_df: pd.DataFrame, bank_name: str = "") -> go.Figure:
        """Create timeline plot of withdrawals and deposits"""
        fig = go.Figure()
        
        # Add withdrawal traces
        withdrawals = transactions_df[transactions_df['withdrawal_amount'] > 0]
        if not withdrawals.empty:
            fig.add_trace(go.Scatter(
                x=withdrawals['transaction_date'],
                y=withdrawals['withdrawal_amount'],
                mode='markers+lines',
                name='Withdrawals',
                line=dict(color=self.color_scheme['withdrawal']),
                marker=dict(size=6)
            ))
        
        # Add deposit traces
        deposits = transactions_df[transactions_df['deposit_amount'] > 0]
        if not deposits.empty:
            fig.add_trace(go.Scatter(
                x=deposits['transaction_date'],
                y=deposits['deposit_amount'],
                mode='markers+lines',
                name='Deposits',
                line=dict(color=self.color_scheme['deposit']),
                marker=dict(size=6)
            ))
        
        # Add balance trace
        if 'balance' in transactions_df.columns:
            fig.add_trace(go.Scatter(
                x=transactions_df['transaction_date'],
                y=transactions_df['balance'],
                mode='lines',
                name='Balance',
                line=dict(color=self.color_scheme['balance'], dash='dot'),
                yaxis='y2'
            ))
        
        # Update layout
        title = f"Transaction Timeline - {bank_name}" if bank_name else "Transaction Timeline"
        fig.update_layout(
            title=title,
            xaxis_title="Date",
            yaxis_title="Amount (₹)",
            yaxis2=dict(
                title="Balance (₹)",
                overlaying='y',
                side='right'
            ),
            hovermode='x unified',
            template='plotly_white'
        )
        
        return fig
    
    def create_monthly_summary(self, transactions_df: pd.DataFrame) -> go.Figure:
        """Create monthly summary bar chart"""
        monthly_data = transactions_df.copy()
        monthly_data['month'] = monthly_data['transaction_date'].dt.to_period('M')
        
        monthly_summary = monthly_data.groupby('month').agg({
            'withdrawal_amount': 'sum',
            'deposit_amount': 'sum'
        }).reset_index()
        monthly_summary['month'] = monthly_summary['month'].astype(str)
        
        fig = go.Figure()
        
        fig.add_trace(go.Bar(
            x=monthly_summary['month'],
            y=monthly_summary['deposit_amount'],
            name='Deposits',
            marker_color=self.color_scheme['deposit']
        ))
        
        fig.add_trace(go.Bar(
            x=monthly_summary['month'],
            y=monthly_summary['withdrawal_amount'],
            name='Withdrawals',
            marker_color=self.color_scheme['withdrawal']
        ))
        
        fig.update_layout(
            title="Monthly Transaction Summary",
            xaxis_title="Month",
            yaxis_title="Amount (₹)",
            barmode='group',
            template='plotly_white'
        )
        
        return fig
    
    def create_flag_summary(self, analyzed_df: pd.DataFrame) -> go.Figure:
        """Create visualization for flagged transactions"""
        flag_counts = {
            'Large DD Withdrawals': analyzed_df['is_large_dd'].sum(),
            'Large RTGS Deposits': analyzed_df['is_large_rtgs'].sum(),
            'Suspicious Entities': analyzed_df['is_suspicious_entity'].sum()
        }
        
        fig = px.bar(
            x=list(flag_counts.keys()),
            y=list(flag_counts.values()),
            title="Flagged Transactions Summary",
            labels={'x': 'Flag Type', 'y': 'Count'},
            color=list(flag_counts.keys()),
            color_discrete_sequence=['#FFA15A', '#19D3F3', '#FF6692']
        )
        
        return fig