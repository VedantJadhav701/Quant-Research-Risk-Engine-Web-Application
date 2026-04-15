import numpy as np
import pandas as pd
from scipy.stats import t
import logging

logger = logging.getLogger(__name__)

class RiskSimulator:
    """
    Monte Carlo Risk Engine with adaptive regime logic.
    """
    def __init__(self, n_paths: int = 10000, horizon: int = 252):
        self.n_paths = n_paths
        self.horizon = horizon

    def estimate_nu(self, returns: pd.Series):
        """
        Estimates the degrees of freedom (nu) for the Student-t distribution.
        """
        try:
            # Fit Student-t to historical returns
            res = t.fit(returns)
            nu = res[0]
            # Bound nu between 2 and 30
            return max(2.0, min(30.0, nu))
        except:
            return 5.0 # Robust fallback

    def run_simulation(self, current_price: float, returns: pd.Series, regime: str):
        """
        Runs adaptive Monte Carlo simulation.
        """
        mu = returns.mean()
        sigma = returns.std()
        
        # Adaptive Logic based on Regime
        sim_paths = self.n_paths
        nu = self.estimate_nu(returns)
        
        if regime == 'High Volatility':
            sigma *= 1.2 # Scale up volatility
            nu = max(2.0, nu * 0.8) # Fatter tails
            sim_paths = int(self.n_paths * 1.5)
        elif regime == 'Low Volatility':
            sigma *= 0.9 # Scale down volatility
            nu = min(30.0, nu * 1.2) # Thinner tails
            sim_paths = int(self.n_paths * 0.8)
        
        logger.info(f"Simulating {sim_paths} paths with nu={nu:.2f}, sigma={sigma:.4f} for regime: {regime}")
        
        # Generate T-distributed random shocks
        # Student-t returns: mu + sigma * shocks
        # Note: scale needs to be adjusted for t-dist variance = nu / (nu - 2)
        scale = sigma / np.sqrt(nu / (nu - 2)) if nu > 2 else sigma
        
        shocks = t.rvs(df=nu, loc=mu, scale=scale, size=(self.horizon, sim_paths))
        
        # Calculate price paths
        # price_t = price_0 * exp(cumsum(returns))
        log_price_paths = np.log(current_price) + np.cumsum(shocks, axis=0)
        price_paths = np.exp(log_price_paths)
        
        return price_paths, nu

    def calculate_metrics(self, price_paths: np.ndarray, current_price: float):
        """
        Computes risk metrics from simulated paths.
        """
        # Final terminal returns
        terminal_returns = (price_paths[-1] - current_price) / current_price
        
        # VaR 95%
        var_95 = np.percentile(terminal_returns, 5)
        
        # CVaR 95%
        cvar_95 = terminal_returns[terminal_returns <= var_95].mean()
        
        # Sharpe Ratio (Simulated)
        # Assuming risk-free rate = 0 for simplicity in this metric
        expected_return = terminal_returns.mean()
        volatility = terminal_returns.std()
        sharpe = expected_return / volatility if volatility > 0 else 0
        
        # Max Drawdown for each path
        drawdowns = []
        for i in range(price_paths.shape[1]):
            path = price_paths[:, i]
            peak = np.maximum.accumulate(path)
            dd = (path - peak) / peak
            drawdowns.append(dd.min())
        
        max_dd = np.mean(drawdowns)
        
        return {
            'VaR_95': var_95,
            'CVaR_95': cvar_95,
            'Sharpe': sharpe,
            'Max_Drawdown': max_dd,
            'Expected_Return': expected_return
        }
