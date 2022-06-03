
import seaborn as sns

from collections import Counter
from itertools import combinations
import pandas as pd

import networkx as nx
from nxviz.plots import CircosPlot, ArcPlot
import matplotlib.pyplot as plt

import csv

paper_keywords = {}
with open('article_keywords.csv') as csv_file:
    csv_reader = csv.reader(csv_file, delimiter=',')
    first = True
    for row in csv_reader:
        if first:
            first = False
            continue

        if row[0] == "" or row[1] == "":
            continue

        keywords = [x.strip().lower() for x in row[1].split(';')]
        if len(keywords) < 2 :
            continue

        paper_keywords[ row[0] ] = keywords

#
# expertise centered
#

# Create dataframe 

keyword_connections = list(
    map(lambda x: list(combinations(x, 2)), paper_keywords.values())
)
flat_connections = [item for sublist in keyword_connections for item in sublist]

df = pd.DataFrame(flat_connections, columns=["From", "To"])
df_graph = df.groupby(["From", "To"]).size().reset_index()
df_graph.columns = ["From", "To", "Count"]

keywords_flat = [
    keyword
    for keywords in paper_keywords.values()
    for keyword in keywords
]

df_graph.to_excel("article_keyword_graph_edge_table.csv")

# Create graph

G = nx.from_pandas_edgelist(
    df_graph, source="From", target="To", edge_attr="Count"
)

top_keywords = pd.DataFrame.from_records(
    Counter(keywords_flat).most_common(70), columns=["Name", "Count"]
)

top_nodes = (n for n in list(G.nodes()) if n in list(top_keywords["Name"]))

G_top = G.subgraph(top_nodes)

for n in G_top.nodes():
    G_top.nodes[n]["Number of papers"] = int(
        top_keywords[top_keywords["Name"] == n]["Count"]
    )

# Create Plots

c = CircosPlot(
    G_top,
    dpi=600,
    node_grouping="Number of papers",
    edge_width="Count",
    figsize=(20, 20),
    node_color="Number of papers",
    node_labels=True,
    group_legend=True,
    #node_label_layout="rotation"
)
c.draw()
plt.tight_layout(rect=(0.05, 0.05, 0.95, 0.95)) 
plt.savefig("Keywords_top_circos.png")
plt.show()

options = {
	"node_color": "blue",
	"node_size": 20,
	"edge_color": "grey",
	"linewidths": 0,
	"width": 0.1,
}

plt.figure(figsize=(20, 20)) 
pos = nx.kamada_kawai_layout(G_top) 
nx.draw(G_top,pos, **options)
nx.draw_networkx_labels(G_top,pos)
plt.savefig("Keywords_top_spring_layout.png")
plt.show()

#plt.figure(figsize=(20, 20)) 
#pos = nx.spring_layout(G) 
#nx.draw(G,pos, **options)
#nx.draw_networkx_labels(G,pos)
#plt.savefig("Keywords_spring_layout.png")
#plt.show()

sns.set(rc={'figure.figsize':(7,11)})
sns.barplot(x="Count", y="Name", data=top_keywords, palette="RdBu_r")
plt.title("Top Keywords")
plt.tight_layout() 
plt.savefig("Keywords_top_rank.png")
plt.show()

dc = nx.degree_centrality(G_top)
x=sorted(dc,key=dc.get)
y=[dc[k] for k in x]
sns.barplot(x=y,y=x)
#plt.xticks(rotation=70)
plt.tight_layout()
plt.savefig("Keywords_top_degree_centrality.png")
plt.show()

#dc = nx.degree_centrality(G)
#x=sorted(dc,key=dc.get)
#y=[dc[k] for k in x]
#sns.barplot(x=y,y=x)
##plt.xticks(rotation=70)
#plt.tight_layout()
#plt.savefig("Expertise_degree_centrality.png")
#plt.show()


