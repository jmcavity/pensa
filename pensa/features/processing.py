import numpy as np
import scipy as sp
import scipy.stats
import scipy.spatial
import scipy.spatial.distance
import pyemma
from pyemma.util.contexts import settings
import MDAnalysis as mda
import matplotlib.pyplot as plt
import os
import warnings
#from pensa.features import *



# -- Utilities to extract time series --


def get_feature_data(feat, data, feature_name):
    """
    Returns the timeseries of one particular feature.
    
    Parameters
    ----------
        feat : list of str
            List with all feature names.
        data : float array
            Feature values data from the simulation.
        feature_name : str
           Name of the selected feature.
    
    Returns
    -------
        timeseries : float array
            Value of the feature for each frame.
    
    """
    # Select the feature and get its index.
    index = np.where( np.array( feat ) == feature_name )[0][0]
    # Extract the timeseries.
    timeseries = data[:,index]
    return timeseries


def get_feature_timeseries(feat, data, feature_type, feature_name):
    """
    Returns the timeseries of one particular feature from a set with several feature types.
    
    Parameters
    ----------
        feat : list of str
            List with all feature names.
        data : float array
            Feature values data from the simulation.
        feature_type : str
            Type of the selected feature 
            ('bb-torsions', 'bb-distances', 'sc-torsions').
        feature_name : str
           Name of the selected feature.
    
    Returns
    -------
        timeseries : float array
            Value of the feature for each frame.
    
    """
    timeseries = get_feature_data(feat[feature_type], data[feature_type], feature_name)
    return timeseries


def get_multivar_res_timeseries(feat, data, feature_type, write=None, out_name=None):
    """
    Returns the timeseries of one particular feature.
    
    Parameters
    ----------
    feat : list of str
        List with all feature names.
    data : float array
        Feature values data from the simulation.
    feature_type : str
        Type of the selected feature 
        ('bb-torsions', 'bb-distances', 'sc-torsions').
    write : bool, optional
        If true, write out the data into a directory titled with the feature_type str.
        The default is None.
    out_name : str, optional
        Prefix for the written data. The default is None.    

    Returns
    -------
    feature_names : list of str
        Names of all features
    features_data : numpy array
        Data for all features
    """
    
    # Initialize the dictionaries.
    feature_names = {}
    features_data = {}
    
    feat_name_list = feat[feature_type]
    #obtaining the residue numbers 
    res_numbers = [int(feat_name.split()[-1]) for feat_name in feat_name_list]
    #grouping indices where feature refers to same residue
    index_same_res = [list(np.where(np.array(res_numbers)==seq_num)[0])
                      for seq_num in list(set(res_numbers))]   
    #obtaining timeseries data for each residue
    multivar_res_timeseries_data=[]
    sorted_names = []
    for residue in range(len(index_same_res)):
        feat_timeseries=[]
        for residue_dim in index_same_res[residue]:
            single_feat_timeseries = get_feature_timeseries(feat,data,feature_type,feat_name_list[residue_dim])            
            feat_timeseries.append(list(single_feat_timeseries))
        multivar_res_timeseries_data.append(feat_timeseries)
        feat_name_split = feat_name_list[residue_dim].split()
        resname = feat_name_split[-2] + ' ' + feat_name_split[-1] 
        sorted_names.append(resname)
        if write is True:
            for subdir in [feature_type+'/']:
                if not os.path.exists(subdir):
                    os.makedirs(subdir)
            resname_out = feat_name_split[-2] + feat_name_split[-1] 
            filename= feature_type+'/' + out_name + resname_out + ".txt"
            np.savetxt(filename, feat_timeseries, delimiter=',', newline='\n')
            
    # return multivar_res_timeseries_data
    feature_names[feature_type]=sorted_names
    features_data[feature_type]=np.array(multivar_res_timeseries_data, dtype=object)
    # Return the dictionaries.
    return feature_names, features_data            

  
def match_sim_lengths(sim1,sim2):
    """
    Make two lists the same length by truncating the longer list to match.


    Parameters
    ----------
    sim1 : list
        A one dimensional distribution of a specific feature.
    sim2 : list
        A one dimensional distribution of a specific feature.

    Returns
    -------
    sim1 : list
        A one dimensional distribution of a specific feature.
    sim2 : list
        A one dimensional distribution of a specific feature.

    """
    if len(sim1)!=len(sim2):
        if len(sim1)>len(sim2):
            sim1=sim1[0:len(sim2)]
        if len(sim1)<len(sim2):
            sim2=sim2[0:len(sim1)]  
    return sim1, sim2



# -- Utilities to sort the features


def sort_features(names, sortby):
    """
    Sorts features by a list of values.
    
    Parameters
    ----------
    names : str array
        Array of feature names.
    sortby : float array
        Array of the values to sort the names by.
        
    Returns
    -------
    sort : array of tuples [str,float]
        Array of sorted tuples with feature and value.
    
    """
    # Get the indices of the sorted order
    sort_id = np.argsort(sortby)[::-1]  
    # Bring the names and values in the right order
    sorted_names  = []
    sorted_values = []
    for i in sort_id:
        sorted_names.append(np.array(names)[i])
        sorted_values.append(sortby[i])
    sn, sv = np.array(sorted_names), np.array(sorted_values)
    # Format for output
    sort = np.array([sn,sv]).T
    return sort


def sort_sincos_torsions_by_resnum(tors, data):
    """
    Sort sin/cos of torsion features by the residue number..
    Parameters
    ----------
    tors : list of str
        The list of torsion features.
    Returns
    -------
    new_tors : list of str
        The sorted list of torsion features.
    """
    renamed = []
    for t in tors:
        rn = t.split(' ')[-1].replace(')','')
        ft = t.split(' ')[0].replace('(',' ')
        sincos, angle = ft.split(' ')
        renamed.append('%09i %s %s'%(int(rn),angle,sincos))
    new_order = np.argsort(renamed)
    new_tors = np.array(tors)[new_order].tolist()
    new_data = data[:,new_order]
    return new_tors, new_data


def sort_distances_by_resnum(dist, data):
    """
    Sort distance features by the residue number..
    Parameters
    ----------
    dist : list of str
        The list of distance features.
    Returns
    -------
    new_dist : list of str
        The sorted list of distance features.
    """
    renamed = []
    for d in dist:
        rn1, at1, rn2, at2 = np.array(d.split(' '))[np.array([2,3,6,7])]
        renamed.append('%09i %s %09i %s'%(int(rn1),at1,int(rn2),at2))
    new_order = np.argsort(renamed)
    new_dist = np.array(dist)[new_order].tolist()
    new_data = data[:,new_order]
    return new_dist, new_data


def select_common_features(features_a, features_b):
    intersect = set(features_a).intersection(features_b)
    is_common_a = [f in intersect for f in features_a]
    is_common_b = [f in intersect for f in features_b]
    return np.array(is_common_a), np.array(is_common_b)
    


# -- Utilities to process feature data --


def correct_angle_periodicity(angle):
    """
    Correcting for the periodicity of angles [radians].  
    Waters featurized using PENSA and including discrete occupancy are handled.
    
    Parameters
    ----------
    angle : list
        Univariate data for an angle feature.

    Returns
    -------
    new_angle : list
        Periodically corrected angle feature.

    """
    new_angle = angle.copy()
    continuous_angles = [angle for angle in new_angle if angle != 10000.0]
    index_cont_angles = [index for index, angle in enumerate(new_angle) if angle != 10000.0]      
    heights = np.histogram(continuous_angles, bins=90, density=True)
    ## Shift everything before bin with minimum height by periodic amount
    if heights[0][0] > min(heights[0]):   
        perbound = heights[1][np.where(heights[0] == min(heights[0]))[0][0]+1]
        for angle_index in range(len(continuous_angles)):
            if continuous_angles[angle_index] < perbound:
                continuous_angles[angle_index] += 2*np.pi
    for index in range(len(index_cont_angles)):
        new_angle[index_cont_angles[index]] = continuous_angles[index]
    return new_angle


