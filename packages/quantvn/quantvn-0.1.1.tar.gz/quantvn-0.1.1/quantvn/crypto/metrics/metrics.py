import numpy as np


class Metrics:
    def __init__(self, backtest):
        self.backtest = backtest
        self.daily_pnl = backtest.daily_PNL().diff().dropna()

    def avg_loss(self):
        losses = self.daily_pnl[self.daily_pnl < 0]
        return losses.mean()

    def avg_return(self):
        return self.daily_pnl.mean()

    def avg_win(self):
        wins = self.daily_pnl[self.daily_pnl > 0]
        return wins.mean()

    def max_drawdown(self):
        cumulative = self.daily_pnl.cumsum()
        peak = cumulative.cummax()
        drawdown = cumulative - peak
        return drawdown.min() / self.backtest.estimate_minimum_capital()

    def win_rate(self):
        wins = (self.daily_pnl > 0).sum()
        total = len(self.daily_pnl)
        return wins / total if total > 0 else 0

    def volatility(self):
        return self.daily_pnl.std()

    def sharpe(self, risk_free_rate=0.0):
        return (self.avg_return() - risk_free_rate) / self.volatility() * np.sqrt(365)

    def sortino(self):
        downside_std = self.daily_pnl[self.daily_pnl < 0].std()
        return (
            np.sqrt(252) * self.avg_return() / downside_std
            if downside_std > 0
            else np.nan
        )

    def calmar(self):
        return (
            np.sqrt(252) * self.avg_return() / abs(self.max_drawdown())
            if self.max_drawdown() != 0
            else np.nan
        )

    def profit_factor(self):
        total_gain = self.daily_pnl[self.daily_pnl > 0].sum()
        total_loss = abs(self.daily_pnl[self.daily_pnl < 0].sum())
        return total_gain / total_loss if total_loss != 0 else np.nan

    def risk_of_ruin(self):
        win_rate = self.win_rate()
        loss_rate = 1 - win_rate
        return (
            (loss_rate / win_rate) ** (1 / self.avg_loss())
            if self.avg_loss() != 0
            else np.nan
        )

    def value_at_risk(self, confidence_level=0.05):
        return self.daily_pnl.quantile(confidence_level)
