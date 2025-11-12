import numpy as np, pandas as pd

def business_dataset(T=720, seed=42):
    np.random.seed(seed)
    dates = pd.date_range("2023-01-01", periods=T, freq="D")

    marketing_spend = 1000 + 200*np.sin(np.linspace(0, 4*np.pi, T)) + 100*np.random.randn(T)
    marketing_spend = np.clip(marketing_spend, 300, 2000)

    price = 10 + 0.5*np.sin(np.linspace(0, 2*np.pi, T)/10) + 0.2*np.random.randn(T)
    price = np.clip(price, 8, 12)

    # state variables
    new_users = np.zeros(T)
    churned_users = np.zeros(T)
    active_users = np.zeros(T)
    paying_users = np.zeros(T)
    support_tickets = np.zeros(T)
    revenue = np.zeros(T)

    # initialize
    active_users[0] = 3000
    new_users[0] = 500
    paying_users[0] = 400
    support_tickets[0] = 200
    churned_users[0] = 100
    revenue[0] = paying_users[0]*price[0]

    for t in range(1, T):
        # marketing → new users
        new_users[t] = 0.5*marketing_spend[t]/10 + 0.95*new_users[t-1] + np.random.randn()*20

        # churn dynamics: depends on support load and active size
        churn_rate = 0.1 + 0.00001*support_tickets[t-1] + np.random.randn()*0.002
        churn_rate = np.clip(churn_rate, 0.01, 0.15)
        churned_users[t] = churn_rate * active_users[t-1]

        # support tickets depend on active users & lagged tickets
        active_users[t] = active_users[t-1] + new_users[t] - churned_users[t]
        support_tickets[t] = 0.05*active_users[t] + 0.6*support_tickets[t-1] + np.random.randn()*30

        # paying users depend on price & active users
        conversion_rate = 0.08 - 0.01*(price[t]-10)
        paying_users[t] = 0.7*paying_users[t-1] + conversion_rate*active_users[t] + np.random.randn()*10
        paying_users[t] = max(0, paying_users[t])

        # revenue = paying_users × price
        revenue[t] = paying_users[t]*price[t]

    df = pd.DataFrame({
        "marketing_spend": marketing_spend,
        "price": price,
        "new_users": new_users,
        "churned_users": churned_users,
        "active_users": active_users,
        "support_tickets": support_tickets,
        "paying_users": paying_users,
        "revenue": revenue
    }, index=dates)

    return df
