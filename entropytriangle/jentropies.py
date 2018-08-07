import sys                          #' Sys.Exit 
import warnings                     #' Warnings 

import numpy as np                  #' Numpy 
import pandas as pd                 #' DataFrames manipulation
import scipy as sc               

from .auxfunc import * 


def jentropies2d(Nxy, base = 2):

    """
    Joint Entropy decomposition of a 2d contingency matrix due to a channel transmission

    > edf = jentropies2d (Nxy, base = 2)

    Parameters
    ----------
    Nxy : Contingency matrix for calculating the channel entropies
    base : The logarithm to be used in working out the sentropies (Default base = 2 -> "log2")

    Returns
    ----------
    edf : Pandas DataFrame containing the values of the entropies calculated from the contingency matrix

    """

    dims = Nxy.shape # dim is a tuple wiht dim[0] rows  and dim[1] columns

    if(len(dims) != 2):
        sys.exit("It must be a 2 dimensions array")

    Nx = Nxy.sum(axis = 1) ; Ny = Nxy.sum(axis = 0) 
    Hx = sc.stats.entropy(Nx , base = base) ; Hy = sc.stats.entropy(Ny , base = base)
    Ux = np.log2(dims[0]) ; Uy = np.log2(dims[1])
    Hxy = sc.stats.entropy(Nxy.reshape(np.prod(dims)), base  = base)
    VI_P = [(Hxy-Hy),(Hxy-Hx)]

    #edf = pd.DataFrame([Ux,Uy,Hx,Hy,Hxy], columns = ['Ux','Uy','Hx','Hy','Hxy'])
    edf = pd.DataFrame({'Type':['X','Y'],'H_P':[Hx,Hy] , 'H_U' : [Ux,Uy] ,'DeltaH_P':[(Ux - Hx) , (Uy - Hy)] , 'M_P': [Hx - VI_P[0] , Hy - VI_P[1]] , 'VI_P': VI_P }, columns = ['Type','H_U','H_P','DeltaH_P','M_P','VI_P'])
    edf = edf.append(edf.apply(lambda x: np.sum(x,axis=0),axis = 0), ignore_index=True)
    #edf.loc['All'] = edf.sum(axis = 0)
    edf = edf.set_index('Type')

    return edf





def jentropies_table(Nxy, base = 2):

    """
    Joint Entropy decomposition of a n-d contingency matrix due to a channel transmission

    > edf = jentropies_table (Nxy, base = 2)

    Parameters
    ----------
    Nxy : Contingency matrix for calculating the channel entropies
    base : The logarithm to be used in working out the sentropies (Default base = 2 -> "log2")

    Returns
    ----------
    edf : Pandas DataFrame containing the values of the entropies calculated from the contingency matrix

    """

    dims = Nxy.shape # dim is a tuple wiht dim[0] rows  and dim[1] columns

    if(len(dims) < 2):
        sys.exit("Cannot process joint entropies for tables with less than 2 dimensions")

    if (dims[1] < 2 or dims[2] < 2):
        stop("jentropies are not defined for distributions with a singleton domain.")

    if (len(dims) == 2):
        edf = jentropies2d(Nxy , base = base)

    else:	
        if (len(dims)==3):
            lis = list()
            for i in range((dims[0])): lis.append(jentropies2d(Nxy[i]))

        else:
            lis = list()
            Nxy = Nxy.reshape((np.prod(list(Nxy.shape[0:-2]))), Nxy.shape[-2], Nxy.shape[-1])
            for i in range((Nxy.shape[0])): lis.append(jentropies2d(Nxy[i]))

        edf = pd.concat(lis)

    return edf




def jentorpies_df(X,Y , base = 2):

    """
    Channel Entropy decomposition of two dataframes X and Y

    > edf = jentropies_df (X,Y, base = 2)

    Parameters
    ----------
    X, Y : DataFrame for calculating the channel entropies
    base : The logarithm to be used in working out the sentropies (Default base = 2 -> "log2")

    Returns
    ----------
    edf : Pandas DataFrame containing the values of the entropies calculated from the contingency matrix

    """

    dimx = X.shape ; dimy = Y.shape
    
    if(not isinstance(X,pd.DataFrame)):
        sys.exit("Can only work with Data Frames! (X it´s not a DataFrame)")
    
    if(not isinstance(Y,pd.DataFrame)):
        sys.exit("Can only work with Data Frames! (Y it´s not a DataFrame)")   
    
    if (dimx[0] == 0 or dimx[1] == 0):
        sys.exit("Can only work with non-empty data.frames X!")

    if (dimy[0] == 0 or dimy[1] == 0):
        sys.exit("Can only condition on non-empty data.frame Y!")

    if (dimx[0] != dimy[0]):	
        sys.exit("Can only condition on variable lists with the same number of instances!")

    if (not(all(X.dtypes)=='category')):
        warnings.warn("Discretizing data from X DataFrame before entropy calculation!") #' Throwing a Warning for communicating a discretization of data
        X = discretization(X)

    if (not(all(Y.dtypes)=='category')):
        warnings.warn("Discretizing data from X DataFrame before entropy calculation!") #' Throwing a Warning for communicating a discretization of data
        Y = discretization(Y)


    VI_P = np.array([condentropy_df(X,Y,base = base),condentropy_df(Y,X,base = base)])

    H_U = np.array([np.sum(X.apply((lambda x : np.log2(len(pd.unique(x)))), axis = 0).values) , np.sum(Y.apply((lambda x : np.log2(len(pd.unique(x)))), axis = 0).values)])
    H_P = np.array([np.sum(X.apply(ent,axis=0).values) , np.sum(Y.apply(ent,axis=0).values)])

    edf = pd.DataFrame({'Type' : ['X','Y'], 'H_U': H_U , 'H_P': H_P , 'DeltaH_P' : HU - HP, 'M_P' : HP - VI_P, 'VI_P ' : VI_P }, columns = ['Type','H_U','H_P','DeltaH_P','M_P','VI_P'])
    edf = edf.set_index('Type')
    edf.loc['Type'] = edf.sum(axis = 0)

    return edf



