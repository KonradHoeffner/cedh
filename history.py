# prototype with much code from ChatCPT, improvements are welcome
import os
import json
import pygit2
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator
from matplotlib.dates import DateFormatter
#import plotly.express as px
from datetime import datetime, timedelta
from numpy import nan
from matplotlib.colors import Normalize, ListedColormap
import matplotlib

BRANCH_NAME = 'gh-pages'
FILENAME = 'data/cards.json'
COLORS = {'W': 'White', 'U': 'Blue', 'B': 'Black', 'R': 'Red', 'G': 'Green'}
repo_path = os.getcwd()
#dates = []
data = {}

def collect_json_with_dates(repo):
    branch = repo.branches[BRANCH_NAME]
    cardss = []
    for commit in repo.walk(branch.target, pygit2.GIT_SORT_TOPOLOGICAL | pygit2.GIT_SORT_REVERSE):
        commit_date = datetime.utcfromtimestamp(commit.commit_time)#.strftime('%Y%m%d')
        if FILENAME in commit.tree:
            data_blob = repo.get(commit.tree[FILENAME].id)
            data_content = json.loads(data_blob.data.decode('utf-8'))
            #dates.append(commit_date)
            cardss.append((commit_date, data_content))
            #break # faster testing first only
    return cardss

def plot(color):
    for (date,cards) in cardss:
        data[date] = {cardname: value['identity_rank'] for cardname, value in cards.items() if value['color_identity'] == [color]}
    
    #print(data)
    #dates = list(data.keys())
    #card_ranks = {card: [data[date].get(card, 999) for date in dates] for card in data[dates[0]].keys()}

    df = pd.DataFrame.from_dict(data, orient='index')
    df = df.reindex(columns=sorted(df.columns), fill_value=nan) # prevent crash on new cards
    df = df[df.iloc[-1].sort_values().index] # colormap assignment by final rank

    # Filter and keep only the cards whose rank is below 21 at least once
    filtered_cards = df.columns[df.lt(21).any()]
    df = df[filtered_cards]

    # legend_handles = []  # Store legend handles for customization
    # legend_labels = []  # Store legend labels for customization

    # Create the bump chart
    fig, ax = plt.subplots(figsize=(15, 10))
    # Create a colormap with unique colors for each card.
    # Otherwise, colors may repeat.
    # It's a bit awkward because all cards are the same color so that would be the most intuitive color but then all would have the same.
    # we can still have some repetition because the largest matplotlib colormap has 20 colors and there can be more than 20 cards
    # in case one falls out of the top 20, but the effect should be minimal as we cycle around so same colors shouldn't touch realistically
    colormap = ListedColormap(plt.cm.tab20.colors, name='tab20_cyclic')

    #normalize = Normalize(vmin=0, vmax=len(df.columns) - 1)

    for i, card in enumerate(df.columns):
        #ax.plot(df.index, df[card], marker='o', label=card, color=colormap(normalize(i)))
        ax.plot(df.index, df[card], marker='o', label=card, color=colormap((i)))
         #line,  = ax.plot(df.index, df[card], marker='o', label=card)
         # legend_handles.append(line)  # Store the line handle
         # legend_labels.append(card)
        #ax.text(df.index[-1], df[card].iloc[-1], card, va='center', ha='left', fontsize=9, color='blue')
 #   for card, ranks in card_ranks.items():
 #       ax.plot(dates, ranks, marker='o', label=card)

    # Customize the plot
    ax.set_title(f'Most played {COLORS[color]} cards over time')
    ax.set_xlabel('Date')
    margin = timedelta(days=10)
    ax.set_xlim(df.index[0]-margin, df.index[-1]+margin)
    ax.xaxis.set_major_locator(MaxNLocator(integer=True))
    date_format = DateFormatter("%b %Y")
    ax.xaxis.set_major_formatter(date_format)

    #ax.set_ylabel('Rank')
    ax.set_ylim(0, 20.5)
    ax.set_yticks(range(1, 21))
    ax.invert_yaxis()
    #ax.legend(loc='lower left')
    ax.grid()

    legend_labels = list(df.columns)
    legend_labels.sort(key=lambda card: df[card].iloc[-1])
    for card in legend_labels:
        firstrank = df[card].iloc[0]
        rank = df[card].iloc[-1]
        #ax.annotate(f"{card} ({rank})", xy=(df.index[-1], rank), xytext=(10, 0), textcoords='offset points', fontsize=9, ha='left', va='center')
        ax.annotate(card, xy=(df.index[-1], rank), xytext=(50, 0), textcoords='offset points', color = colormap(df.columns.get_loc(card)), fontsize=9, ha='left', va='center')
        ax.annotate(card, xy=(df.index[0], firstrank), xytext=(-120, 0), textcoords='offset points', color = colormap(df.columns.get_loc(card)), fontsize=9, ha='left', va='center')

    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig(f'{COLORS[color]}.svg', format='svg')
    plt.show()

if __name__ == '__main__':
    repo = pygit2.Repository(repo_path)
    cardss = collect_json_with_dates(repo)
    for color in COLORS:
        plot(color) 
