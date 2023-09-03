import os
import json
import pygit2
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator
from matplotlib.dates import DateFormatter
#import plotly.express as px
from datetime import datetime
from numpy import nan

BRANCH_NAME = 'gh-pages'
FILENAME = 'data/cards.json'
#COLORS = {'W': 'White', 'U': 'Blue', 'B': 'Black', 'R': 'Red', 'G': 'Green'}
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

if __name__ == '__main__':
    repo = pygit2.Repository(repo_path)
    cardss = collect_json_with_dates(repo)
   
    for (date,cards) in cardss:
        blue = {cardname: value['identity_rank'] for cardname, value in cards.items() if value['color_identity'] == ["U"]}
        #column = {}
        #for cardname, value in blue.items():
        #    column[cardname] = {card: cardname, rank: value['identity_rank']}
        data[date] = blue
        #print(list(blue.items())[0])
        #break
    
    #print(data)
    #dates = list(data.keys())
    #card_ranks = {card: [data[date].get(card, 999) for date in dates] for card in data[dates[0]].keys()}

    df = pd.DataFrame.from_dict(data, orient='index')
    df = df.reindex(columns=sorted(df.columns), fill_value=nan)
    
    # Filter and keep only the cards whose rank is below 20 at least once
    filtered_cards = df.columns[df.lt(20).any()]
    df = df[filtered_cards]

    # Create the bump chart
    fig, ax = plt.subplots(figsize=(15, 9))
    for card in df.columns:
        ax.plot(df.index, df[card], marker='o') #, label=card)
        ax.text(df.index[-1], df[card].iloc[-1], card, va='center', ha='left', fontsize=9, color='blue')
 #   for card, ranks in card_ranks.items():
 #       ax.plot(dates, ranks, marker='o', label=card)

    # Customize the plot
    ax.set_title('Most played blue cards over time')
    ax.set_xlabel('Date')
    ax.xaxis.set_major_locator(MaxNLocator(integer=True))
    date_format = DateFormatter("%b %Y")
    ax.xaxis.set_major_formatter(date_format)
    #xticks_datetime = [datetime.strptime(label, '%Y%m%d') for label in ax.get_xticklabels()]
    #xticks_labels = [label.get_text() for label in ax.get_xticklabels()]
    #ax.set_xticklabels(xticks_datetime, rotation=45)

    ax.set_ylabel('Rank')
    ax.set_ylim(0, 20.5)
    ax.set_yticks(range(1, 21))
    ax.invert_yaxis()
    ax.legend(loc='best')
    ax.grid()

    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.show()

