import pandas
import matplotlib.pyplot
import plotnine
from plotnine import *

data = pandas.read_csv("APS - DataScience Py/10411_games_with_centipawn_metrics.csv")
data = data.drop(
    ["Unnamed: 0", "White Expected Rating by ACPL", "Black Expected Rating by ACPL"],
    axis=1,
)


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

pd = (
    data.groupby(["White Label", "Black Label", "Result"])[
        ["White Label", "Black Label"]
    ]
    .value_counts()
    .unstack()
    .fillna(0)
)

pd = pd.div(pd.sum(axis=1), axis=0).fillna(0)
teste = pd.stack().reset_index()
teste.columns = ["White Label", "Black Label", "Result", "count"]
teste["Comb"] = (
    teste["White Label"].astype(str) + "-" + teste["Black Label"].astype(str)
)

(
    ggplot(round(teste, 3), aes("Result", "Comb", fill="count"))
    + geom_tile(aes(width=0.95, height=0.95))
    + scale_fill_distiller(direction=1)
    + geom_text(aes(label="count"), size=10)
    + theme_light()
)


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









