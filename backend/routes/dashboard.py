from fastapi import APIRouter, Depends, Request, Form
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from sqlalchemy import func
from backend.config.database import get_db
import backend.models.index as models
from backend.services.auth import get_current_user
from datetime import date, timedelta, datetime
import calendar
import io
import base64
import matplotlib
matplotlib.use("Agg")  # Non-interactive backend (no display needed)
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])

# ── Matplotlib helper: dark-themed chart → base64 PNG string ─────────────

_BG  = "#1a1a2e"   # card / figure background
_AX  = "#16213e"   # axes background
_FG  = "#e0e0e0"   # text / spine colour
_GRID = "rgba(255,255,255,0.08)"  # not used directly; see below


def _fig_to_b64(fig) -> str:
    """Render a matplotlib figure to a base64-encoded PNG string."""
    buf = io.BytesIO()
    fig.savefig(buf, format="png", bbox_inches="tight", dpi=110)
    buf.seek(0)
    encoded = base64.b64encode(buf.read()).decode("utf-8")
    plt.close(fig)
    return encoded


def _apply_dark_style(fig, ax, title: str):
    """Apply the app's dark theme to a figure/axes pair."""
    fig.patch.set_facecolor(_BG)
    ax.set_facecolor(_AX)
    ax.set_title(title, color=_FG, fontsize=13, fontweight="bold", pad=12)
    ax.tick_params(colors=_FG, labelsize=9)
    for spine in ax.spines.values():
        spine.set_edgecolor("#333355")
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda v, _: f"₹{v:,.0f}"))
    ax.grid(axis="y", color="#333355", linewidth=0.7, linestyle="--")


def _make_line_chart(labels: list, amounts: list, title: str, color: str = "#00e676") -> str:
    """Return a base64 PNG of a dark-themed line chart for monthly income."""
    fig, ax = plt.subplots(figsize=(8, 3.2))
    _apply_dark_style(fig, ax, title)

    if amounts:
        x = range(len(labels))
        ax.plot(x, amounts, color=color, linewidth=2.2, marker="o",
                markersize=5, markerfacecolor=color, zorder=3)
        ax.fill_between(x, amounts, alpha=0.18, color=color)
        ax.set_xticks(list(x))
        ax.set_xticklabels(labels, color=_FG, fontsize=8, rotation=45, ha="right")
    else:
        ax.text(0.5, 0.5, "No income data for this period",
                ha="center", va="center", color="#888", transform=ax.transAxes, fontsize=11)
        ax.set_xticks([])

    ax.set_yticks(ax.get_yticks())
    ax.set_yticklabels([f"₹{int(v):,}" for v in ax.get_yticks()], color=_FG, fontsize=8)
    fig.tight_layout()
    return _fig_to_b64(fig)


def _make_bar_chart(labels: list, amounts: list, title: str, color: str = "#00e676") -> str:
    """Return a base64 PNG of a dark-themed bar chart for yearly income."""
    fig, ax = plt.subplots(figsize=(8, 3.2))
    _apply_dark_style(fig, ax, title)

    bars = ax.bar(labels, amounts, color=color, alpha=0.85, width=0.6,
                  edgecolor="#111", linewidth=0.5)
    # Highlight non-zero bars with a subtle gradient edge
    for bar, val in zip(bars, amounts):
        if val > 0:
            bar.set_edgecolor(color)
            bar.set_linewidth(1.2)

    ax.set_xticks(range(len(labels)))
    ax.set_xticklabels(labels, color=_FG, fontsize=9)
    ax.set_yticks(ax.get_yticks())
    ax.set_yticklabels([f"₹{int(v):,}" for v in ax.get_yticks()], color=_FG, fontsize=8)
    fig.tight_layout()
    return _fig_to_b64(fig)


def get_dashboard_data(db: Session, current_user: models.User, month: int = None, year: int = None):
    today = date.today()
    if not year:
        year = today.year
    if not month:
        month = today.month
        
    start_date = date(year, month, 1)
    last_day = calendar.monthrange(year, month)[1]
    end_date = date(year, month, last_day)
    
    total_expense = db.query(func.sum(models.Expense.amount)).filter(
        models.Expense.user_id == current_user.id,
        func.extract('year', models.Expense.date) == year
    ).scalar() or 0.0
    this_month_expense = db.query(func.sum(models.Expense.amount)).filter(
        models.Expense.user_id == current_user.id,
        models.Expense.date >= start_date,
        models.Expense.date <= end_date
    ).scalar() or 0.0

    total_income_sum = db.query(func.sum(models.Income.amount)).filter(models.Income.user_id == current_user.id).scalar() or 0.0
    total_balance = total_income_sum - total_expense

    # Daily (Selected Month)
    daily_expenses_query = db.query(
        models.Expense.date,
        func.sum(models.Expense.amount).label("total")
    ).filter(
        models.Expense.user_id == current_user.id,
        models.Expense.date >= start_date,
        models.Expense.date <= end_date
    ).group_by(models.Expense.date).order_by(models.Expense.date).all()
    
    daily_labels = []
    daily_amounts = []
    for e in daily_expenses_query:
        # Handle SQLite returning string for dates
        dt = e.date
        if isinstance(dt, str):
            dt = datetime.strptime(dt, "%Y-%m-%d").date()
        
        label = f"{dt.day} {dt.strftime('%b')}"
        daily_labels.append(label)
        daily_amounts.append(float(e.total))
        
    daily_chart_config = {
        "type": "line",
        "data": {
            "labels": daily_labels,
            "datasets": [{
                "label": 'Expense Amount (₹)',
                "data": daily_amounts,
                "borderColor": '#00d2ff',
                "backgroundColor": 'rgba(0, 210, 255, 0.2)',
                "borderWidth": 2,
                "tension": 0.4,
                "fill": True
            }]
        },
        "options": {
            "responsive": True,
            "maintainAspectRatio": False,
            "plugins": {
                "legend": { "display": False }
            }
        }
    }

    # Monthly (Global Bar Graph)
    monthly_expenses_query = db.query(
        func.extract('month', models.Expense.date).label("month"),
        func.sum(models.Expense.amount).label("total")
    ).filter(
        models.Expense.user_id == current_user.id,
        func.extract('year', models.Expense.date) == year
    ).group_by("month").order_by("month").all()
    
    month_names = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
    monthly_amounts = [0.0] * 12
    for e in monthly_expenses_query:
        idx = int(e.month) - 1
        monthly_amounts[idx] = float(e.total)
        
    yearly_chart_config = {
        "type": 'bar',
        "data": {
            "labels": month_names,
            "datasets": [{
                "label": 'Total Expense (₹)',
                "data": monthly_amounts,
                "backgroundColor": '#3a7bd5',
                "borderRadius": 4
            }]
        },
        "options": {
            "responsive": True,
            "maintainAspectRatio": False,
            "plugins": {
                "legend": { "display": False }
            }
        }
    }

    # Categories Breakdown
    cat_distribution = db.query(
        models.Category.name,
        func.sum(models.Expense.amount).label("total")
    ).join(models.Expense, models.Category.id == models.Expense.category_id).filter(
        models.Expense.user_id == current_user.id,
        models.Expense.date >= start_date,
        models.Expense.date <= end_date
    ).group_by(models.Category.name).all()

    cat_labels = []
    cat_amounts = []
    for c in cat_distribution:
        cat_labels.append(c.name)
        cat_amounts.append(float(c.total))
        
    background_colors = [
        '#FF6384', '#36A2EB', '#FFCE56', '#4BC0C0', '#9966FF', 
        '#FF9F40', '#00d2ff', '#3a7bd5', '#8A2BE2', '#00FA9A'
    ]
    
    cat_chart_config = {
        "type": 'bar',
        "data": {
            "labels": cat_labels,
            "datasets": [{
                "label": 'Total Expense (₹)',
                "data": cat_amounts,
                "backgroundColor": background_colors[:len(cat_labels)] if cat_labels else [],
                "borderRadius": 4
            }]
        },
        "options": {
            "responsive": True,
            "maintainAspectRatio": False,
            "plugins": {
                "legend": { "display": False }
            }
        }
    }

    # Recent Expenses
    recent_expenses = db.query(models.Expense).filter(
        models.Expense.user_id == current_user.id
    ).order_by(models.Expense.date.desc()).limit(10).all()

    # All Categories (for form)
    categories = db.query(models.Category).filter(
        (models.Category.created_by_id == current_user.id) | 
        (models.Category.created_by_id.is_(None))
    ).all()

    # ── Income: Monthly (daily breakdown for selected month) ──────────────
    monthly_income_query = db.query(
        models.Income.date,
        func.sum(models.Income.amount).label("total")
    ).filter(
        models.Income.user_id == current_user.id,
        models.Income.date >= start_date,
        models.Income.date <= end_date
    ).group_by(models.Income.date).order_by(models.Income.date).all()

    inc_daily_labels = []
    inc_daily_amounts = []
    for row in monthly_income_query:
        dt = row.date
        if isinstance(dt, str):
            dt = datetime.strptime(dt, "%Y-%m-%d").date()
        inc_daily_labels.append(f"{dt.day} {dt.strftime('%b')}")
        inc_daily_amounts.append(float(row.total))

    month_full_name = date(year, month, 1).strftime("%B")
    monthly_income_chart = _make_line_chart(
        inc_daily_labels, inc_daily_amounts,
        title=f"Monthly Incomes ({month_full_name} {year})",
        color="#00e676"
    )

    # ── Income: Yearly (monthly totals for selected year) ─────────────────
    yearly_income_query = db.query(
        func.extract('month', models.Income.date).label("month"),
        func.sum(models.Income.amount).label("total")
    ).filter(
        models.Income.user_id == current_user.id,
        func.extract('year', models.Income.date) == year
    ).group_by("month").order_by("month").all()

    month_names_short = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
                         'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
    inc_yearly_amounts = [0.0] * 12
    for row in yearly_income_query:
        inc_yearly_amounts[int(row.month) - 1] = float(row.total)

    yearly_income_chart = _make_bar_chart(
        month_names_short, inc_yearly_amounts,
        title=f"Yearly Incomes ({year})",
        color="#00e676"
    )

    return {
        "total_expense": total_expense,
        "this_month_expense": this_month_expense,
        "total_balance": total_balance,
        "total_income": total_income_sum,
        "daily_chart_config": daily_chart_config,
        "yearly_chart_config": yearly_chart_config,
        "cat_chart_config": cat_chart_config,
        "monthly_income_chart": monthly_income_chart,
        "yearly_income_chart": yearly_income_chart,
        "user": current_user,
        "selected_month": month,
        "selected_year": year,
        "month_full_name": month_full_name
    }



@router.get("/summary")
def get_dashboard_summary(db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    today = date.today()
    current_month_start = today.replace(day=1)
    
    # Total Expenses (All time)
    total_expense = db.query(func.sum(models.Expense.amount)).filter(models.Expense.user_id == current_user.id).scalar() or 0.0
    
    # This month expense
    this_month_expense = db.query(func.sum(models.Expense.amount)).filter(
        models.Expense.user_id == current_user.id,
        models.Expense.date >= current_month_start
    ).scalar() or 0.0

    return {
        "total_expense": total_expense,
        "this_month_expense": this_month_expense,
        "savings": 0 # Future implement total income vs expense
    }

@router.get("/daily")
def get_daily_expenses(month: int = None, year: int = None, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    if not month or not year:
        today = date.today()
        month = today.month
        year = today.year
        
    start_date = date(year, month, 1)
    # get last day of month
    last_day = calendar.monthrange(year, month)[1]
    end_date = date(year, month, last_day)

    expenses = db.query(
        models.Expense.date,
        func.sum(models.Expense.amount).label("total")
    ).filter(
        models.Expense.user_id == current_user.id,
        models.Expense.date >= start_date,
        models.Expense.date <= end_date
    ).group_by(models.Expense.date).order_by(models.Expense.date).all()

    return [{"date": str(e.date), "amount": e.total} for e in expenses]

@router.get("/monthly")
def get_monthly_summary(year: int = None, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    if not year:
        year = date.today().year

    # Basic SQLite extraction for month, depends on dialect for true SQL cross-compatibility
    # For simplicity and standard SQL, we process in memory or use cast. 
    # SQLAlchemy func.extract('month', date) works across major dialects.
    
    expenses_query = db.query(
        func.extract('month', models.Expense.date).label("month"),
        func.sum(models.Expense.amount).label("total")
    ).filter(
        models.Expense.user_id == current_user.id,
        func.extract('year', models.Expense.date) == year
    ).group_by("month").order_by("month").all()

    return [{"month": e.month, "amount": e.total} for e in expenses_query]

@router.get("/category-distribution")
def get_category_distribution(month: int = None, year: int = None, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    query = db.query(
        models.Category.name,
        func.sum(models.Expense.amount).label("total")
    ).join(models.Expense, models.Category.id == models.Expense.category_id).filter(
        models.Expense.user_id == current_user.id
    )

    if month and year:
        start_date = date(year, month, 1)
        last_day = calendar.monthrange(year, month)[1]
        end_date = date(year, month, last_day)
        query = query.filter(models.Expense.date >= start_date, models.Expense.date <= end_date)

    distribution = query.group_by(models.Category.name).all()

    return [{"category": d.name, "amount": d.total} for d in distribution]
