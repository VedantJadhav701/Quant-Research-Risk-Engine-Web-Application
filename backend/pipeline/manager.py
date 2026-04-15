import numpy as np
import logging
import json
from datetime import datetime
from backend.data.ingestor import DataIngestor
from backend.volatility.engine import VolatilityEngine
from backend.regime.classifier import RegimeClassifier
from backend.risk.simulator import RiskSimulator

# Setup structured logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PipelineManager:
    """
    Integrates all modules into a context-aware execution flow.
    """
    def __init__(self):
        self.data_ingestor = DataIngestor()
        self.vol_engine = VolatilityEngine()
        self.regime_classifier = RegimeClassifier()
        self.risk_simulator = RiskSimulator()

    def run_analysis(self, ticker: str, start_date: str, end_date: str, custom_data_path: str = None):
        """
        Runs the full assessment pipeline.
        """
        start_time = datetime.now()
        logger.info(f"Starting pipeline analysis for {ticker}")
        
        # 1. Data Ingestion
        if custom_data_path:
            df = self.data_ingestor.process_custom_data(custom_data_path)
            data_source = "custom_upload"
        else:
            df = self.data_ingestor.fetch_ticker_data(ticker, start_date, end_date)
            data_source = "yfinance"
        
        current_price = df['Close'].iloc[-1]
        
        # 2. Regime Detection
        df_regime = self.regime_classifier.detect_regimes(df)
        current_regime = df_regime['regime'].iloc[-1]
        
        # 3. Volatility Surface
        surface_df = self.vol_engine.generate_surface_data(df, current_price)
        grid_x, grid_y, grid_z = self.vol_engine.create_mesh_grid(surface_df)
        
        # 4. Adaptive Monte Carlo
        # Adaptive logic is handled inside RiskSimulator based on current_regime
        price_paths, estimated_nu = self.risk_simulator.run_simulation(
            current_price, 
            df['log_return'], 
            current_regime
        )
        risk_metrics = self.risk_simulator.calculate_metrics(price_paths, current_price)
        
        # 5. Result Formatting
        execution_time = (datetime.now() - start_time).total_seconds()
        
        # Structured Logging for Engineering Signals
        logger.info(json.dumps({
            "event": "analysis_complete",
            "ticker": ticker,
            "regime": current_regime,
            "nu": estimated_nu,
            "VaR_95": risk_metrics['VaR_95'],
            "CVaR_95": risk_metrics['CVaR_95'],
            "data_source": data_source,
            "execution_seconds": execution_time
        }))
        
        # Final check for JSON compliance (replace NaN/Inf)
        def clean_json(obj):
            if isinstance(obj, list):
                return [clean_json(x) for x in obj]
            if isinstance(obj, dict):
                return {k: clean_json(v) for k, v in obj.items()}
            # Handle float, np.float64, etc.
            if isinstance(obj, (float, np.floating)):
                if np.isnan(obj) or np.isinf(obj):
                    return None
            return obj

        return clean_json({
            "metadata": {
                "ticker": ticker,
                "current_price": float(current_price),
                "regime": current_regime,
                "data_source": data_source,
                "execution_time": execution_time,
                "timestamp": datetime.now().isoformat()
            },
            "regime_data": {
                "dates": df_regime.index.strftime('%Y-%m-%d').tolist(),
                "prices": df_regime['Close'].fillna(0).tolist(),
                "regimes": df_regime['regime'].fillna("Unknown").tolist()
            },
            "volatility": {
                "surface": {
                    "x": grid_x.tolist(), # Strike
                    "y": grid_y.tolist(), # Expiry
                    "z": grid_z.tolist()  # IV
                },
                "raw_points": surface_df.to_dict(orient='records')
            },
            "risk": {
                "metrics": risk_metrics,
                "simulation": {
                    # For performance, only return a subset of paths for the UI
                    "paths": price_paths[:, :100].tolist(), 
                    "horizon": self.risk_simulator.horizon
                }
            }
        })
