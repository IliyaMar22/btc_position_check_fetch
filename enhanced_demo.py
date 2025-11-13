#!/usr/bin/env python3
"""
Enhanced BTC CPI Analysis Demo
==============================

This demo showcases the ultra-advanced features of the enhanced BTC CPI analyzer.
Run this script to see the comprehensive analysis in action.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from enhanced_btc_cpi_analyzer import UltraAdvancedCPIBitcoinAnalyzer
import matplotlib.pyplot as plt
import warnings
warnings.filterwarnings('ignore')

def run_demo():
    """Run the enhanced BTC CPI analysis demo."""
    print("🚀 Enhanced BTC CPI Analysis Demo")
    print("=" * 50)
    print()
    
    # Initialize the ultra-advanced analyzer
    print("Initializing Ultra-Advanced CPI-Bitcoin Analyzer...")
    analyzer = UltraAdvancedCPIBitcoinAnalyzer()
    
    try:
        # Run the comprehensive analysis
        print("\nStarting comprehensive analysis...")
        results = analyzer.run_ultra_comprehensive_analysis()
        
        # Display key insights
        print("\n" + "="*70)
        print("🎯 KEY INSIGHTS SUMMARY")
        print("="*70)
        
        if 'btc_analysis' in results and results['btc_analysis'] is not None:
            clean_data = results['btc_analysis'].dropna(subset=['cpi_surprise', 'btc_return_15min'])
            
            print(f"\n📊 Analysis Summary:")
            print(f"• Total CPI Events Analyzed: {len(clean_data)}")
            print(f"• Average CPI Surprise: {clean_data['cpi_surprise'].mean():.3f}%")
            print(f"• Average BTC 15-min Return: {clean_data['btc_return_15min'].mean():.3f}%")
            print(f"• CPI-BTC Correlation: {clean_data['cpi_surprise'].corr(clean_data['btc_return_15min']):.3f}")
            
            # Market regime breakdown
            if 'market_regime' in clean_data.columns:
                regime_counts = clean_data['market_regime'].value_counts()
                print(f"\n🎭 Market Regime Distribution:")
                for regime, count in regime_counts.items():
                    print(f"  {regime.replace('_', ' ').title()}: {count} events ({count/len(clean_data)*100:.1f}%)")
        
        # Monte Carlo insights
        if 'monte_carlo' in results and results['monte_carlo']:
            print(f"\n🎲 Monte Carlo Simulation Results:")
            for regime, stats in results['monte_carlo']['statistics'].items():
                print(f"  {regime.replace('_', ' ').title()}:")
                print(f"    Expected Return: {stats['mean_return']:.2f}%")
                print(f"    Volatility: {stats['std_return']:.2f}%")
                print(f"    Sharpe Ratio: {stats['sharpe_ratio']:.3f}")
                print(f"    95% VaR: {stats['var_95']:.2f}%")
        
        # ML Model performance
        if 'ml_models' in results and results['ml_models']:
            print(f"\n🤖 Machine Learning Model Performance:")
            if 'ensemble' in results['ml_models']:
                print(f"  Ensemble R²: {results['ml_models']['ensemble']['r2']:.3f}")
                print(f"  Ensemble RMSE: {results['ml_models']['ensemble']['rmse']:.3f}%")
            
            if 'models' in results['ml_models']:
                best_model = max(results['ml_models']['models'].items(), 
                               key=lambda x: x[1]['test_r2'])
                print(f"  Best Model: {best_model[0]} (R²: {best_model[1]['test_r2']:.3f})")
        
        print(f"\n📁 Generated Files:")
        print("  • ultra_advanced_cpi_analysis.png - Static dashboard")
        print("  • ultra_advanced_cpi_dashboard.html - Interactive dashboard")
        
        print(f"\n✅ Demo completed successfully!")
        print("="*70)
        
        return results
        
    except Exception as e:
        print(f"\n❌ Demo failed: {e}")
        import traceback
        traceback.print_exc()
        return None

def quick_analysis():
    """Run a quick analysis for demonstration purposes."""
    print("⚡ Quick Analysis Mode")
    print("=" * 30)
    
    analyzer = UltraAdvancedCPIBitcoinAnalyzer()
    
    try:
        # Fetch data
        print("Fetching data...")
        multi_asset_data = analyzer.fetch_enhanced_multi_asset_data()
        cpi_data = analyzer.fetch_enhanced_cpi_data()
        
        # Quick analysis
        print("Running quick analysis...")
        btc_analysis = analyzer.analyze_enhanced_btc_reaction()
        
        # Quick Monte Carlo
        print("Running Monte Carlo simulation...")
        monte_carlo = analyzer.run_enhanced_monte_carlo_simulation(n_simulations=500)
        
        # Quick visualizations
        print("Creating visualizations...")
        analyzer.create_ultra_advanced_visualizations()
        
        print("✅ Quick analysis completed!")
        
        return {
            'multi_asset_data': multi_asset_data,
            'cpi_data': cpi_data,
            'btc_analysis': btc_analysis,
            'monte_carlo': monte_carlo
        }
        
    except Exception as e:
        print(f"❌ Quick analysis failed: {e}")
        return None

if __name__ == "__main__":
    print("Choose analysis mode:")
    print("1. Full comprehensive analysis (recommended)")
    print("2. Quick analysis (faster)")
    
    choice = input("\nEnter choice (1 or 2): ").strip()
    
    if choice == "2":
        results = quick_analysis()
    else:
        results = run_demo()
    
    if results:
        print(f"\n🎉 Analysis completed! Check the generated files for detailed results.")
    else:
        print(f"\n❌ Analysis failed. Please check the error messages above.")






