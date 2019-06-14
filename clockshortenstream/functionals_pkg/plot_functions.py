import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd

sns.set()


def plot_histogram(filename,metric_name,array):

    fig, ax = plt.subplots(ncols=1, nrows=1, figsize=(20, 20), sharex='col', sharey='row')
    plt.suptitle('Distribution of ' + metric_name,fontsize=30)
    plt.setp(ax.get_xticklabels(), visible=True)
    sns.distplot(array, kde=True, rug=True, hist=True, ax=ax, color='green')
    plt.savefig(filename,bbox_inches='tight')
    plt.close()


def plot_graph(filename,x_metric,y_metric,array_x,array_y):

    fig, ax = plt.subplots(ncols=1, nrows=1, figsize=(20, 20), sharex='col', sharey='row')
    d = {x_metric:array_x,y_metric:array_y}
    pd_d = pd.DataFrame(d)

    plt.suptitle('Graph of ' + x_metric +' vs '+y_metric,fontsize=30)

    plt.setp(ax.get_xticklabels(), visible=True)
    sns.lineplot(x=x_metric, y=y_metric, data=pd_d, ax=ax, markers=True)
    plt.savefig(filename, bbox_inches='tight')
    plt.close()

