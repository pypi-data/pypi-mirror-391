"""
Class for managing input Numpy arrays to be chunked
"""
import numpy.typing as npt

from tomocompress.constants import DEFAULT_CHUNK_SIZE

class InputImageArray(object):
    """
    3D numpy array of images, iterated in chunks
    """

    def __init__(self, input_data:npt.NDArray, dataset__out_name:str = "data", chunk_size=DEFAULT_CHUNK_SIZE):

        self.dataset__out_name = dataset__out_name
        self.chunk_size = chunk_size  # a chunk_size of 1 corresponds to one 1 image
        self.shape = input_data.shape
        self.nrows = self.shape[0] # number of images

    def __iter__(self):
        """Returns a generator that allows iterating data in chunks"""

        # Yields data in chunks
        for i in range(0, self.nrows, self.chunk_size):
            # Calculate the slice for this chunk
            # the min function serves when we reach the end of nrows
            chunk_slice = slice(i, min(i + self.chunk_size, self.nrows))

            # Read the chunk from the input dataset
            data_chunk = input_dataset[chunk_slice]

            # Perform any processing on the data_chunk here if needed
            # Example: data_chunk = np.sqrt(data_chunk)

            yield chunk_slice, data_chunk

