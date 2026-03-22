"""Generate charts as PNG BytesIO for Telegram."""
import io
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime


# Art Deco style
COLORS = {
    'bg': '#0A0A0F',
    'card': '#1A1A24',
    'gold': '#C9A84C',
    'gold_light': '#E8D48B',
    'teal': '#3DE8C7',
    'sapphire': '#5DADE2',
    'cream': '#FAF3E0',
    'cream_dim': '#D4C9A8',
    'ruby': '#FF4136',
}


def _setup_ax(ax, title: str):
    ax.set_facecolor(COLORS['card'])
    ax.set_title(title, color=COLORS['gold'], fontsize=14, fontweight='bold', pad=12)
    ax.tick_params(colors=COLORS['cream_dim'], labelsize=9)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['bottom'].set_color(COLORS['gold'] + '40')
    ax.spines['left'].set_color(COLORS['gold'] + '40')
    ax.grid(True, alpha=0.1, color=COLORS['gold'])


def generate_food_level_chart(telemetry: list) -> io.BytesIO:
    """Food level over time line chart."""
    fig, ax = plt.subplots(figsize=(8, 4))
    fig.patch.set_facecolor(COLORS['bg'])
    _setup_ax(ax, 'Уровень корма')

    if telemetry:
        times = [datetime.fromisoformat(t.get('timestamp', t.get('createdAt', '')).replace('Z', '+00:00')) for t in telemetry]
        foods = [t.get('foodLevel', t.get('food_level', 0)) for t in telemetry]
        waters = [t.get('waterLevel', t.get('water_level', 0)) for t in telemetry]

        ax.plot(times, foods, color=COLORS['gold'], linewidth=2, label='Корм %')
        ax.plot(times, waters, color=COLORS['sapphire'], linewidth=1.5, alpha=0.7, label='Вода %')
        ax.axhline(y=20, color=COLORS['ruby'], linestyle='--', alpha=0.5, label='Порог')
        ax.fill_between(times, 0, 20, alpha=0.05, color=COLORS['ruby'])
        ax.legend(facecolor=COLORS['card'], edgecolor=COLORS['gold'] + '40', labelcolor=COLORS['cream_dim'], fontsize=9)
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))

    ax.set_ylim(0, 105)
    ax.set_ylabel('%', color=COLORS['cream_dim'], fontsize=10)

    buf = io.BytesIO()
    fig.tight_layout()
    fig.savefig(buf, format='png', dpi=150, facecolor=fig.get_facecolor())
    plt.close(fig)
    buf.seek(0)
    return buf


def generate_feedings_chart(stats: dict) -> io.BytesIO:
    """Daily feedings bar chart."""
    fig, ax = plt.subplots(figsize=(8, 4))
    fig.patch.set_facecolor(COLORS['bg'])
    _setup_ax(ax, 'Статистика кормлений')

    total = stats.get('totalFeedings', stats.get('total_feedings', 0))
    consumed = stats.get('foodConsumed', stats.get('food_consumed', 0))
    avg_food = stats.get('avgFoodLevel', stats.get('avg_food_level', 0))

    labels = ['Кормлений', 'Корма (г)', 'Ср. уровень %']
    values = [total, consumed, avg_food]
    colors = [COLORS['gold'], COLORS['teal'], COLORS['sapphire']]

    bars = ax.bar(labels, values, color=colors, width=0.5, edgecolor=COLORS['gold'] + '30')
    for bar, v in zip(bars, values):
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 1,
                f'{v:.0f}', ha='center', va='bottom', color=COLORS['cream'], fontsize=11)

    buf = io.BytesIO()
    fig.tight_layout()
    fig.savefig(buf, format='png', dpi=150, facecolor=fig.get_facecolor())
    plt.close(fig)
    buf.seek(0)
    return buf
