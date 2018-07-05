# collect.py
# execute the run.py program before running collect.py!

import multiprocessing as mp
import pickle
import pandas as pd
import timeit
import config
from functions import *
from run_graphs import *
import time
from IPython.core.display import HTML


def main():
    config.start = timeit.default_timer()

    # initiate multiprocessing with 'num_processors' threads
    # NOTE: increasing the number of processors does not always increase speed of program. in fact, it may actually
    # slow down the program due to the additional overhead needed for process switching
    # NOTE: fork doesn't work on Mac, spawn is best because it works on Mac and is default on Windows
    mp.set_start_method('spawn')
    p = mp.Pool(processes=config.num_processors)  # default number is mp.cpu_count()

    # get starting time from run.py
    start_prog = int(open(config.tmp_loc + 'start_prog.txt', 'r').read())

    # loading variables after model is done running
    model_directory = config.tmp_loc + 'model/'
    agent_vars = pd.read_pickle(model_directory + 'agent_vars_df.pkl')
    model_vars = pd.read_pickle(model_directory + 'model_vars_df.pkl')
    ideas = pd.read_pickle(model_directory + 'ideas.pkl')
    ind_ideas = pd.read_pickle(model_directory + 'ind_ideas.pkl')
    # effort_invested_by_age = np.load(model_directory + 'effort_invested_by_age.npy')
    social_output = np.load(model_directory + 'social_output.npy')
    ideas_entered = np.load(model_directory + 'ideas_entered.npy')
    prop_age = np.load(model_directory + 'prop_age.npy')
    prop_idea = np.load(model_directory + 'prop_idea.npy')
    marginal_effort_by_age = np.load(model_directory + 'marginal_effort_by_age.npy')
    with open(model_directory + "final_perceived_returns_invested_ideas.txt", "rb") as fp:
        final_perceived_returns_invested_ideas = pickle.load(fp)

    arg_list = [("agent", agent_vars), ("model", model_vars), ("ideas", ideas), ("ind_ideas", ind_ideas),

                # ("im_graph", ind_ideas['agent_k_invested_ideas'], ind_ideas['agent_perceived_return_invested_ideas'], "k",
                #  "perceived returns",
                #  "perceived return vs cost for all INVESTED ideas across all scientists,time periods (biased)", False,
                #  "perceived", True),
                #
                # ("im_graph", ind_ideas['agent_k_invested_ideas'], ind_ideas['agent_perceived_return_invested_ideas'], "k",
                #  "perceived returns",
                #  "perceived return vs cost for all INVESTED ideas across all scientists,time periods (biased)", False,
                #  "perceived", False),
                #
                # ("im_graph", ind_ideas['agent_k_invested_ideas'], ind_ideas['agent_actual_return_invested_ideas'], "k",
                #  "actual returns",
                #  "actual return vs cost for all INVESTED ideas across all scientists,time periods (biased)", False,
                #  "actual", True),
                #
                # ("im_graph", ind_ideas['agent_k_invested_ideas'], ind_ideas['agent_actual_return_invested_ideas'], "k",
                #  "actual returns",
                #  "actual return vs cost for all INVESTED ideas across all scientists,time periods (biased)", False,
                #  "actual", False),

                # COMMENTED OUT PARAMS ARE GRAPHS THAT PLOT FOR EACH INDIVIDUAL SCIENTIST THAT AREN"T WORTH GRAPHING
                # (they take a lot of time to graph since there's so many scientists but they don't tell use anything)

                # ("resid_scatterplot", ind_ideas['agent_actual_return_invested_ideas'],
                #  ind_ideas['agent_perceived_return_invested_ideas'],
                #  final_perceived_returns_invested_ideas, "Scientist ID", "Residual",
                #  "Residuals for all INVESTED ideas (actual-perceived)"),

                # ("two_var_bar_graph", effort_invested_by_age, "Idea", "Marginal Effort Invested",
                #  "Marginal Effort Invested By Young and Old Scientists For All Ideas", True),
                #
                # ("two_var_bar_graph", effort_invested_by_age, "Idea", "Marginal Effort Invested",
                #  "Marginal Effort Invested By Young and Old Scientists For All Ideas", False),

                # runtime is WAY too long for linear y
                # ("two_var_scatterplot", ideas['avg_k'], ideas['total_pr'], "k", "perceived returns",
                #  "perceived return vs cost for INVESTED ideas (plot to check for bias)", True),

                # ("two_var_scatterplot", ideas['avg_k'], ideas['total_pr'], "k", "perceived returns",
                #  "perceived return vs cost for INVESTED ideas (plot to check for bias)", False),
                #
                # # puts the above scatterplot in perspective with other imgraphs
                # # this is for invested ideas across all scientists/tp while the other ones are just all the ideas that
                # # scientists invested in
                # ("im_graph", ideas['avg_k'], ideas['total_pr'], "k", "perceived returns",
                #  "(IM) perceived return vs cost for INVESTED ideas (plot to check for bias)", False, "IM", False),
                #
                # ("line_graph", ideas_entered, social_output, True, "# of ideas entered in lifetime", "total research output",
                #  "Average Total Research Output Vs # Of Ideas Entered in Lifetime", False),
                #
                # ("line_graph", ideas_entered, social_output, False, "# of ideas entered in lifetime", "total research output",
                #  "Cum Total Research Output Vs # Of Ideas Entered in Lifetime", False),

                ("line_graph", ideas_entered, social_output, True, "# of ideas entered in lifetime", "total research output",
                 "Average Total Research Output Vs # Of Ideas Entered in Lifetime", True),

                # ("line_graph", ideas_entered, social_output, False, "# of ideas entered in lifetime", "total research output",
                #  "Cum Total Research Output Vs # Of Ideas Entered in Lifetime", True),

                ("one_var_bar_graph", prop_age, "scientist age", "fraction paying k",
                 "Proportion of Scientists Paying to Learn By Age", "age"),

                ("one_var_bar_graph", prop_idea, "age of idea", "proportion of scientists working on the idea",
                 "Proportion of Scientists Working Based on Age of Idea", "idea"),

                ("two_var_line_graph", marginal_effort_by_age, "age of idea", "marginal effort",
                 "Effort Invested By Ages of Ideas and Scientists", False)]

    p.starmap(func_distr, arg_list)  # starmap maps each function call into a parallel thread
    p.close()
    p.join()

    # saves all of the images to an html file
    png_to_html()

    stop_run("Total time to process data")

    print("\nEND OF PROGRAM\ntotal runtime:", time.time() - start_prog, "seconds")


# assigning which function to call in the run_graphs.py file
def func_distr(graph_type, *other):
    start = timeit.default_timer()

    # set dataframe settings to max width, max rows, and max columns since we are collecting large quantities
    # of data and printing out entire arrays/tuples
    pd.set_option("display.max_colwidth", -1)
    pd.set_option('display.max_columns', None)
    pd.set_option('display.max_rows', None)

    if graph_type == "agent":
        # agent dataframe (other[0] contains agent_vars)
        agent_vars = other[0]
        agent_vars = agent_vars.replace(np.nan, '', regex=True).replace("\\r\\n", "<br>", regex=True)
        # print("\n\n\nDATAFRAME (AGENT)\n",agent_vars.to_string())
        HTML(agent_vars.to_html('web/pages/page_agent_vars.html', escape=False))
        # agent_vars.to_csv('web/csv/csv_agent_vars.csv')
        agent_vars = None
    elif graph_type == "model":
        # model dataframe (other[0] contains model_vars)
        model_vars = other[0]
        model_vars = model_vars.replace(np.nan, '', regex=True).replace("\\r\\n", "<br>", regex=True)  # .transpose()
        # print("\n\n\nDATAFRAME (MODEL)\n",model_vars.to_string())
        HTML(model_vars.to_html('web/pages/page_model_vars.html', escape=False))
        # model_vars.to_csv('web/csv/csv_model_vars.csv')
        model_vars = None
    elif graph_type == "ideas":
        # serious data table
        data1 = other[0].astype(str)
        columns = ['scientists_invested', "times_invested", "avg_k", "total_effort (marginal)", "prop_invested",
                   "total_pr", "total_ar"]
        for col in columns:
            data1.ix[pd.to_numeric(data1[col], errors='coerce') == 0, [col]] = ''
        data1.to_html('web/pages/page_ideas.html')
        # data1.to_csv('web/csv/data1.csv')
        data1 = None
    elif graph_type == "ind_ideas":
        ind_vars = other[0]
        ind_vars = ind_vars.transpose()
        # ind_vars.sort_values("agent_k_invested_ideas", inplace=True)
        # print("\n\n\nDATAFRAME (IND VARS)\n", ind_vars.to_string())
        ind_vars.to_html('web/pages/page_ind_ideas.html')
        # ind_vars.to_csv('web/csv/csv_ind_vars.csv')
        ind_vars = None
    elif graph_type == "line_graph":
        line_graph(*other)
    elif graph_type == "im_graph":
        im_graph(*other)
    elif graph_type == "resid_scatterplot":
        resid_scatterplot(*other)
    elif graph_type == "two_var_scatterplot":
        two_var_scatterplot(*other)
    elif graph_type == "two_var_bar_graph":
        two_var_bar_graph(*other)
    elif graph_type == "one_var_bar_graph":
        one_var_bar_graph(*other)
    elif graph_type == "two_var_line_graph":
        two_var_line_graph(*other)

    gc_collect()
    stop = timeit.default_timer()
    print("\nfinished", graph_type, stop-start, "seconds")


if __name__ == '__main__':  # for multiprocessor package so it knows the true main/run function
    main()
