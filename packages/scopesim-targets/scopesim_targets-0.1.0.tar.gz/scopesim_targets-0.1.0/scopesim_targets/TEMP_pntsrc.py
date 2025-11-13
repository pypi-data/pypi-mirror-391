# -*- coding: utf-8 -*-
"""
Created on Sun Nov  9 15:42:13 2025

@author: ghost
"""
from astropy.coordinates import SkyCoord, concatenate


# try:
#     tgt.resolve_spectrum()
# except NotInLibraryError as err:
#     err.add_note(f"\nAvailable spectral types are:\n {'\n'.join(str(item) for item in DEFAULT_LIBRARY.items())}")
#     raise

class PointSourceCluster(Cluster):
    """Base class for Cluster of Point Source Targets."""

    def __init__(self, recipe=None, origin=None):
        super().__init__(recipe)

        self.origin = origin or recipe[0].position
        self.frame = self.origin.skyoffset_frame()

    def to_table(self):
        """Combine target recipe to single table."""
        # TODO: Deal more efficiently with generator recipes that might be able
        #       to return a table directly.
        coords = [
            target.position.transform_to(self.frame) for target in self.recipe
        ]
        return concatenate(coords).to_table()
