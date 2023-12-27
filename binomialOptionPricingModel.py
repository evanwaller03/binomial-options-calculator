'''
Download the following libraries to use this:

    pip3 install QuantLib-Python
    pip3 install matplotlib 
    
Enjoy!
'''

import QuantLib as ql
import datetime
import matplotlib.pyplot as plt

def ql_to_datetime(d):
    return datetime.date(d.year(), d.month(), d.dayOfMonth())

def calculate_option_prices(start_date, strike_price, underlying_price, volatility, annual_growth_rate, raw_dividend_yield, raw_risk_free_rate, maturity_date):
    # Convert start_date and end_date from datetime.date to QuantLib.Date
    start_date = ql.Date(start_date.day, start_date.month, start_date.year)
    
    # Calculate daily rate from annual growth rate
    daily_rate = (1 + annual_growth_rate)**(1/365) - 1
    
    # Construct QuantLib structures
    calendar = ql.UnitedStates(ql.UnitedStates.NYSE)
    day_count = ql.ActualActual(ql.ActualActual.ISDA)
    underlying = ql.SimpleQuote(underlying_price)
    volatility_q = ql.BlackVolTermStructureHandle(ql.BlackConstantVol(start_date, calendar, volatility, day_count))
    dividend_yield = ql.YieldTermStructureHandle(ql.FlatForward(start_date, raw_dividend_yield, day_count))
    risk_free_rate = ql.YieldTermStructureHandle(ql.FlatForward(start_date, raw_risk_free_rate, day_count))
    
    # Define the American option
    call_payoff = ql.PlainVanillaPayoff(ql.Option.Call, strike_price)
    put_payoff = ql.PlainVanillaPayoff(ql.Option.Put, strike_price)
    exercise = ql.AmericanExercise(start_date, maturity_date)
    american_call_option = ql.VanillaOption(call_payoff, exercise)
    american_put_option = ql.VanillaOption(put_payoff, exercise)
    
    steps = 100 # Number of steps for the binomial tree
    
    # Store prices for each day
    call_prices = []
    put_prices = []
    dates = []
    current_date = start_date
    
    # Calculate option prices for each day from start_date to end_date
    while current_date <= maturity_date:
        underlying_q = ql.QuoteHandle(ql.SimpleQuote(underlying_price))
        stochastic_process = ql.GeneralizedBlackScholesProcess(underlying_q, dividend_yield, risk_free_rate, volatility_q)

        # Set up the pricing engine
        ql.Settings.instance().evaluationDate = current_date
        engine = ql.BinomialVanillaEngine(stochastic_process, "crr", steps)
        american_call_option.setPricingEngine(engine)
        american_put_option.setPricingEngine(engine)

        # Append date and calculated values to the array of prices
        dates.append(ql_to_datetime(current_date))
        call_prices.append(american_call_option.NPV())
        put_prices.append(american_put_option.NPV())

        # Update values for next iteration
        current_date = current_date + ql.Period(1, ql.Days)
        underlying_price = (underlying_price * (1 + daily_rate))  # Update underlying price
    
    # Return the calculated prices
    return call_prices, put_prices, dates

# Example usage:
start_date = datetime.date(year=2023, month=12, day=27)
maturity_date = ql.Date(15, 3, 2024)
call_prices, put_prices, dates = calculate_option_prices(start_date, strike_price=5.0, underlying_price=3.56, volatility=1.04025, annual_growth_rate=4.0, raw_dividend_yield=0.00, raw_risk_free_rate=0.039, maturity_date=maturity_date)

print(f"American Call Option Prices: {call_prices}")
print(f"American Put Option Prices: {put_prices}")
print(f"Peak Call Price: {max(call_prices):.2f}")
print(f"Peak Put Price: {max(put_prices):.2f}")

plt.figure(figsize=(10, 6))
plt.plot(dates, call_prices, label='American Call Option Price')
plt.plot(dates, put_prices, label='American Put Option Price')
plt.xlabel('Date')
plt.ylabel('Option Price')
plt.title('Option Price Evolution Over Time')
plt.legend()
plt.show()