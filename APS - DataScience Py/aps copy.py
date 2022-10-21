import pandas
import matplotlib.pyplot
import plotnine
from plotnine import *

data = pandas.read_csv("C:/Users/Vitor Russomano/VsCodeProjects/Notes/APS - DataScience Py/10411_games_with_centipawn_metrics.csv")
data = data.drop(
    ["Unnamed: 0", "White Expected Rating by ACPL", "Black Expected Rating by ACPL"],
    axis=1,
)

data = data[data['Result'] != '*']

# join both sides elo
# show counts and freq


table = {
    "Title": [
        "Super Grandmaster",
        "Grandmaster",
        "Master",
        "Expert Player",
        "Average Player",
        "Beginner",
    ],
    "ELO": ["2700+", "2500+", "2200-2499", "1800-2199", "1200-1799", "<1200"],
}
pandas.DataFrame(table)


# Full elo
teste = pandas.concat([data["White ELO"], data["Black ELO"]])

count = pandas.cut(
    teste,
    [0, 1200, 1800, 2200, 2500, 2700, 4000],
    labels=[
        "Beginner",
        "Average Player",
        "Expert Player",
        "Master",
        "Grandmaster",
        "Super Grandmaster",
    ],
).value_counts()



#
data["Result"].value_counts() / data["Result"].count()

###############

data[["White Label", "Black Label"]] = data[["White ELO", "Black ELO"]].apply(
    lambda x: pandas.cut(
        x,
        [0, 1200, 1800, 2200, 2500, 2700, 4000],
        labels=[
            "Beginner",
            "Average Player",
            "Expert Player",
            "Master",
            "Grandmaster",
            "Super Grandmaster",
        ],
    ),
    axis=0,
)

pda = (
    data.groupby(["White Label", "Black Label", "Result"])['Result'].size()
    .unstack(fill_value=0))



pd = (
    data.groupby(["Black Label", "White Label", "Result"])['Result'].size()
    .unstack(fill_value=0))


k = k.div(k.sum(axis=1), axis=0).fillna(0)


testando = pandas.DataFrame({"0-1" : pd.iloc[:,0] + pda.iloc[:,1] ,"1-0":pd.iloc[:,1] + pda.iloc[:,0], "1/2-1/2": pd.iloc[:,2]})


ok = pd.reset_index()[pd.reset_index()['Black Label'] == pd.reset_index()['White Label']].set_index(['Black Label','White Label'])

testando.update(ok)

############################

filtered = data[(data['White Label'] != 'Beginner') & (data['Black Label']!= 'Beginner') &(data['Result'] != '*')]

pd = filtered.groupby(["White Label", "Result"]).size().fillna(0).unstack()
pd = pd.drop('Beginner')
pd = pd.div(pd.sum(axis=1), axis=0).fillna(0)


teste = pd.stack().reset_index()
teste.columns = ["White Label", "Result", "count"]


(
    ggplot(round(teste, 3), aes("White Label", "Result", fill="count"))
    + geom_tile(aes(width=0.95, height=0.95))
    + scale_fill_distiller(direction=1)
    + geom_text(aes(label="count"), size=4, fontweight="bold")
    + theme_light()
)


######
data["Comb"] = (
    data["White Label"].astype(str) + "-" + data["Black Label"].astype(str)
)



data.groupby(['Comb','Result']).size().fillna(0).unstack()
