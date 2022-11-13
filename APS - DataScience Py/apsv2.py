import numpy
import pandas
from plotnine import *
from ast import literal_eval

data = pandas.read_csv(
    "C:/Users/Vitor Russomano/VsCodeProjects/Notes/APS - DataScience Py/10411_games_with_centipawn_metrics.csv"
)
data = data.drop(
    ["Unnamed: 0", "White Expected Rating by ACPL", "Black Expected Rating by ACPL"],
    axis=1,
)
############

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

table = pandas.DataFrame.from_dict(table)

count = (
    pandas.cut(
        pandas.concat([data["White ELO"], data["Black ELO"]]),
        [0, 1200, 1800, 2200, 2500, 2700, 4000],
        labels=[
            "Beginner",
            "Average Player",
            "Expert Player",
            "Master",
            "Grandmaster",
            "Super Grandmaster",
        ],
    )
    .value_counts()
    .reset_index()
    .rename(columns={"index": "Title", 0: "Number of Games"})
)


pandas.merge(table, count)

############
table = data["Result"].value_counts() / data["Result"].count()
print(table)

############

data = data[data["Result"] != "*"]
table = data["Result"].value_counts() / data["Result"].count()
print(table)

############

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
data[["White Label", "Black Label", "Result"]]


###########



data.groupby(['White Label','Black Label'])['Result'].value_counts().unstack().fillna(0)



###############

data.assign(
    integer_result=lambda _: _.Result.replace({"1-0": 1, "1/2-1/2": 0.5, "0-1": 0})
).groupby(["White Label", "Black Label"]).agg(
    mean_int_result=("integer_result", "mean")
).reset_index().pipe(
    lambda _: ggplot(_, aes(x="Black Label", y="mean_int_result",fill='Black Label'))
    + geom_col()
    + facet_wrap("White Label") 
    + theme_minimal() 
   + theme(axis_text_x=element_blank()))

#################



data.query('`White Label`!= "Beginner" &  `Black Label` != "Beginner"').groupby(
    ["White Label", "Result"]
).size().fillna(0).unstack().transpose().apply(lambda x: x.div(x.sum(), axis=0)).drop(
    "Beginner", axis=1
).stack().reset_index().rename(
    columns={0: "Count"}
).pipe(
    lambda _: (
        ggplot(round(_,3), aes("White Label", "Result", fill="Count"))
        + geom_tile(aes(width=0.95, height=0.95))
        + scale_fill_distiller(direction=1)
        + geom_text(aes(label="Count"), size=4, fontweight="bold")
        + theme_minimal()
    )
)
############
(
    ggplot(data, aes(x="Moves"))
    + geom_density(alpha=0.1)
    + theme_minimal()
    + labs(title="Density of Games Moves", caption="Fonte: Elaborada pelo autor")
)

############

Q1 = numpy.percentile(data["Moves"], 25, method="midpoint")

Q3 = numpy.percentile(data["Moves"], 75, method="midpoint")


Interquartil = Q3 - Q1
upper = numpy.where(data["Moves"] >= (Q3 + 1.5 * Interquartil))


lower = numpy.where(data["Moves"] <= (Q1 - 1.5 * Interquartil))


data.drop(upper[0], inplace=True)
data.drop(lower[0], inplace=True)


(
    ggplot(
        pandas.concat(
            [
                data[["White Label", "Moves"]].rename(columns={"White Label": "Label"}),
                data[["Black Label", "Moves"]].rename(columns={"Black Label": "Label"}),
            ]
        )
    )
    + geom_boxplot(aes(x="Label", y="Moves"))
    + theme_minimal()
    + theme(axis_text_x=element_text(rotation=45, hjust=1))
)


############
## Analysis of evaluation


evaluation = data.copy()
evaluation["Evaluations List"] = data["Evaluations List"].apply(literal_eval)

evaluation = (
    evaluation.explode("Evaluations List")
    .reset_index()
    .rename(columns={"index": "game_number"})
    .assign(Depth=lambda _: evaluation.groupby(_.game_number).cumcount())
)

evaluation["Evaluations List"] = pandas.to_numeric(
    evaluation["Evaluations List"].div(100)
)


(
    evaluation.query("game_number==0").pipe(
        lambda _: (
            ggplot(_, aes(x="Depth", y="Evaluations List", group=1)) + geom_line()
        )
        + geom_hline(yintercept=0, linetype="dashed", color="red", size=1)
        + labs(title="Evaluation by Depth", caption="Fonte: Elaborada pelo autor")
        + theme_minimal()
    )
)

############
(
    evaluation.groupby("Depth", as_index=False)
    .agg(eval_mean=("Evaluations List", numpy.mean))
    .pipe(
        lambda _: (
            (ggplot(_, aes(x="Depth", y="eval_mean")) + geom_line())
            + geom_hline(yintercept=0, linetype="dashed", color="red", size=1)
            + theme_minimal()
            + labs(
                title="Mean evaluation by Depth", caption="Fonte: Elaborada pelo autor"
            )
            + ylim(-1.5, 1.5)
            + xlim(0, 120)
        )
    )
)
############


# FIXME: Not showing enough data. Something is happening along the way.
# FIXME: There are nan where it shouldnt be
(
    evaluation.groupby(
        ["Depth", "White Label"],
    )
    .agg(eval_mean=("Evaluations List", numpy.mean))
    .reset_index()
    .rename(columns={"White Label": "white_label"})
    .pipe(
        lambda _: ggplot(_, aes(x="Depth", y="Evaluations List"))
        + geom_area()
        + geom_smooth(method="lm", color="grey", linetype="dotted")
        + facet_wrap("white_label")
        + geom_hline(yintercept=0, linetype="dashed", color="red", size=1)
        + theme_minimal()
        + labs(title="____", caption="Fonte: Elaborada pelo autor")
        + xlim(0, 120)
    )
)

###########################
# Difference in numerical ELO
data = data.rename(columns={"White ELO": "white_elo", "Black ELO": "black_elo"}).assign(
    wtbdiff=lambda _: _.white_elo - _.black_elo,
    btwdiff=lambda _: _.black_elo - _.white_elo,
)


bins = numpy.arange(data["wtbdiff"].min(), data["btwdiff"].max(), 150)
pandas.merge(
    data.assign(
        binned_btw=lambda _: pandas.cut(_.btwdiff, bins=bins),
        integer_result=lambda _: _.Result.replace({"1-0": 1, "1/2-1/2": 0.5, "0-1": 0}),
    )
    .groupby("binned_btw")
    .agg(btw_mean=("integer_result", numpy.mean))
    .dropna(),
    data.assign(
        binned_wtb=lambda _: pandas.cut(_.wtbdiff, bins=bins),
        integer_result=lambda _: _.Result.replace({"1-0": 1, "1/2-1/2": 0.5, "0-1": 0}),
    )
    .groupby("binned_wtb")
    .agg(wtb_mean=("integer_result", numpy.mean))
    .dropna(),
    left_index=True,
    right_index=True,
).reset_index().melt(id_vars="index", value_vars=["btw_mean", "wtb_mean"]).pipe(
    lambda _: ggplot(_)
    + geom_line(aes(x="index", y="value", group="variable", colour="variable"))
    + geom_point(aes(x="index", y="value", group="variable", colour="variable"))
    + scale_color_manual(["grey", "black"])
    + theme_minimal()
    + theme(axis_text_x=element_text(rotation=90, hjust=1))
    + labs(title="____", caption="Fonte: Elaborada pelo autor")
)

# How does the Top 10 players differ
n = 10

topn = pandas.DataFrame(
    {
        "Player": data.filter(["White Name", "Black Name", "black_elo", "white_elo"])
        .melt(
            id_vars=["White Name", "Black Name"], value_vars=["white_elo", "black_elo"]
        )
        .sort_values(by="value", ascending=False)["White Name"]
        .unique()[0:10],
        "ELO": data.filter(["White Name", "Black Name", "black_elo", "white_elo"])
        .melt(
            id_vars=["White Name", "Black Name"], value_vars=["white_elo", "black_elo"]
        )
        .sort_values(by="value", ascending=False)["value"]
        .unique()[0:10],
        "Ranking (ELO)": numpy.arange(1, n + 1),
    }
)

(
    topn.pipe(lambda _: ggplot(_, aes(y="ELO", x="reorder(Player,ELO)")))
    + geom_point(colour="red")
    + geom_segment(
        aes(x="Player", xend="Player", y=min(topn["ELO"]), yend=max(topn["ELO"])),
        linetype="dashed",
        size=0.5,
        colour="grey",
    )
    + coord_flip()
    + theme_minimal()
    + theme(panel_grid_major_x=element_blank())
    + labs(title="Top 10 Player Ranking by ELO", caption="Fonte: Elaborada pelo autor")
)


data[data["White Name"].isin(list(topn["Player"]))].filter(
    ["White Name", "White Av CP Loss"]
).groupby("White Name").agg(w_cp_mean=("White Av CP Loss", numpy.mean)).merge(
    topn, left_index=True, right_on="Player"
).sort_values(
    "Ranking (ELO)"
)


data[data["Black Name"].isin(list(topn["Player"]))].filter(
    ["Black Name", "Black Av CP Loss"]
).groupby("Black Name").agg(b_cp_mean=("Black Av CP Loss", numpy.mean)).merge(
    topn, left_index=True, right_on="Player"
).sort_values(
    "Ranking (ELO)"
)


# General One


data["White CP Loss List"] = data["White CP Loss List"].apply(literal_eval)
data["Black CP Loss List"] = data["Black CP Loss List"].apply(literal_eval)


pandas.concat(
    [
        (
            data.filter(["White CP Loss List", "White Label"])
            .melt(
                id_vars=["White Label"],
                value_vars=["White CP Loss List"],
            )
            .rename(columns={"White Label": "Label"})
            .explode("value")
        ),
        (
            data.filter(["Black CP Loss List", "Black Label"])
            .melt(
                id_vars=["Black Label"],
                value_vars=["Black CP Loss List"],
            )
            .rename(columns={"Black Label": "Label"})
            .explode("value")
        ),
    ]
).apply(lambda x: pandas.to_numeric(x) if x.name == "value" else x).pipe(
    lambda _: ggplot(_, aes(x="value"))
    + geom_density(aes( fill="variable") , alpha=0.4)
    + facet_wrap("Label")
    + xlim(-1, 1)
    + theme_minimal()
)


# Compare top 10 and others in Mean CP Loss

