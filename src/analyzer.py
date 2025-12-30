"""
Price Data Analyzer
Analyzes and visualizes e-commerce price trends
"""

import pandas as pd
import matplotlib.pyplot as plt
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import os
from config import PRICE_DATA_FILE, OUTPUT_DIR

class PriceAnalyzer:
    def __init__(self):
        self.df = None
        self.load_data()
    
    def load_data(self):
        """Load price data from CSV"""
        if not os.path.exists(PRICE_DATA_FILE):
            print(f"❌ Data file not found: {PRICE_DATA_FILE}")
            print("Please run scraper.py first to collect data.")
            return False
        
        self.df = pd.read_csv(PRICE_DATA_FILE)
        self.df['timestamp'] = pd.to_datetime(self.df['timestamp'])
        
        # Filter out records with no price
        self.df = self.df[self.df['price'].notna()]
        
        print(f"✅ Loaded {len(self.df)} price records")
        return True
    
    def generate_summary_statistics(self):
        """Generate summary statistics for each product"""
        if self.df is None or len(self.df) == 0:
            return None
        
        summary = []
        
        for product_title in self.df['title'].unique():
            product_df = self.df[self.df['title'] == product_title].copy()
            product_df = product_df.sort_values('timestamp')
            
            if len(product_df) > 0:
                current_price = product_df.iloc[-1]['price']
                min_price = product_df['price'].min()
                max_price = product_df['price'].max()
                avg_price = product_df['price'].mean()
                
                # Calculate price change
                if len(product_df) > 1:
                    first_price = product_df.iloc[0]['price']
                    price_change = current_price - first_price
                    price_change_pct = (price_change / first_price) * 100
                else:
                    price_change = 0
                    price_change_pct = 0
                
                summary.append({
                    'Product': product_title,
                    'Current Price': f'${current_price:.2f}',
                    'Min Price': f'${min_price:.2f}',
                    'Max Price': f'${max_price:.2f}',
                    'Avg Price': f'${avg_price:.2f}',
                    'Price Change': f'${price_change:+.2f}',
                    'Change %': f'{price_change_pct:+.2f}%',
                    'Records': len(product_df)
                })
        
        return pd.DataFrame(summary)
    
    def create_matplotlib_charts(self):
        """Create static charts using Matplotlib"""
        if self.df is None or len(self.df) == 0:
            return
        
        products = self.df['title'].unique()
        n_products = len(products)
        
        # Create subplots
        fig, axes = plt.subplots(n_products, 1, figsize=(12, 4 * n_products))
        
        if n_products == 1:
            axes = [axes]
        
        for idx, product in enumerate(products):
            product_df = self.df[self.df['title'] == product].copy()
            product_df = product_df.sort_values('timestamp')
            
            ax = axes[idx]
            ax.plot(product_df['timestamp'], product_df['price'], 
                   marker='o', linewidth=2, markersize=4)
            ax.set_title(f'{product} - Price Trend', fontsize=12, fontweight='bold')
            ax.set_xlabel('Date')
            ax.set_ylabel('Price ($)')
            ax.grid(True, alpha=0.3)
            ax.tick_params(axis='x', rotation=45)
            
            # Add min/max price annotations
            min_idx = product_df['price'].idxmin()
            max_idx = product_df['price'].idxmax()
            
            min_price = product_df.loc[min_idx, 'price']
            max_price = product_df.loc[max_idx, 'price']
            
            ax.axhline(y=min_price, color='green', linestyle='--', 
                      alpha=0.5, label=f'Min: ${min_price:.2f}')
            ax.axhline(y=max_price, color='red', linestyle='--', 
                      alpha=0.5, label=f'Max: ${max_price:.2f}')
            ax.legend()
        
        plt.tight_layout()
        output_path = os.path.join(OUTPUT_DIR, 'price_trends.png')
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        print(f"✅ Saved: {output_path}")
        plt.close()
    
    def create_plotly_interactive_chart(self):
        """Create interactive charts using Plotly"""
        if self.df is None or len(self.df) == 0:
            return
        
        products = self.df['title'].unique()
        
        # Create interactive line chart
        fig = go.Figure()
        
        for product in products:
            product_df = self.df[self.df['title'] == product].copy()
            product_df = product_df.sort_values('timestamp')
            
            fig.add_trace(go.Scatter(
                x=product_df['timestamp'],
                y=product_df['price'],
                mode='lines+markers',
                name=product,
                hovertemplate='<b>%{fullData.name}</b><br>' +
                             'Date: %{x|%Y-%m-%d}<br>' +
                             'Price: $%{y:.2f}<br>' +
                             '<extra></extra>'
            ))
        
        fig.update_layout(
            title='E-commerce Price Trends - Interactive View',
            xaxis_title='Date',
            yaxis_title='Price (USD)',
            hovermode='x unified',
            template='plotly_white',
            height=600,
            showlegend=True
        )
        
        output_path = os.path.join(OUTPUT_DIR, 'price_trends_interactive.html')
        fig.write_html(output_path)
        print(f"✅ Saved: {output_path}")
    
    def create_comparison_chart(self):
        """Create price comparison bar chart"""
        if self.df is None or len(self.df) == 0:
            return
        
        # Get latest price for each product
        latest_prices = []
        
        for product in self.df['title'].unique():
            product_df = self.df[self.df['title'] == product].copy()
            product_df = product_df.sort_values('timestamp')
            latest_price = product_df.iloc[-1]['price']
            latest_prices.append({
                'Product': product,
                'Price': latest_price
            })
        
        df_latest = pd.DataFrame(latest_prices)
        df_latest = df_latest.sort_values('Price', ascending=False)
        
        # Create bar chart
        fig = go.Figure(data=[
            go.Bar(
                x=df_latest['Product'],
                y=df_latest['Price'],
                text=df_latest['Price'].apply(lambda x: f'${x:.2f}'),
                textposition='auto',
                marker_color='steelblue'
            )
        ])
        
        fig.update_layout(
            title='Current Price Comparison',
            xaxis_title='Product',
            yaxis_title='Price (USD)',
            template='plotly_white',
            height=500
        )
        
        output_path = os.path.join(OUTPUT_DIR, 'price_comparison.html')
        fig.write_html(output_path)
        print(f"✅ Saved: {output_path}")


def main():
    """Main execution function"""
    print("📊 E-commerce Price Analyzer")
    print("=" * 60)
    
    analyzer = PriceAnalyzer()
    
    if analyzer.df is None or len(analyzer.df) == 0:
        print("❌ No data available for analysis")
        return
    
    # Generate summary statistics
    print("\n📈 Summary Statistics:")
    summary = analyzer.generate_summary_statistics()
    if summary is not None:
        print(summary.to_string(index=False))
    
    # Create visualizations
    print("\n🎨 Creating visualizations...")
    analyzer.create_matplotlib_charts()
    analyzer.create_plotly_interactive_chart()
    analyzer.create_comparison_chart()
    
    print("\n" + "=" * 60)
    print("✅ Analysis complete!")
    print(f"📁 Output files saved to: {OUTPUT_DIR}")


if __name__ == "__main__":
    main()