import pandas as pd

def test_revenue_definition():
    df = pd.DataFrame({"Quantity":[2,3], "UnitPrice":[5.0,10.0]})
    assert (df["Quantity"]*df["UnitPrice"]).sum() == 40.0

def test_monthly_growth():
    s = pd.Series([100.0, 120.0])
    growth = (s.iloc[1]/s.iloc[0]-1)*100
    assert growth == 20.0
