import QuantLib as ql
import datetime
import matplotlib.pyplot as plt

def ql_to_datetime(d):
    return datetime.date(d.year(), d.month(), d.dayOfMonth())

def calculate_implied_volatility(market_price, underlying_price, strike_price, risk_free_rate, maturity_date, option_type='call'):
    # Ensure maturity_date is a QuantLib Date
    ql_maturity_date = ql.Date(maturity_date.day, maturity_date.month, maturity_date.year)

    if option_type == 'call':
        payoff = ql.PlainVanillaPayoff(ql.Option.Call, strike_price)
    else:
        payoff = ql.PlainVanillaPayoff(ql.Option.Put, strike_price)
    exercise = ql.AmericanExercise(ql.Date.todaysDate(), ql_maturity_date)
    option = ql.VanillaOption(payoff, exercise)

    u = ql.SimpleQuote(underlying_price)
    # Corrected instantiation of ActualActual
    day_counter = ql.ActualActual(ql.ActualActual.ISDA)
    dividend_yield = ql.FlatForward(ql.Date.todaysDate(), 0.0, day_counter)
    calendar = ql.UnitedStates(ql.UnitedStates.NYSE)
    volatility_q = ql.BlackConstantVol(ql.Date.todaysDate(), calendar, 0.20, day_counter)
    risk_free_rate = ql.YieldTermStructureHandle(ql.FlatForward(ql.Date.todaysDate(), risk_free_rate, day_counter))

    stoch_process = ql.BlackScholesMertonProcess(ql.QuoteHandle(u), ql.YieldTermStructureHandle(dividend_yield), risk_free_rate, ql.BlackVolTermStructureHandle(volatility_q))

    iv = option.impliedVolatility(market_price, stoch_process)
    return iv

def calculate_option_prices(start_date, strike_price, underlying_price, volatility, annual_growth_rate, raw_dividend_yield, raw_risk_free_rate, maturity_date, market_price=None, option_type='call'):
    # Convert dates to QuantLib dates
    ql_start_date = ql.Date(start_date.day, start_date.month, start_date.year)
    ql_maturity_date = ql.Date(maturity_date.day, maturity_date.month, maturity_date.year)
    
    daily_rate = (1 + annual_growth_rate)**(1/365) - 1

    calendar = ql.UnitedStates(ql.UnitedStates.NYSE)
    day_count = ql.ActualActual(ql.ActualActual.ISDA)

    # Corrected BlackVolTermStructureHandle usage
    volatility_q = ql.BlackVolTermStructureHandle(ql.BlackConstantVol(ql_start_date, calendar, volatility, day_count))
    dividend_yield = ql.YieldTermStructureHandle(ql.FlatForward(ql_start_date, raw_dividend_yield, day_count))
    risk_free_rate = ql.YieldTermStructureHandle(ql.FlatForward(ql_start_date, raw_risk_free_rate, day_count))

    call_payoff = ql.PlainVanillaPayoff(ql.Option.Call, strike_price)
    put_payoff = ql.PlainVanillaPayoff(ql.Option.Put, strike_price)
    exercise = ql.AmericanExercise(ql_start_date, ql_maturity_date)
    american_call_option = ql.VanillaOption(call_payoff, exercise)
    american_put_option = ql.VanillaOption(put_payoff, exercise)
    
    steps = 100
    
    call_prices = []
    put_prices = []
    dates = []
    current_date = ql_start_date
    
    while current_date <= ql_maturity_date:
        # ...
        if market_price:
            implied_vol = calculate_implied_volatility(market_price, underlying_price, strike_price, raw_risk_free_rate, maturity_date, option_type)
            # Update the volatility handle with the new implied volatility
            volatility_q = ql.BlackVolTermStructureHandle(ql.BlackConstantVol(current_date, calendar, implied_vol, day_count))
        
        underlying_q = ql.QuoteHandle(ql.SimpleQuote(underlying_price))
        stochastic_process = ql.GeneralizedBlackScholesProcess(underlying_q, dividend_yield, risk_free_rate, volatility_q)

        ql.Settings.instance().evaluationDate = current_date
        engine = ql.BinomialVanillaEngine(stochastic_process, "crr", steps)
        american_call_option.setPricingEngine(engine)
        american_put_option.setPricingEngine(engine)

        dates.append(ql_to_datetime(current_date))
        call_prices.append(american_call_option.NPV())
        put_prices.append(american_put_option.NPV())

        current_date = current_date + ql.Period(1, ql.Days)
        underlying_price *= (1 + daily_rate)
    
    return call_prices, put_prices, dates

# Example usage
start_date = datetime.date(year=2023, month=12, day=27)
maturity_date = datetime.date(year=2024, month=1, day=19)
market_price_of_call = 1.14  # Example market price for call
market_price_of_put = 0.1   # Example market price for put

call_prices, put_prices, dates = calculate_option_prices(start_date, strike_price=2.5, underlying_price=3.44, volatility=1.14403, annual_growth_rate=1.0, raw_dividend_yield=0.00, raw_risk_free_rate=0.039, maturity_date=maturity_date, market_price=market_price_of_call, option_type='call')

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
