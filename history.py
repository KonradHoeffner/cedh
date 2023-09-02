import os
import json
import pygit2
#import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime

repo_path = os.getcwd()
branch_name = 'gh-pages'
filename = 'data/cards.json'
COLORS = {'W': 'White', 'U': 'Blue', 'B': 'Black', 'R': 'Red', 'G': 'Green'}

def collect_json_with_dates(repo):
    branch = repo.branches[branch_name]
    cardss = []
    for commit in repo.walk(branch.target, pygit2.GIT_SORT_TOPOLOGICAL | pygit2.GIT_SORT_REVERSE):
        commit_date = datetime.utcfromtimestamp(commit.commit_time).strftime('%Y%m%d')
        if filename in commit.tree:
            data_blob = repo.get(commit.tree[filename].id)
            data_content = json.loads(data_blob.data.decode('utf-8'))
            cardss.append((commit_date, data_content))
            break # faster testing first only
    return cardss

if __name__ == '__main__':
    repo = pygit2.Repository(repo_path)
    cardss = collect_json_with_dates(repo)
   
    for (date,cards) in cardss:
        #keys = list(cards.keys())
        #keys.sort()
        print(cards['Ponder'])
        #blue = filter(lambda card: card.color_identity == ['U'], cards)
        blue = {cardname: value for cardname, value in cards.items() if value['color_identity'] == ["U"]}
        print(list(blue)[0:10])
        # todo
        # Create a relative rank change plot
        plt.plot(time_points, item1_ranks, label='Item 1')
        plt.plot(time_points, item2_ranks, label='Item 2')

        # Customize the plot (remove y-axis label and ticks)
        plt.ylabel('Relative Rank')
        plt.tick_params(axis='y', which='both', left=False)

        # Add legend and title
        plt.legend()
        plt.title('Relative Rank Change Over Time')

        # Show the plot
        plt.show()

        break
