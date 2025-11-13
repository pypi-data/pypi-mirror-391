"""
Compressor interface
Author: Nicolas Soler (SDM)
"""

import os
import numpy as np
import logging
import h5py
import blosc2
import blosc2_grok
import hdf5plugin

from abc import ABC, abstractmethod
#from timeit_decorator import timeit_sync as timeit  # decorator for timing functions
from tqdm.auto import tqdm  # progress bar

# Custom code
# from codec import Codec
from tomocompress.hdf5_data import Hdf5DataFile
from tomocompress.input_image_array import InputImageArray
from tomocompress.utils import new_hdf5_path
from tomocompress.constants import DEFAULT_CR, DEFAULT_CHUNK_SIZE

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)


# --------------
class Compressor(ABC):
    """Interface for Compressor"""

    @abstractmethod
    def compress(self):
        raise NotImplementedError(
            "The 'compress' method must be implemented in subclasses"
        )

    @abstractmethod
    def decompress(self):
        raise NotImplementedError(
            "The 'decompress' method must be implemented in subclasses"
        )


class HDF5Compressor(Compressor):
    """Intermediate compressor class for handling HDF5"""

    def __init__(
        self,
        input_hdf5: str,
        input_np_array: np.ndarray = None,
        dataset_name: str = "data,dark,flat",
        chunk_size: int = DEFAULT_CHUNK_SIZE,
    ):
        """
        param input_hdf5: path to the input HDF5 file to compress
        param inputImageArray: InputImageArray object (alternative to input_hdf5, if not None, superseeds input_hdf5)
        param dataset_name: the name of the dataset to compress
        param chunk_size: the size of the chunks to be compressed
        """

        # If an input 3D np array of data is provided, use it
        self.input_img_array = None
        if input_np_array is not None:
            self.input_img_array = InputImageArray(
                input_data=input_np_array,
                dataset_name=dataset_name,
                chunk_size=chunk_size,
            )

            self.input_hdf5_obj = None
            self.chunk_size = self.input_img_array.chunk_size

        # Else, the user provides an HDF5 file path with the names of datasets to be compressed
        else:
            if not input_hdf5:
                raise ValueError("No input HDF5 file provided")

            if not dataset_name:
                raise ValueError("You need to specify a dataset name to be compressed")

            self.input_hdf5_obj = Hdf5DataFile(
                path=input_hdf5, dataset_names=dataset_name, chunk_size=chunk_size
            )
            self.chunk_size = self.input_hdf5_obj.chunk_size

    def compress(self):
        raise NotImplementedError(
            "The 'compress' method must be implemented in subclasses"
        )

    def decompress(self):
        raise NotImplementedError(
            "The 'decompress' method must be implemented in subclasses"
        )


class Blosc2GrokCompressor(HDF5Compressor):
    """
    Wrapper for Blosc2&Grok compression
    It creates a compressed file in the same directory as the original file,
    (with the prefix "compressed_grok_")
    """

    def __init__(
        self,
        input_hdf5: str = "",
        input_np_array: np.ndarray = None,
        dataset_name: str = "data,dark,flat",
        compression_ratio: float = DEFAULT_CR,
        chunk_size: int = DEFAULT_CHUNK_SIZE,
        output_file_path="",
    ):
        """
        see https://gist.github.com/t20100/80960ec46abd3a863e85876c013834bb

        param input_hdf5: path to the input HDF5 file to compress
        param inputImageArray: InputImageArray object (alternative to input_hdf5, if not None, superseeds input_hdf5)
        param dataset_name: the name of the dataset to compress
        param compression_ratio: the desired compression ratio
        param output_file_path: path to the output compressed HDF5 file (if empty, a new file is created next to the input file)
        """

        super().__init__(input_hdf5=input_hdf5,
                         input_np_array=input_np_array,
                         dataset_name=dataset_name,
                         chunk_size=chunk_size)

        self._compression_ratio = compression_ratio
        self.output_file_path = output_file_path

    @property
    def compression_ratio(self) -> float:
        """Target compression ratio"""
        if isinstance(self._compression_ratio, (int, float)):
            if self._compression_ratio <= 0:
                raise ValueError(f"Compression ratio must be positive, not {self._compression_ratio}")
            return self._compression_ratio
        else:
            raise ValueError(f"Compression ratio must be a number, not {type(self._compression_ratio)}")


    def _np2blosc2arr(self, data: np.ndarray) -> blosc2.NDArray:
        """
        Compress a 3D array with blosc2&grok as a stack of JPEG2000 images.

        param data: Numpy 3D array of data to be compressed
        """
        # The input HDF5 object has to be turned into a Numpy array
        # to be then transformed by _np2blosc2arr
        # Setting the Grok plugin

        blosc2_grok.set_params_defaults(
            cod_format=blosc2_grok.GrkFileFmt.GRK_FMT_JP2,
            quality_mode="rates",
            quality_layers=np.array([self.compression_ratio], dtype=np.float64),
        )

        # Returns a compressed numpy array
        # Conversation with F.Alted 12 June 2025
        # The array returned must be 2D (i.e. the shape of an image)
        # for example (1, 256, 256)
        # because JPEG2K doesn't know how to deal with 3D arrays
        # in this context there is one block per chunk,
        # The compression must be done image per image.
        one_image_shape = (1,) + data.shape[1:]  # one image # (1, height, width)

        return blosc2.asarray(
            data,
            chunks=one_image_shape,  # chunks must be 2D (i.e. one image)
            blocks=one_image_shape,  # one block per chunk (conversation with Francesc)
            cparams={
                "codec": blosc2.Codec.GROK,
                "filters": [],
                "splitmode": blosc2.SplitMode.NEVER_SPLIT,
            },
        )

    def _blosc_grok_compress_chunk(self, input_dataset_obj:InputImageArray, output_hdf5:str, compressed_dataset_name:str):
        """
        Iterates through the input dataset object, compresses it chunk by chunk
        param input_dataset_obj: Input HDF5Data object or InputImageArray object to be compressed
        param output_hdf5: path to the output HDF5 file where to store the compressed dataset
        param compressed_dataset_name: name of the dataset to create inside the output HDF5 file
        """

        with h5py.File(output_hdf5, "a") as h5f:
            # Create the HDF5 dataset

            # Input HDF5Data object
            dataset_in = input_dataset_obj

            if self.compression_ratio > 1:


                n_images = dataset_in.nrows  # total number of images to process

                logging.info("## source dataset name: " + dataset_in.dataset_name)
                logging.info("data.shape: " + str(dataset_in.shape))
                logging.info("data.dtype: " + str(dataset_in.dtype))
                logging.info("Compressing images, please wait.")

                # Output HDF5 dataset
                logging.debug(f"creating dataset {compressed_dataset_name}")
                dataset_out = h5f.create_dataset(
                    compressed_dataset_name,
                    shape=dataset_in.shape,
                    dtype=dataset_in.dtype,
                    chunks=(
                        dataset_in.chunk_size,
                        dataset_in.shape[1],
                        dataset_in.shape[2],
                    ),
                    allow_unknown_filter=True,
                    compression=hdf5plugin.Blosc2(),
                )

                # Feeding the compressor one image at a time
                for i, (chunk_slice, data_chunk) in tqdm(
                    enumerate(dataset_in), desc="Images compressed", total=n_images
                ):
                    offset = (
                        chunk_slice.start,
                        0,
                        0,
                    )  # Move one chunk size along the first axis

                    # Compress the data with blosc2 & grok
                    blosc2_array = self._np2blosc2arr(data_chunk)
                    cframe = blosc2_array.schunk.to_cframe()

                    # Write the compressed data to HDF5 using direct chunk write
                    dataset_out.id.write_direct_chunk(offset, cframe)

                logging.info(f"Wrote: {self.compression_ratio}x blosc2_grok (JPEG2K) compressed dataset in {output_hdf5}")

            else: # compression ratio of 1
                logging.info("Compression ratio of 1, copying dataset without compression.")
                # Copying the dataset without compression
                h5f.create_dataset(
                    compressed_dataset_name,
                    data=dataset_in.input_data,
                    chunks=(
                        dataset_in.chunk_size,
                        dataset_in.shape[1],
                        dataset_in.shape[2],
                    ),
                )


    def compress(self) -> h5py.Dataset:
        """
        Store data compressed with blosc2&grok in a new dataset
        """
        if not self.input_hdf5_obj and not self.input_img_array:
            raise ValueError("No input data provided for compression")

        #----- Working with an input Numpy array (superseeds any input HDF5 file)
        elif self.input_img_array:
            dataset_in = self.input_img_array

            if self.output_file_path:
                compressed_hdf5_name = os.path.abspath(self.output_file_path)

                # if only a directory has been specified, create a new file name
                if "." not in os.path.basename(compressed_hdf5_name):
                    compressed_hdf5_name = os.path.join(
                        compressed_hdf5_name,
                        f"{self.compression_ratio}X_blosc2grok_compressed_data.h5",
                    )
            else:
                compressed_hdf5_name = new_hdf5_path(
                    "in_memory_array.h5",
                    f"{self.compression_ratio}X_blosc2grok_compressed_",
                    remove=True,
                )

            if os.path.exists(compressed_hdf5_name):
                logging.warning(f"Removing previous compressed dataset {compressed_hdf5_name}")
                os.remove(compressed_hdf5_name)
 
            # Compressing with Blosc
            self._blosc_grok_compress_chunk(dataset_in, compressed_hdf5_name, dataset_in.dataset_name)

        #----- Working with an input HDF5 file if no input Numpy array-----
        elif self.input_hdf5_obj:
            # output file
            if self.output_file_path:
                compressed_hdf5_name = os.path.abspath(self.output_file_path)

                # if only a directory has been specified, create a new file name
                if "." not in os.path.basename(compressed_hdf5_name):
                    compressed_hdf5_name = os.path.join(
                        compressed_hdf5_name,
                        f"{self.compression_ratio}X_blosc2grok_compressed_{os.path.basename(self.input_hdf5_obj.path)}",
                    )
            
            else:
                compressed_hdf5_name = new_hdf5_path(
                    self.input_hdf5_obj.path,
                    f"{self.compression_ratio}X_blosc2grok_compressed_",
                    remove=True,
                )
            output_hdf5 = self.input_hdf5_obj.copy_without_data()

            logging.info("Target compression ratio: " + str(self.compression_ratio))

            # Going through all datasets to compress in the input HDF5 dataset:
            for input_dataset_obj in self.input_hdf5_obj.dataset_obj_list:
                # The compressed dataset name (including path)
                # in the output file (same as in input HDF5)
                compressed_dataset_name = (input_dataset_obj.dataset_path)  # entire path inside hdf5

                # Compress this input Numpy array and add it to the output HDF5
                self._blosc_grok_compress_chunk(input_dataset_obj, output_hdf5, compressed_dataset_name)
                

            os.rename(output_hdf5, compressed_hdf5_name)
        return compressed_hdf5_name

    def decompress(self):
        pass


#---- trying the program
def main():
    # creating a Numpy array of 100 images to feed in
    data_array = np.random.randint(0, 256, size=(100, 512, 512), dtype=np.uint8)

    # Compressing it in a new HDF5 file with Blosc2&Grok
    compressor = Blosc2GrokCompressor(input_np_array=data_array,
                                      dataset_name="data",
                                      compression_ratio=2,
                                      output_file_path="2X_compressed.h5"
                                      )
    compressor.compress()

if __name__ == "__main__":
    main()
