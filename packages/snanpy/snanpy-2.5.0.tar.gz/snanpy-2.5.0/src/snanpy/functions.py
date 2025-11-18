from matplotlib import pyplot as plt
import matplotlib as mpl
import pandas as pd
import os

mpl.rcParams.update(mpl.rcParamsDefault)

plt.rc('text', usetex=True)
plt.rc('font', family='serif')

def figax(figsize=(8,6), xlim: tuple =None, ylim: tuple =None, xlabel: str=None, ylabel:str=None, title:str=None, font_size: int = 19):
    """
    Generates a plot environment.

    Parameters
    ----------
    figsize : tuple
    xlim : tuple
        Set the minimum and the maximum value of the x-axis
    ylim : tuple
        Set the minimum and the maximum value of the y-axis
    xlabel : str
        Set the xlabel
    ylabel : str
        Set the ylabel
    title : str
        Set the title
    font_size : int 
        Set the font size

    Returns
    -------
        The fig and ax from plt.subplots()
    """
    plt.rcParams.update({'font.size': font_size})
    fig, ax = plt.subplots(figsize=figsize, constrained_layout=True)
    ax.grid(linewidth=0.5) 
    if xlim is not None:
        ax.set_xlim(xlim)  
    if ylim is not None:
        ax.set_ylim(ylim) 
    ax.set_title(title)
    ax.set_ylabel(ylabel)
    ax.set_xlabel(xlabel) 

    return fig, ax

def saveplot(name: str, folder: str=None, dpi: int = 200, extension : str = 'png'):
    """
    Save a pyplot under specified name with specified resolution to specified folder

    Parameters
    ----------
    name : str
        File name that will be used 
    folder : str 
        Name of the subfolder in a 'Figures' folder the plot will be saved into. If it does not exist, it is generated.
    dpi : int
        Resolution of the plot
    extension : str 
        File extension to be used
    
    Returns
    -------
    None
    """

    
    base_path = os.path.join(os.getcwd(), 'Figures')
    if folder:
        path = os.path.join(base_path, folder)
    else:
        path = base_path
    os.makedirs(path, exist_ok=True)

    plt.savefig(path + '\\' + name + '.' + extension, dpi=dpi)

def cluster_and_slice(df, timestep=None, timeframe='1D', startdatetime=None, method='mean'):
    """
    Cluster and slice a time series DataFrame.
    
    Parameters
    ----------
    df : pd.DataFrame
        Input DataFrame with a DatetimeIndex.
    timestep : str or None, optional
        Resampling frequency (e.g. '15min', '1h', '1d', '1m', '1y'). 
        If None, keep original resolution.
    timeframe : str, optional
        Length of time to extract starting from startdatetime (e.g. '1h', '1d', '1m', '1y').
    startdatetime : str or pd.Timestamp, optional
        Starting datetime for the slice. Defaults to the first index value.
    method : str, optional
        Aggregation method for clustering ('mean' or 'sum').
    
    Returns
    -------
    pd.DataFrame
        Clustered and sliced DataFrame.
    """
    if not isinstance(df.index, pd.DatetimeIndex):
        raise ValueError("DataFrame index must be a DatetimeIndex (set parse_dates=True?)")

    # Determine start time
    if startdatetime is None:
        startdatetime = df.index.min()
    else:
        startdatetime = pd.Timestamp(startdatetime)

    # Compute end time based on timeframe
    enddatetime = startdatetime + pd.to_timedelta(timeframe)

    # Slice the timeframe
    sliced = df.loc[startdatetime:enddatetime]

    # Apply clustering / resampling
    if timestep is not None:
        if method == 'mean':
            clustered = sliced.resample(timestep).mean()
        elif method == 'sum':
            clustered = sliced.resample(timestep).sum()
        else:
            raise ValueError("method must be 'mean' or 'sum'")
    else:
        clustered = sliced.copy()

    # Drop rows with all NaNs after resampling
    clustered = clustered.dropna(how='all')
    
    return clustered

def list_filenames(path : str, extension : str):
    """
    Lists all filenames with a given extension

    Parameters
    ----------
    path: str
        Path of the folder
    extension: str
        Extension of the files (e.g. ".csv")

    Returns
    -------
    list
        List of all filenames with the given extension
    """
    filenames = []
    for filename in os.listdir(path):
        if filename.endswith(f'{extension}'):
            filenames.append(filenames)
    return filenames