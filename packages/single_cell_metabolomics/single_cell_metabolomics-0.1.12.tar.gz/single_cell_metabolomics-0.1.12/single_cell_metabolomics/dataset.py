# %%
import numpy as np
import pandas as pd
from scipy.sparse import coo_matrix, save_npz
import pyopenms as oms
# import multiprocessing as mp
# import itertools
# from functools import partial

from typing import List
from pathlib import Path
import typer
from loguru import logger
from tqdm import tqdm

from .database import DatabaseController

resultDBWorker = DatabaseController(table_name='analysis_results')

# %%
app = typer.Typer(add_completion=False)

# @app.command()
# def main(
#     # ---- REPLACE DEFAULT PATHS AS APPROPRIATE ----
#     input_path: Path = RAW_DATA_DIR / "dataset.csv",
#     output_path: Path = PROCESSED_DATA_DIR / "dataset.csv",
#     # ----------------------------------------------
# ):
#     # ---- REPLACE THIS WITH YOUR OWN CODE ----
#     logger.info("Processing dataset...")
#     for i in tqdm(range(10), total=10):
#         if i == 5:
#             logger.info("Something happened for iteration 5.")
#     logger.success("Processing dataset complete.")
#     # -----------------------------------------

@app.command()
def mzml2tsv(input_path = Path('.'), output_path = Path('.'), integration_type = 'sum'):
    logger.info(f'Read file: {input_path}')
    exp = oms.MSExperiment()
    oms.MzMLFile().load(input_path, exp)
    spectra = exp.getSpectra()
    spectra_ms1 = [s for s in spectra if s.getMSLevel() == 1]

    positions = []
    intensities = []
    polarities = []
    polarity_map = {
        oms.IonSource.Polarity.POSITIVE: 'positive',
        oms.IonSource.Polarity.NEGATIVE: 'negative',
        oms.IonSource.Polarity.POLNULL: 'polnull'
    }
    scan_number = len(spectra_ms1)
    for i in range(scan_number):
        positions.extend(spectra_ms1[i].get_peaks()[0])
        intensities.extend(spectra_ms1[i].get_peaks()[1])
        polarities.extend(
            [polarity_map.get(spectra_ms1[i].getInstrumentSettings().getPolarity(), None)] *
            len(spectra_ms1[i].get_peaks()[0])
        )
    data = pd.DataFrame(
        {
            'position': positions,
            'intensity': intensities,
            'mode': polarities
        }
    )
    data['position'] = np.round(data['position'], 4)
    if integration_type == 'mean':
        data['intensity'] = data['intensity'] / scan_number
    data = data.groupby(['mode', 'position']).agg({'intensity': 'sum'}).reset_index()

    logger.info(f'Write file: {output_path}')
    data.to_csv(output_path, sep='\t', index=False, header=False)

def create_bins(lower_bound, upper_bound, bin_width):
    bins = []
    added_bound = lower_bound
    while added_bound < upper_bound:
        bins.append(added_bound)
        added_bound = added_bound + added_bound * bin_width / 1e6
    bins.append(added_bound)
    return bins

def get_bins_center(bins):
    n = len(bins)
    bins = np.array(bins)
    bin_center = (bins[:n-1] + bins[1:]) / 2
    return bin_center

@app.command()
def bindata(
    input_path = Path('.'),
    output_path = Path('.'),
    BIN_WIDTH: float = 0.0003,
    BIN_WIDTH_UNIT: str = 'm/z',
    MS_LOWER_BOUND: float = 100,
    MS_UPPER_BOUND: float = 1500
):
    logger.info(f'Read file: {input_path}')
    data = pd.read_table(input_path, header=None, names=['mode', 'position', 'intensity'])
    data = data[(data['position'] >= MS_LOWER_BOUND) & (data['position'] <= MS_UPPER_BOUND)]

    if BIN_WIDTH_UNIT == 'ppm':
        bins = create_bins(MS_LOWER_BOUND, MS_UPPER_BOUND, BIN_WIDTH)
    elif BIN_WIDTH_UNIT == 'm/z':
        bins = np.arange(MS_LOWER_BOUND - BIN_WIDTH / 2, MS_UPPER_BOUND + BIN_WIDTH, BIN_WIDTH)
    bins_center = get_bins_center(bins)
    data['bin_index'] = np.digitize(data['position'], bins, right=False) - 1

    binned_data = data.groupby(['mode', 'bin_index']).agg({'position': 'mean', 'intensity': 'sum'}).reset_index()
    bin_center = bins_center[binned_data['bin_index']]
    binned_data['bin_center'] = [f'{i:.4f}' for i in bin_center]

    output = binned_data[['mode', 'bin_center', 'intensity']]
    logger.info(f'Write file: {output_path}')
    output.to_csv(output_path, sep='\t', index=False, header=False)


def read_tsv_file(file_path):
    """
    Reads a tsv file and renames the columns for merging.
    """
    try:
        df = pd.read_table(
            file_path,
            sep='\t',
            header=None,
            names=['mode', 'mass', f'{file_path.stem}']
        )
        return df
    except FileNotFoundError:
        logger.error(f'File not found: {file_path}')
        return None
    except pd.errors.EmptyDataError:
        logger.error(f'Empty tsv file: {file_path}')
        return None
    except Exception as e:
        logger.error(f'Error reading file {file_path}: {e}')
        return None

def build_sparse_matrix(dataframes, mass_set):
    """
    Builds a sparse matrix from a list of DataFrames based on 'mode' and 'mass_binned'.
    """
    mass_list = sorted(list(mass_set))
    row_names = mass_list
    index_map = {mass: idx for idx, mass in enumerate(mass_list)}
    rows = []
    cols = []
    data = []
    column_names = []
    for col_idx, df in tqdm(enumerate(dataframes)):
        column_names.append(df.columns[-1])  # Last column is the intensity
        for _, row in df.iterrows():
            mass_key = (row['mode'], row['mass'])
            if mass_key in index_map:
                row_idx = index_map[mass_key]
                rows.append(row_idx)
                cols.append(col_idx)
                data.append(row.iloc[-1])  # Last column is the intensity

    sparse_matrix = coo_matrix(
        (data, (rows, cols)),
        shape=(len(row_names), len(dataframes))
    )
    return sparse_matrix, row_names, column_names

# def transpose_to_csr_matrix(sparse_matrix, row_names, column_names):
#     """
#     Transposes a sparse matrix.
#     """
#     return sparse_matrix.transpose().tocsr(), column_names, row_names

@app.command()
def mergetsv(dataset_id: int, input_tsvs: List[Path] = [], output_tsv = Path('.')):
    """
    Combines a list of DataFrames on the 'mode' and 'mass' columns using sparse matrix representation.
    """
    dataframes = []
    mass_set = set()
    for tsv in input_tsvs:
        df = read_tsv_file(tsv)
        if df is not None:
            dataframes.append(df)
            mass_set.update(zip(df['mode'], df['mass']))

    if not dataframes:
        logger.error('No valid dataframes to combine.')
        return None

    try:
        sparse_matrix, row_names, column_names = build_sparse_matrix(dataframes, mass_set)
        # combined_df = pd.DataFrame.sparse.from_spmatrix(
        #     sparse_matrix,
        #     index=pd.MultiIndex.from_tuples(row_names, names=['mode', 'mass']),
        #     columns=column_names
        # )
        # combined_df.reset_index(inplace=True)
        # return combined_df
        
        # logger.info(f'Write sparse matrix to {output_folder / "combined_sparse_matrix.npz"}')
        # save_npz(output_folder / 'combined_sparse_matrix.npz', sparse_matrix)
        # row_df = pd.DataFrame(row_names, columns=['mode', 'mass'])
        # row_df.to_csv(output_folder / 'row_names.tsv', sep='\t', index=False, header=True)
        # col_df = pd.DataFrame(column_names, columns=['sample'])
        # col_df.to_csv(output_folder / 'column_names.tsv', sep='\t', index=False, header=True)
        resultDBWorker.create_data(
            dataset_id = dataset_id,
            pipeline_stage = 'preprocessing',
            result_type = 'mergetsv_sparse_matrix',
            result_data = {
                'sparse_matrix': {
                    'data': sparse_matrix.data.tolist(),
                    'row': sparse_matrix.row.tolist(),
                    'col': sparse_matrix.col.tolist(),
                    'shape': sparse_matrix.shape
                },
                'row_names': row_names,
                'column_names': column_names
            }
        )
        pd.DataFrame(row_names, columns=['mode', 'mass']).to_csv(
            output_tsv, sep='\t', index=False, header=True
        )

    except Exception as e:
        logger.error(f'Error combining DataFrames: {e}')
        return None


# def concat_dataframes(base_df, df_chunk):
#     """
#     Function to join a list of dataframes with the base_df.
#     """
#     df_chunk = [df.set_index(['mode', 'mass_binned']) for df in df_chunk]
#     df_chunk = [base_df.join(df, how='left') for df in df_chunk]
#     result = pd.concat(df_chunk, axis=1)
#     return result

# def combine_dataframes(dataframes, mass_set, N_PROCESSORS=16):
#     """
#     Combines a list of DataFrames on the 'mass_binned' column using outer merge.
#     """
#     if not dataframes:
#         logger.error('No valid dataframes to combine.')
#         return None

#     try:
#         mass_list = sorted(list(mass_set))
#         index = pd.MultiIndex.from_tuples(mass_list, names=['mode', 'mass_binned'])
#         logger.info(f'Created MultiIndex with {len(index)} (mode, mass_binned) combinations.')
#         base_df = pd.DataFrame(index=index)

#         logger.info(f'Concat {len(dataframes)} dataframes.')
#         chunk_size = len(dataframes) // N_PROCESSORS
#         chunks = [dataframes[i:i + chunk_size] for i in range(0, len(dataframes), chunk_size)]
#         del dataframes
#         logger.info(f'Concat {len(chunks)} dataframe chunks.')
#         with mp.Pool(processes=N_PROCESSORS) as pool:
#             results = pool.starmap(concat_dataframes, zip(itertools.repeat(base_df, len(chunks)), chunks))
#         del chunks
#         logger.info(f'Concat {len(results)} combination results.')
#         final_result = pd.concat(results, axis=1)
#         final_result.reset_index(inplace=True)
#         del results
#         return final_result
#     except Exception as e:
#         logger.error(f'Error combining DataFrames: {e}')
#         return None

# def read_dataframe_and_mass(tsv_path):
#     df = read_tsv_file(tsv_path)
#     if df is not None:
#         return(df, zip(df['mode'], df['mass_binned']))

# def combine_tsvs(input_tsvs, N_PROCESSORS=16):
#     """
#     Combines multiple tsv files into a single DataFrame based on 'mode' and 'mass_binned'.
#     """
#     logger.info('Input tsv files')
#     with mp.Pool(processes=N_PROCESSORS) as pool:
#         results = pool.map(read_dataframe_and_mass, input_tsvs)
#     dataframes = []
#     mass_set = set()
#     for content in results:
#         dataframes.append(content[0])
#         mass_set.update(content[1])

#     combined_df = combine_dataframes(dataframes, mass_set)
#     if combined_df is not None:
#         logger.info(f'Successfully combined {len(dataframes)} tsv files.')
#     return combined_df

# @app.command()
# def mergetsv(input_tsv_folder = Path('.'), output_tsv = Path('.')):
#     logger.info(f'Processing {input_tsv_folder}')
#     input_tsvs = sorted(Path(input_tsv_folder).glob('*.tsv'))

#     combined_df = combine_tsvs(input_tsvs)

#     logger.info(f'Output to {output_tsv}')
#     combined_df.to_csv(output_tsv, sep='\t', index=False, header=True)

if __name__ == '__main__':
    app()
