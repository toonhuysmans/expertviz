
from urllib.request import urlopen, urljoin
from bs4 import BeautifulSoup

import seaborn as sns

from collections import Counter
from itertools import combinations
import pandas as pd

import networkx as nx
from nxviz.plots import CircosPlot, ArcPlot
import matplotlib.pyplot as plt

# Scrape Expertise

base_url = "https://www.tudelft.nl/"

search_terms = ["scanning","usability","biomechanics","orthopedics","digital+human+modeling","physical+ergonomics","biomechanics","anthropometry","comfort"]
#["ergnomics","human+factors","scanning","usability","biomechanics","orthopedics","teamwork","cognition","perception","hci","lighting","digital+human+modeling","physical+ergonomics","biomechanics","anthropometry","comfort"]
#search_terms = ["teamwork","organisational+ergonomics"]
#search_terms = ["perception","cognition","hci","lighting"]
#search_terms = ["digital+human+modeling","physical+ergonomics","biomechanics","anthropometry","comfort"]


people_urls = []
for term in search_terms:

	print("Searching for people with expertise:", term)

	search_url = "https://www.tudelft.nl/io/onderzoek/expertise?q=" + term
	search_result_page = urlopen(search_url)

	soup = BeautifulSoup(search_result_page, 'html.parser')
	people_urls.extend( [ link.get('href') for link in soup.find_all("a") if link.get("href") and "personen/" in link.get('href') ] )


people_expertise = {}
for people_url in set(people_urls):
	people_page = urlopen( urljoin(base_url,people_url) if people_url[0] == "/" else people_url )

	soup = BeautifulSoup(people_page, 'html.parser')

	try:
		name = soup.find(attrs={"class": "profile"}).h3.string
	except:
		continue

	print("Collecting expertise from:", name)

	expertise = []
	new_expertise = soup.body.get("data-tags")
	if new_expertise :
		expertise.extend( [ entry.strip()[2:].lower() for entry in new_expertise.split(",") ] )

	old_expertise = soup.head.find("meta",attrs={"name":"keywords"})
	if old_expertise :
		expertise.extend( [ entry.strip().lower() for entry in old_expertise.get("content").split(",") ] )

	people_expertise[ name ] = list(set( expertise ))

#
# expertise centered
#

# Create dataframe 

expertise_connections = list(
    map(lambda x: list(combinations(x, 2)), people_expertise.values())
)
flat_connections = [item for sublist in expertise_connections for item in sublist]

df = pd.DataFrame(flat_connections, columns=["From", "To"])
df_graph = df.groupby(["From", "To"]).size().reset_index()
df_graph.columns = ["From", "To", "Count"]

expertises_flat = [
    expertise
    for expertises in people_expertise.values()
    for expertise in expertises
]

# Create graph

G = nx.from_pandas_edgelist(
    df_graph, source="From", target="To", edge_attr="Count"
)

top_expertises = pd.DataFrame.from_records(
    Counter(expertises_flat).most_common(50), columns=["Name", "Count"]
)

top_nodes = (n for n in list(G.nodes()) if n in list(top_expertises["Name"]))

G_top = G.subgraph(top_nodes)

for n in G_top.nodes():
    G_top.nodes[n]["Number of staff"] = int(
        top_expertises[top_expertises["Name"] == n]["Count"]
    )

# Create Plots

c = CircosPlot(
    G_top,
    dpi=600,
    node_grouping="Number of staff",
    edge_width="Count",
    figsize=(20, 20),
    node_color="Number of staff",
    node_labels=True,
    group_legend=True,
    #node_label_layout="rotation"
)
c.draw()
plt.tight_layout(rect=(0.05, 0.05, 0.95, 0.95)) 
plt.savefig("Expertises_top_circos.png")
plt.show()

options = {
	"node_color": "blue",
	"node_size": 20,
	"edge_color": "grey",
	"linewidths": 0,
	"width": 0.1,
}

plt.figure(figsize=(20, 20)) 
pos = nx.spring_layout(G_top) 
nx.draw(G_top,pos, **options)
nx.draw_networkx_labels(G_top,pos)
plt.savefig("Expertises_top_spring_layout.png")
plt.show()

plt.figure(figsize=(20, 20)) 
pos = nx.spring_layout(G) 
nx.draw(G,pos, **options)
nx.draw_networkx_labels(G,pos)
plt.savefig("Expertises_spring_layout.png")
plt.show()

sns.set(rc={'figure.figsize':(11.7,8.27)})
sns.barplot(x="Count", y="Name", data=top_expertises, palette="RdBu_r")
plt.title("Top Expertises")
plt.tight_layout() 
plt.savefig("Expertises_top_rank.png")
plt.show()

dc = nx.degree_centrality(G_top)
x=sorted(dc,key=dc.get)
y=[dc[k] for k in x]
sns.barplot(x=y,y=x)
#plt.xticks(rotation=70)
plt.tight_layout()
plt.savefig("Expertise_top_degree_centrality.png")
plt.show()

#dc = nx.degree_centrality(G)
#x=sorted(dc,key=dc.get)
#y=[dc[k] for k in x]
#sns.barplot(x=y,y=x)
##plt.xticks(rotation=70)
#plt.tight_layout()
#plt.savefig("Expertise_degree_centrality.png")
#plt.show()


#
# people centered
#

#all_expertises = list(set(expertises_flat))
all_expertises = top_expertises.Name.to_list()

# reorder data
expertise_people = { e : [] for e in all_expertises }
for person, expertises in people_expertise.items():
	for e in expertises:
		if e in all_expertises:
		 	expertise_people[e].append(person)

# Create dataframe

people_connections = list(
    map(lambda x: list(combinations(x, 2)), expertise_people.values())
)
flat_connections = [item for sublist in people_connections for item in sublist]

df = pd.DataFrame(flat_connections, columns=["From", "To"])
df_graph = df.groupby(["From", "To"]).size().reset_index()
df_graph.columns = ["From", "To", "Count"]

people_flat = [
    person
    for people in expertise_people.values()
    for person in people
]

# Create graph

G = nx.from_pandas_edgelist(
    df_graph, source="From", target="To", edge_attr="Count"
)

top_people = pd.DataFrame.from_records(
    Counter(people_flat).most_common(50), columns=["Name", "Count"]
)

top_nodes = (n for n in list(G.nodes()) if n in list(top_people["Name"]))

G_top = G.subgraph(top_nodes)

for n in G_top.nodes():
    G_top.nodes[n]["Number of expertises"] = int(
        top_people[top_people["Name"] == n]["Count"]
    )

# Create Plots

c = CircosPlot(
    G_top,
    dpi=600,
    node_grouping="Number of expertises",
    edge_width="Count",
    figsize=(20, 20),
    node_color="Number of expertises",
    node_labels=True,
    group_legend=True,
   # node_label_layout="rotation"
)
c.draw()
plt.tight_layout(rect=(0.15, 0.15, 0.85, 0.85)) 
plt.savefig("People_top_circos.png")
plt.show()


plt.figure(figsize=(20, 20)) 
pos = nx.spring_layout(G_top) 
nx.draw(G_top,pos, **options)
nx.draw_networkx_labels(G_top,pos)
plt.savefig("People_top_spring_layout.png")
plt.show()

plt.figure(figsize=(20, 20)) 
pos = nx.spring_layout(G) 
nx.draw(G,pos, **options)
nx.draw_networkx_labels(G,pos)
plt.savefig("People_spring_layout.png")
plt.show()

sns.set(rc={'figure.figsize':(11.7,8.27)})
sns.barplot(x="Count", y="Name", data=top_people, palette="RdBu_r")
plt.title("Top People")
plt.tight_layout() 
plt.savefig("People_ranking.png")
plt.show()

dc = nx.degree_centrality(G_top)
x=sorted(dc,key=dc.get)
y=[dc[k] for k in x]
sns.barplot(x=y,y=x)
#plt.xticks(rotation=70)
plt.tight_layout()
plt.savefig("People_top_degree_centrality.png")
plt.show()

#dc = nx.degree_centrality(G)
#x=sorted(dc,key=dc.get)
#y=[dc[k] for k in x]
#sns.barplot(x=y,y=x)
##plt.xticks(rotation=70)
#plt.tight_layout()
#plt.savefig("People_degree_centrality.png")
#plt.show()
