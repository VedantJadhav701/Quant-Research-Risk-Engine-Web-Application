import numpy as np
from scipy.stats import norm
from scipy.optimize import newton
import pandas as pd
from scipy.interpolate import griddata
import logging

logger = logging.getLogger(__name__)

class VolatilityEngine:
    """
    Mathematical engine for Volatility Surface and IV calculation.
    """
    def __init__(self):
        pass

    @staticmethod
    def black_scholes_price(S, K, T, r, sigma, option_type='call'):
        """
        Calculates Black-Scholes price.
        """
        if T <= 0: return max(0, S - K) if option_type == 'call' else max(0, K - S)
        
        d1 = (np.log(S / K) + (r + 0.5 * sigma**2) * T) / (sigma * np.sqrt(T))
        d2 = d1 - sigma * np.sqrt(T)
        
        if option_type == 'call':
            return S * norm.cdf(d1) - K * np.exp(-r * T) * norm.cdf(d2)
        else:
            return K * np.exp(-r * T) * norm.cdf(-d2) - S * norm.cdf(-d1)

    @staticmethod
    def black_scholes_vega(S, K, T, r, sigma):
        """
        Calculates Vega (derivative w.r.t sigma).
        """
        d1 = (np.log(S / K) + (r + 0.5 * sigma**2) * T) / (sigma * np.sqrt(T))
        return S * norm.pdf(d1) * np.sqrt(T)

    def calculate_iv(self, market_price, S, K, T, r, option_type='call'):
        """
        Computes Implied Volatility using Newton-Raphson.
        """
        if market_price <= 0: return 0.0
        
        # Helper function for newton solver
        def f(sigma):
            return self.black_scholes_price(S, K, T, r, sigma, option_type) - market_price
        
        def fprime(sigma):
            return self.black_scholes_vega(S, K, T, r, sigma)

        try:
            # Initial guess: 20%
            iv = newton(f, x0=0.2, fprime=fprime, maxiter=100)
            return max(0, iv)
        except:
            return 0.0

    def generate_surface_data(self, ticker_data: pd.DataFrame, current_price: float):
        """
        Generates 3D Volatility Surface data.
        Incorporates skew and term structure.
        """
        # Define grid for strikes and expiries
        strikes = np.linspace(current_price * 0.8, current_price * 1.2, 10)
        expiries = np.array([1/12, 3/12, 6/12, 1.0, 2.0]) # 1m to 2y
        
        # Base volatility from historical data (average rolling vol)
        base_vol = ticker_data['rolling_vol'].mean()
        
        # Advanced Model parameters (Skew & Term Structure)
        skew = -0.15 # Typical negative skew for indices/stocks
        term_structure = 0.05 # Vol increases with time
        
        surface_points = []
        for T in expiries:
            for K in strikes:
                # iv = base_vol + skew_impact + term_impact
                # Normalize strike impact: (K-S)/S
                strike_impact = skew * (K - current_price) / current_price
                term_impact = term_structure * np.sqrt(T)
                iv = base_vol + strike_impact + term_impact
                
                surface_points.append({
                    'strike': K,
                    'expiry': T,
                    'iv': max(0.01, iv) # Floor at 1%
                })
        
        return pd.DataFrame(surface_points)

    def create_mesh_grid(self, surface_df: pd.DataFrame):
        """
        Interpolates discrete points into a smooth grid for plotting.
        """
        grid_x, grid_y = np.mgrid[
            surface_df.strike.min():surface_df.strike.max():50j,
            surface_df.expiry.min():surface_df.expiry.max():50j
        ]
        
        points = surface_df[['strike', 'expiry']].values
        values = surface_df['iv'].values
        
        grid_z = griddata(points, values, (grid_x, grid_y), method='cubic')
        
        # Replace NaNs (from griddata boundary issues) with 0 or a floor value
        grid_z = np.nan_to_num(grid_z, nan=0.0)
        
        return grid_x, grid_y, grid_z
