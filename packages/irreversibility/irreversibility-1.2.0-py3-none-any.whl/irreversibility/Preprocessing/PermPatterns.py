

import numpy as np
from itertools import permutations
from scipy.stats import norm
from ..optionalNJIT import optional_njit



def TimeSeriesToPermPatterns( TS, pSize: int = 3, overlapping: bool = True ):

    """
    Add a small amplitude noise to break potential ties. The noise is applied to all values, and its amplitude is calculated as the minimum difference between pairs of values, to maintain the ranking.

    Parameters
    ----------
    TS : numpy.array
        Time series to be processed.

    Returns
    -------
    numpy.array
        Processed time series.

    Raises
    ------
    ValueError
        If the parameters are not correct.
    """

    if type( pSize ) is not int:
        raise ValueError("pSize is not an integer")
    if pSize < 2:
        raise ValueError("pSize cannot be smaller than 2")

    allPatts = np.array( list( permutations( range( pSize ) ) ) )

    encodedTS = []
    tStep = pSize
    if overlapping: tStep = 1

    for offset in range( 0, np.size( TS ) - pSize, tStep ):

        subTS = TS[ offset : ( offset + pSize ) ]
        order = np.argsort( subTS )
        delta = np.sum( np.abs( allPatts - order ), axis = 1 )
        index = np.argmin( delta )
        encodedTS.append( index )

    encodedTS = np.array( encodedTS )

    return encodedTS, allPatts

