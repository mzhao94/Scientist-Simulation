# collect.py
# execute the run.py program before running collect.py!

import multiprocessing as mp
import pickle
import pandas as pd
import timeit
import input_file
from functions import *
from run_graphs import *


def main():
    input_file.start = timeit.default_timer()

    # initiate multiprocessing with 'num_processors' threads
    # NOTE: increasing the number of processors does not always increase speed of program. in fact, it may actually
    # slow down the program due to the additional overhead needed for process switching
    # NOTE: fork doesn't work on Mac, spawn is best because it works on Mac and is default on Windows
    mp.set_start_method('spawn')
    p = mp.Pool(processes=input_file.num_processors)  # default number is mp.cpu_count()

    # get starting time from run.py
    start_prog = int(open('tmp/start_prog.txt', 'r').read())

    model_directory = 'tmp/model/'
    agent_vars = pd.read_pickle(model_directory + 'agent_vars_df.pkl')
    model_vars = pd.read_pickle(model_directory + 'model_vars_df.pkl')
    data1 = pd.read_pickle(model_directory + 'data1.pkl')
    ind_vars = pd.read_pickle(model_directory + 'ind_vars.pkl')
    effort_invested_by_age = np.load(model_directory + 'effort_invested_by_age.npy')
    with open(model_directory + "final_perceived_returns_invested_ideas.txt", "rb") as fp:
        final_perceived_returns_invested_ideas = pickle.load(fp)

    arg_list = [("agent", agent_vars), ("model", model_vars), ("data1", data1), ("ind_vars", ind_vars),

                ("im_graph", ind_vars['agent_k_invested_ideas'], ind_vars['agent_perceived_return_invested_ideas'], "k",
                 "perceived returns",
                 "perceived return vs cost for all INVESTED ideas across all scientists,time periods (biased)", False,
                 "perceived", True),

                ("im_graph", ind_vars['agent_k_invested_ideas'], ind_vars['agent_perceived_return_invested_ideas'], "k",
                 "perceived returns",
                 "perceived return vs cost for all INVESTED ideas across all scientists,time periods (biased)", False,
                 "perceived", False),

                ("im_graph", ind_vars['agent_k_invested_ideas'], ind_vars['agent_actual_return_invested_ideas'], "k",
                 "actual returns",
                 "actual return vs cost for all INVESTED ideas across all scientists,time periods (biased)", False,
                 "actual", True),

                ("im_graph", ind_vars['agent_k_invested_ideas'], ind_vars['agent_actual_return_invested_ideas'], "k",
                 "actual returns",
                 "actual return vs cost for all INVESTED ideas across all scientists,time periods (biased)", False,
                 "actual", False),

                ("resid_scatterplot", ind_vars['agent_actual_return_invested_ideas'],
                 ind_vars['agent_perceived_return_invested_ideas'],
                 final_perceived_returns_invested_ideas, "Scientist ID", "Residual",
                 "Residuals for all INVESTED ideas (actual-perceived)"),

                ("two_var_bar_graph", effort_invested_by_age, "Idea", "Marginal Effort Invested",
                 "Marginal Effort Invested By Young and Old Scientists For All Ideas", True),

                ("two_var_bar_graph", effort_invested_by_age, "Idea", "Marginal Effort Invested",
                 "Marginal Effort Invested By Young and Old Scientists For All Ideas", False),

                # runtime is WAY too long for linear y
                ("two_var_scatterplot", data1['avg_k'], data1['total_pr'], "k", "perceived returns",
                 "perceived return vs cost for INVESTED ideas (plot to check for bias)", True),

                ("two_var_scatterplot", data1['avg_k'], data1['total_pr'], "k", "perceived returns",
                 "perceived return vs cost for INVESTED ideas (plot to check for bias)", False)]

    p.starmap(func_distr, arg_list)  # starmap maps each function call into a parallel thread
    p.close()
    p.join()

    # saves all of the images to an html file
    png_to_html()

    stop_run("Total time to process data")

    print("\nEND OF PROGRAM\ntotal runtime:", timeit.default_timer() - start_prog, "seconds")


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
        # print("\n\n\nDATAFRAME (AGENT)\n",agent_vars.to_string())
        agent_vars.to_html('web/pages/page_agent_vars.html')
        # agent_vars.to_csv('web/csv/csv_agent_vars.csv')
    elif graph_type == "model":
        # model dataframe (other[0] contains model_vars)
        model_vars = other[0]
        # print("\n\n\nDATAFRAME (MODEL)\n",model_vars.to_string())
        model_vars.to_html('web/pages/page_model_vars.html')
        # model_vars.to_csv('web/csv/csv_model_vars.csv')
    elif graph_type == "data1":
        # serious data table
        data1 = other[0]
        data1.to_html('web/pages/page_data1.html')
        # data1.to_csv('web/csv/data1.csv')
    elif graph_type == "ind_vars":
        ind_vars = other[0]
        ind_vars.sort_values("agent_k_invested_ideas", inplace=True)
        # print("\n\n\nDATAFRAME (IND VARS)\n", ind_vars.to_string())
        ind_vars.to_html('web/pages/page_ind_vars.html')
        # ind_vars.to_csv('web/csv/csv_ind_vars.csv')
    elif graph_type == "im_graph":
        im_graph(*other)
    elif graph_type == "resid_scatterplot":
        resid_scatterplot(*other)
    elif graph_type == "two_var_scatterplot":
        two_var_scatterplot(*other)
    elif graph_type == "two_var_bar_graph":
        two_var_bar_graph(*other)

    gc_collect()
    stop = timeit.default_timer()
    print("\nfinished", graph_type, stop-start, "seconds")


if __name__ == '__main__':  # for multiprocessor package so it knows the true main/run function
    main()