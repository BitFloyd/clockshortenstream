import matplotlib.pyplot as plt
import seaborn as sns
sns.set()


def plot_histogram(filename,metric_name,array):

    fig, ax = plt.subplots(ncols=1, nrows=1, figsize=(20, 20), sharex='col', sharey='row')
    plt.suptitle('Distribution of ' + metric_name,fontsize=30)
    plt.setp(ax.get_xticklabels(), visible=True)
    sns.distplot(array, kde=True, rug=True, hist=True, ax=ax, color='green')
    plt.savefig(filename,bbox_inches='tight')
    plt.close()