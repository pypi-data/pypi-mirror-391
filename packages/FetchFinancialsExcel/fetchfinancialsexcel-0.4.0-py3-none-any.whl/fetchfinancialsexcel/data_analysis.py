import pandas as pd
from datetime import datetime
from collections import defaultdict
import statistics as stats
from datetime import timedelta
import statistics as stats
import numpy as np

import statsmodels.api as sm
from sklearn.preprocessing import StandardScaler
import pandas_datareader.data as web


now = datetime.today()
CURRENT_YEAR = now.strftime("%Y")

# Greenblatt Magic Formula number 
def greenblatt_formula(df): 
    
    df = df.copy()
    
    # Mask för rader där PE och ROE är varken None eller 0
    valid_mask = (
        df[f"PE {CURRENT_YEAR}"].notna() & 
        df["ROCE"].notna() &
        (df[f"PE {CURRENT_YEAR}"] != 0) & 
        (df["ROCE"] != 0)
    )

    # Initiera kolumn med None
    df["Greenblatt Formula"] = None

    # Rangordna bara giltiga rader
    PE_rank = df.loc[valid_mask, f"PE {CURRENT_YEAR}"].rank(ascending=True, method="min")
    ROE_rank = df.loc[valid_mask, "ROE"].rank(ascending=False, method="min")

    # Summera rank och skriv in i nya kolumnen för giltiga rader
    for idx in PE_rank.index:
        df.at[idx, "Greenblatt Formula"] = PE_rank[idx] + ROE_rank[idx]

    return df

# standardavvikelsen av monethly return de senaste 36 månaderna 
# rank in ascending order 
def volatility(price_data):
    if len(price_data) < 38:  # Behöver minst 38 dagars data för 36 månaders tillväxt
        return None, [], []

    try:
        for d in price_data:
            if isinstance(d['date'], str):
                d['date'] = datetime.strptime(d['date'], '%Y-%m-%d')

        price_data.sort(key=lambda x: x['date'])

        monthly_data = defaultdict(list)
        for entry in price_data:
            key = (entry['date'].year, entry['date'].month)
            monthly_data[key].append(entry)

        last_day_adj_closes = [entries[-1]['adjusted_close'] for key, entries in sorted(monthly_data.items())]
        last_36_adj_closes = last_day_adj_closes[-38:]

        if len(last_36_adj_closes) < 14:
            return None, [], []

        monthly_growths = []
        for idx in range(1, len(last_36_adj_closes)-1):
            growth = last_36_adj_closes[idx+1] / last_36_adj_closes[idx] - 1
            monthly_growths.append(growth)

        std = stats.stdev(monthly_growths)
        return std, last_36_adj_closes, monthly_growths

    except Exception:
        return None, [], []

# NPY - formel från artikeln "formula investing"
def NPY(closing_prices, data, price_data): 
    def find_adjusted_close_on_or_after(date, stock_prices):
        # Convert to set of available dates for faster lookup
        available_dates = {entry['date'].date(): entry['adjusted_close'] for entry in stock_prices}
        
        # Start at the given date and move forward until found
        while date.date() not in available_dates:
            date += timedelta(days=1)
        
        return available_dates[date.date()]
   
    N = len(closing_prices)
    R = closing_prices[N-1] / closing_prices[N-13] - 1
    inc_data = data.get("Financials", {}).get("Balance_Sheet", {}).get("yearly", {})
    
    sorted_Years = sorted(inc_data.items(), reverse=True)[0:2]

    latest_year = sorted_Years[0][1].get("commonStockSharesOutstanding")
    date_last_year= datetime.strptime(sorted_Years[0][1].get("date"), '%Y-%m-%d') 

    second_latest_year = sorted_Years[1][1].get("commonStockSharesOutstanding")
    date_second_last_year= datetime.strptime(sorted_Years[1][1].get("date"), '%Y-%m-%d') 

    price_last_year = find_adjusted_close_on_or_after(date_last_year, price_data)
    price_second_last_year = find_adjusted_close_on_or_after(date_second_last_year, price_data)
    
    mc_last_year = price_last_year * float(latest_year)
    mc_second_last_year = price_second_last_year * float(second_latest_year)

    delta = mc_last_year / mc_second_last_year

    NPY = R - stats.log(delta)
    
    return NPY 

# Momentum: komulativ produkt av pristillväxt de senaste elva månaderna
def momentum(monthly_growths): 
    c_growth = 1 
    for m_growth in monthly_growths[-12:-1]: 
        c_growth = c_growth * (m_growth + 1)
    return c_growth -1 

# used within wrapper
def conservative(data, price_data): 
    try:
        vol, closing_prices, monthly_growths = volatility(price_data)
    except Exception as e:
        vol = None
        closing_prices = []
        monthly_growths = []

    try:
        if closing_prices and data:
            npy = NPY(closing_prices, data, price_data)
        else:
            npy = None
    except Exception as e:
        npy = None

    try:
        if monthly_growths and len(monthly_growths) >= 12:
            moment = momentum(monthly_growths)
        else:
            moment = None
    except Exception as e:
        moment = None

    return {
        "volatility": vol,
        "npy": npy,
        "moment": moment
    }

# used in analysis section 
def conservative_formula(df, separate_data_list):
    df_temp = pd.DataFrame(separate_data_list)

    # Steg 1: Rankningar (NaN behålls automatiskt vid saknade värden)
    df_temp['volatility_rank'] = df_temp['volatility'].rank(ascending=True, method='min')
    df_temp['npy_rank']        = df_temp['npy'].rank(ascending=False, method='min')
    df_temp['moment_rank']     = df_temp['moment'].rank(ascending=False, method='min')

    # Steg 2: Beräkna snitt-rank om alla tre finns, annars sätt None
    scores_dict = {}
    for _, entry in df_temp.iterrows():
        company = entry['Ticker']
        ranks = [entry['volatility_rank'], entry['npy_rank'], entry['moment_rank']]
        
        if all(pd.notna(ranks)):
            avg_rank = round(sum(ranks) / 3, 1)
        else:
            avg_rank = None

        scores_dict[company] = avg_rank

    # Steg 3: Lägg till i ursprungliga df
    scores_series = pd.Series(scores_dict, name='conservative_score')
    df['Conservative Formula'] = df['Ticker'].map(scores_series)

    return df

# used in analysis section
# This closely follows the academic definition of "quality" used by:
#Asness, Frazzini, and Pedersen (in "Quality Minus Junk")
#Novy-Marx (Gross Profitability)
#Green, Hand, Soliman (Accruals and investment patterns)

def quality_score(df):
    df = df.copy()
    
    try:
        z_norm_grossp = (df['Bruttovinstmarginal'] - df['Bruttovinstmarginal'].mean(skipna=True)) / df['Bruttovinstmarginal'].std(skipna=True)
        accruals_abs = -1 * df['Accruals']
        z_norm_accruals = (accruals_abs - accruals_abs.mean(skipna=True)) / accruals_abs.std(skipna=True)
        assetg_abs = -1 * df['Tillgångstillväxt']
        z_norm_assetg = (assetg_abs - assetg_abs.mean(skipna=True)) / assetg_abs.std(skipna=True)
        
        # beräkna enligt "Combined Quality Score Formula"
        df['Quality Score'] = round((z_norm_grossp + z_norm_accruals + z_norm_assetg) / 3, 4)

    except Exception as e:
        raise ValueError(f"Failed to compute quality score: {e}")

    return df

def create_cop_at_noa_composite_score(df):
    """
    Creates a composite score from COP_AT and NOA_GR1A columns.
    
    1. Selects cop_at, NOA_GR1A, and Sector columns
    2. Standardizes using z-scores within each sector  
    3. Creates composite score = z(COP_AT) - z(NOA_GR1A)
    
    Parameters:
    df (pandas.DataFrame): DataFrame containing 'cop_at', 'NOA_GR1A', and 'Sector' columns
    
    Returns:
    pandas.DataFrame: DataFrame with original columns plus composite score
    """
    print("Calculating composite score...")
    
    # Check if required columns exist
    required_columns = ['cop_at', 'NOA_GR1A', 'Sector']
    missing_columns = [col for col in required_columns if col not in df.columns]
    if missing_columns:
        print(f"Warning: Missing columns {missing_columns}. Skipping composite score calculation.")
        return df
    
    # Create a copy of the dataframe
    result_df = df.copy()
    
    # Initialize the composite score column
    result_df['z_NOA_COP_Composite'] = None
    
    try:
        # Process each sector separately
        for sector_name in df['Sector'].dropna().unique():
            print(f"Processing sector: {sector_name}")
            
            # Get rows for this sector with valid cop_at and NOA_GR1A values
            sector_mask = (
                (df['Sector'] == sector_name) & 
                df['cop_at'].notna() & 
                df['NOA_GR1A'].notna()
            )
            
            sector_count = sector_mask.sum()
            if sector_count < 2:
                print(f"  Skipping {sector_name}: only {sector_count} valid data points")
                continue
            
            # Get the data for this sector
            sector_data = df[sector_mask]
            
            # Calculate sector statistics
            cop_mean = sector_data['cop_at'].mean()
            cop_std = sector_data['cop_at'].std()
            noa_mean = sector_data['NOA_GR1A'].mean()
            noa_std = sector_data['NOA_GR1A'].std()
            
            print(f"  {sector_name}: {sector_count} companies, COP_AT std={cop_std:.4f}, NOA std={noa_std:.4f}")
            
            # Skip if no variation (all values the same)
            if cop_std == 0 or noa_std == 0:
                print(f"  Skipping {sector_name}: zero standard deviation")
                continue
            
            # Calculate z-scores and composite score for each company in this sector
            for idx in sector_data.index:
                cop_value = df.loc[idx, 'cop_at']
                noa_value = df.loc[idx, 'NOA_GR1A']
                
                # Calculate z-scores
                z_cop = (cop_value - cop_mean) / cop_std
                z_noa = (noa_value - noa_mean) / noa_std
                
                # Calculate composite score: z(COP_AT) - z(NOA_GR1A)
                composite = z_cop - z_noa
                
                # Round and store
                result_df.loc[idx, 'z_NOA_COP_Composite'] = round(float(composite), 4)
        
        print("Composite score calculation completed.")
        
    except Exception as e:
        print(f"Error in composite score calculation: {e}")
        return df
    
    return result_df

###################### Residual momentum ######################

def calculate_monthly_excess_returns(ticker, price_data, risk_free_rate=1.02):
    # Need at least 40 months: 2 months lag + 37 months for 36 returns  
    if not price_data or len(price_data) < 40: 
         return {
            ticker: None
        }
    
    try:
        # Convert string dates to datetime objects if needed
        for d in price_data:
            if isinstance(d['date'], str):
                d['date'] = datetime.strptime(d['date'], '%Y-%m-%d')
        
        # Sort by date to ensure chronological order
        price_data.sort(key=lambda x: x['date'])
        
        # Group by month and get last day of each month
        monthly_data = defaultdict(list)
        for entry in price_data:
            key = (entry['date'].year, entry['date'].month)
            monthly_data[key].append(entry)
        
        # Get the last trading day of each month (highest date in each month)
        monthly_prices = []
        for key in sorted(monthly_data.keys()):
            month_entries = monthly_data[key]
            last_day_entry = max(month_entries, key=lambda x: x['date'])
            monthly_prices.append({
                'date': last_day_entry['date'],
                'adjusted_close': last_day_entry['adjusted_close']
            })
        
        # Match Fama-French data period: Skip last 2 months, then take 37 months for 36 returns
        # This ensures price data aligns with Fama-French data (e.g., both end in July when run in September)
        if len(monthly_prices) < 39:  # Need at least 39 months (37 for calculation + 2 for lag)
            return {
                ticker: None
            }
            
        # Skip last 2 months to match Fama-French lag, then take 37 months
        # monthly_prices[:-2] removes last 2 months, [-37:] takes last 37 from remaining
        available_months = monthly_prices[:-2]  # Remove last 2 months
        
        if len(available_months) < 37:
            return {
                ticker: None
            }
            
        relevant_months = available_months[-37:]  # Take last 37 months from lag-adjusted data
        
        # Calculate monthly risk-free rate (convert annual to monthly)
        monthly_rf_rate = (risk_free_rate ** (1/12)) - 1
        
        # Calculate monthly returns and excess returns using relevant_months
        monthly_excess_returns = []
        for i in range(1, len(relevant_months)):
            current_price = relevant_months[i]['adjusted_close']
            previous_price = relevant_months[i-1]['adjusted_close']
            
            # Monthly return
            monthly_return = (current_price / previous_price) - 1
            
            # Excess return (monthly return - risk-free rate)
            excess_return = monthly_return - monthly_rf_rate
            
            monthly_excess_returns.append(excess_return)
        
        return {
            # monthly_excess_returns är nu synkroniserad med Fama-French data
            # Båda datasets slutar samma månad (t.ex. juli när körning sker i september)
            # monthly_excess_returns[0] = äldsta månaden (36 månader tillbaka från slutmånad)
            # monthly_excess_returns[-1] = senaste månaden (samma som sista Fama-French månad)
            f"Excess Returns": {ticker:monthly_excess_returns}
        }
        
    except Exception as e:
        print(f"Error calculating monthly excess returns: {e}")
        return {
            ticker: None
        }


def get_fama_factors(factor_country): 
    """
    Safely fetch Fama-French factors with error handling
    
    Returns:
    pandas.DataFrame or None: Fama-French factors for last 36 months, or None if failed
    """
    try:
        if factor_country == "Europe":
            ff = web.DataReader("Europe_3_Factors", "famafrench")[0]
        else: 
            ff = web.DataReader("F-F_Research_Data_Factors", "famafrench")[0]

        if ff is None or len(ff) == 0:
            print(f"Warning: No Fama-French data received for {factor_country}")
            return None
        
        # Fama-French data is already lagged (e.g., September data goes up to July)
        # So we just take the last 36 months available
        ff_last_36 = ff.tail(36)
        
        if len(ff_last_36) < 36:
            print(f"Warning: Only {len(ff_last_36)} months of Fama-French data available (need 36)")
            return None
            
        return ff_last_36
        
    except Exception as e:
        print(f"Error fetching Fama-French factors for {factor_country}: {e}")
        print("Residual momentum analysis will be skipped.")
        return None

def ticker_excess_returns(df, separate_data_list):        
    # Extract excess returns for each ticker
    ticker_excess_returns = {}
    
    for data_dict in separate_data_list:
        ticker = data_dict.get('Ticker')
        if not ticker:
            continue
        
        # Look for excess returns in the data dictionary
        # Since you return {"Excess Returns": {ticker: monthly_excess_returns}}
        excess_returns_dict = data_dict.get("Excess Returns")
        excess_returns = None
        if excess_returns_dict and isinstance(excess_returns_dict, dict):
            excess_returns = excess_returns_dict.get(ticker)
        
        # Store in dictionary: {ticker: excess_returns_list}
        ticker_excess_returns[ticker] = excess_returns
    
    return ticker_excess_returns


def residual_momentum(factor_country, df, separate_data_list):
    """
    Beräknar residual momentum (rMOM) för varje aktie.

    1. Hämtar Fama-French 3-faktor-data.
    2. Hämtar månatliga överavkastningar för varje ticker.
    3. Utför en linjär regression för varje ticker över en 36-månadersperiod för att få residualer.
    4. Standardiserar residualerna.
    5. Beräknar rMOM-poängen baserat på standardiserade residualer från månader t-6 till t-2.

    Args:
        df (pd.DataFrame): Huvud-DataFrame som inte används direkt i denna funktion, men kan
                           vara en del av en större pipeline.
        separate_data_list (list): En lista med dictionaries, där varje dictionary
                                   innehåller ticker och dess överavkastningar.

    Returns:
        pd.DataFrame: Ett DataFrame som innehåller varje tickers rMOM-poäng.
    """
    
    # Steg 1: Hämta Fama-French-faktorer
    fama_factors = get_fama_factors(factor_country)
    
    # SÄKERHETSKONTROLL: Om Fama-French data inte kan hämtas, returnera ursprunglig df
    if fama_factors is None:
        print("Warning: Residual momentum analysis skipped due to missing Fama-French data")
        return df
    
    try:
        fama_factors = fama_factors[['Mkt-RF', 'SMB', 'HML']]
    except KeyError as e:
        print(f"Error: Required Fama-French columns missing: {e}")
        return df
    
    # Steg 2: Hämta överavkastningar för varje ticker
    ticker_returns = ticker_excess_returns(df, separate_data_list)
    
    # SÄKERHETSKONTROLL: Om inga ticker returns finns, returnera ursprunglig df
    if not ticker_returns:
        print("Warning: No ticker excess returns found for residual momentum analysis")
        return df
    # Steg 3 & 4: Regression och standardisering av residualer
    all_rmom_scores = {}
    
    for ticker, returns_list in ticker_returns.items():
        if returns_list is None or len(returns_list) < 36:
            continue # Hoppa över om det inte finns tillräckligt med data
        
        try:
            # SÄKERHETSKONTROLL: Kontrollera att vi har exakt 36 månaders data
            if len(returns_list) != 36:
                print(f"Warning: {ticker} has {len(returns_list)} months of data, need exactly 36")
                continue
                
            # Säkerställ att vi har 36 månaders data och matcha index
            if len(fama_factors) != 36:
                print(f"Warning: Fama-French data has {len(fama_factors)} months, need exactly 36")
                continue
                
            returns_series = pd.Series(returns_list, index=fama_factors.index)
            
            # SÄKERHETSKONTROLL: Kontrollera för NaN eller inf värden
            if returns_series.isna().any() or np.isinf(returns_series).any():
                print(f"Warning: {ticker} has NaN or infinite values in returns data")
                continue
            
            if fama_factors.isna().any().any() or np.isinf(fama_factors).any().any():
                print(f"Warning: Fama-French data has NaN or infinite values")
                continue
            
            # Regressionen måste ha en konstant term
            X = sm.add_constant(fama_factors)
            y = returns_series

            # Utför OLS-regression
            model = sm.OLS(y, X).fit()
            residuals = model.resid
            
            # SÄKERHETSKONTROLL: Kontrollera residualer
            if residuals.isna().any() or np.isinf(residuals).any():
                print(f"Warning: {ticker} regression produced NaN or infinite residuals")
                continue
            
            if len(residuals) < 6:
                print(f"Warning: {ticker} has too few residuals ({len(residuals)}) for momentum calculation")
                continue
            
            # Standardisera residualerna
            scaler = StandardScaler()
            residuals_reshaped = residuals.values.reshape(-1, 1)
            standardized_residuals = scaler.fit_transform(residuals_reshaped)
            
            # Steg 5: Beräkna rMOM-poäng
            # Använd residualer från t-6 till t-2 för att undvika reversering 
            rmom_window = standardized_residuals[-6:-1].flatten()
            
            # SÄKERHETSKONTROLL: Kontrollera att vi har tillräckligt med data för momentum
            if len(rmom_window) < 5:
                print(f"Warning: {ticker} has insufficient data for momentum window")
                continue
                
            rmom_score = np.mean(rmom_window)
            
            # SÄKERHETSKONTROLL: Kontrollera att resultatet är giltigt
            if np.isnan(rmom_score) or np.isinf(rmom_score):
                print(f"Warning: {ticker} produced invalid rMOM score")
                continue
            
            all_rmom_scores[ticker] = round(rmom_score, 4)
            
        except Exception as e:
            print(f"Error in residual momentum calculation for {ticker}: {e}")
            continue

    # SÄKERHETSKONTROLL: Om inga rMOM scores beräknades, returnera ursprunglig df
    if not all_rmom_scores:
        print("Warning: No residual momentum scores could be calculated")
        # Lägg till tom rMOM kolumn för konsistens
        df_copy = df.copy()
        df_copy['rMOM'] = None
        return df_copy
    
    try:
        # Returnera en DataFrame med rMOM-poängen för varje ticker
        rmom_df = pd.DataFrame.from_dict(all_rmom_scores, orient='index', columns=['rMOM'])
        rmom_df.index.name = 'Ticker'
        
        # SÄKERHETSKONTROLL: Kontrollera att ursprunglig df har Ticker kolumn
        if 'Ticker' not in df.columns:
            print("Error: Original DataFrame missing 'Ticker' column for residual momentum merge")
            return df
        
        # Slå samman rMOM-poängen med det ursprungliga DataFrame
        merged_df = pd.merge(df, rmom_df, left_on='Ticker', right_on='Ticker', how='left')
        
        print(f"Successfully calculated residual momentum for {len(all_rmom_scores)} tickers")
        return merged_df
        
    except Exception as e:
        print(f"Error merging residual momentum results: {e}")
        return df