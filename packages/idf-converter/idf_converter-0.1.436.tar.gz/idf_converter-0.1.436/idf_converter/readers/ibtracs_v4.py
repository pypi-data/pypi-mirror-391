# vim: ts=4:sts=4:sw=4
#
# @date 2023-06-27
#
# This file is part of IDF converter, a set of tools to convert satellite,
# in-situ and numerical model data into Intermediary Data Format, making them
# compatible with the SEAScope application.
#
# Copyright (C) 2014-2022 OceanDataLab
#
# IDF converter is free software: you can redistribute it and/or modify it
# under the terms of the GNU Lesser General Public License as published by the
# Free Software Foundation, either version 3 of the License, or (at your
# option) any later version.
#
# IDF converter is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE. See the GNU Lesser General Public License for more
# details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with IDF converter. If not, see <https://www.gnu.org/licenses/>.

"""
"""

import os
import numpy
# import pyproj
import typing
import netCDF4
import logging
import datetime
import idf_converter.lib
import idf_converter.lib.geo
from idf_converter.lib.types import InputOptions, OutputOptions
from idf_converter.lib.types import ReaderResult, TransformsList

logger = logging.getLogger(__name__)

DATA_MODEL = 'time_dependent'
VARS_IN_KNOTS = ('wind',)
VARS_IN_MB = ('pres',)
VARS_IN_NM = ('r34_ne', 'r34_se', 'r34_sw', 'r34_nw', 'r50_ne', 'r50_se',
              'r50_sw', 'r50_nw', 'r64_ne', 'r64_se', 'r64_sw', 'r64_nw',
              'rmw')

VARS_BY_SOURCE: typing.Dict[str, typing.Dict[str, typing.Optional[str]]] = {
 'usa': {'lat': 'usa_lat',
         'lon': 'usa_lon',
         'wind': 'usa_wind',
         'pres': 'usa_pres',
         'r34': 'usa_r34',
         'r50': 'usa_r50',
         'r64': 'usa_r64',
         'rmw': 'usa_rmw'},
 'newdelhi': {'lat': 'newdelhi_lat',
              'lon': 'newdelhi_lon',
              'wind': 'newdelhi_wind',
              'pres': 'newdelhi_pres',
              'r34': None,
              'r50': None,
              'r64': None,
              'rmw': None},
 'bom': {'lat': 'bom_lat',
         'lon': 'bom_lon',
         'wind': 'bom_wind',
         'pres': 'bom_pres',
         'r34': 'bom_r34',
         'r50': 'bom_r50',
         'r64': 'bom_r64',
         'rmw': 'bom_rmw'},
 'reunion': {'lat': 'reunion_lat',
             'lon': 'reunion_lon',
             'wind': 'reunion_wind',
             'pres': 'reunion_pres',
             'r34': 'reunion_r34',
             'r50': 'reunion_r50',
             'r64': 'reunion_r64',
             'rmw': 'reunion_rmw'},
 'wellington': {'lat': 'wellington_lat',
                'lon': 'wellington_lon',
                'wind': 'wellington_wind',
                'pres': 'wellington_pres',
                'r34': None,
                'r50': None,
                'r64': None,
                'rmw': None},
 'tokyo': {'lat': 'tokyo_lat',
           'lon': 'tokyo_lon',
           'wind': 'tokyo_wind',
           'pres': 'tokyo_pres',
           'r34': None,
           'r50': None,
           'r64': None,
           'rmw': None},
 'kma': {'lat': 'kma_lat',
         'lon': 'kma_lon',
         'wind': 'kma_wind',
         'pres': 'kma_pres',
         'r34': None,
         'r50': None,
         'r64': None,
         'rmw': None},
 'hko': {'lat': 'hko_lat',
         'lon': 'hko_lon',
         'wind': 'hko_wind',
         'pres': 'hko_pres',
         'r34': None,
         'r50': None,
         'r64': None,
         'rmw': None},
 'mlc': {'lat': 'mlc_lat',
         'lon': 'mlc_lon',
         'wind': 'mlc_wind',
         'pres': 'mlc_pres',
         'r34': None,
         'r50': None,
         'r64': None,
         'rmw': None},
 'neumann': {'lat': 'neumann_lat',
             'lon': 'neumann_lon',
             'wind': 'neumann_wind',
             'pres': 'neumann_pres',
             'r34': None,
             'r50': None,
             'r64': None,
             'rmw': None},
 'td9635': {'lat': 'td9635_lat',
            'lon': 'td9635_lon',
            'wind': 'td9635_wind',
            'pres': 'td9635_pres',
            'r34': None,
            'r50': None,
            'r64': None,
            'rmw': None},
 'td9636': {'lat': 'td9636_lat',
            'lon': 'td9636_lon',
            'wind': 'td9636_wind',
            'pres': 'td9636_pres',
            'r34': None,
            'r50': None,
            'r64': None,
            'rmw': None},
 'ds824': {'lat': 'ds824_lat',
           'lon': 'ds824_lon',
           'wind': 'ds824_wind',
           'pres': 'ds824_pres',
           'r34': None,
           'r50': None,
           'r64': None,
           'rmw': None},
 'nadi': {'lat': 'nadi_lat',
          'lon': 'nadi_lon',
          'wind': 'nadi_wind',
          'pres': 'nadi_pres',
          'r34': None,
          'r50': None,
          'r64': None,
          'rmw': None},
 'cma': {'lat': 'cma_lat',
         'lon': 'cma_lon',
         'wind': 'cma_wind',
         'pres': 'cma_pres',
         'r34': None,
         'r50': None,
         'r64': None,
         'rmw': None},
 'wmo': {'lat': 'lat',
         'lon': 'lon',
         'wind': 'wmo_wind',
         'pres': 'wmo_pres',
         'r34': None,
         'r50': None,
         'r64': None,
         'rmw': None},
}


class InputPathMissing(ValueError):
    """Error raised when the input options have no "path" entry"""
    pass


class SourcesMissing(ValueError):
    """Error raised when the input option "sources" is specified but has an
    empty value."""
    pass


class UnsupportedSources(ValueError):
    """Error raised when the input option "sources" contains at least one
    value that is not supported by this reader."""
    def __init__(self, sources: typing.List[str]) -> None:
        """"""
        self.sources = sources


def help() -> typing.Tuple[str, str]:
    """Describe options supported by this reader.

    Returns
    -------
    str
        Description of the supported options
    """
    inp = ('    path\t\tPath of the input file',
           '    min_datetime\tDatetime in YYYY-mm-ddTHH:MM:SSZ format defining'
           ' the lower temporal bound for extracted storms, i.e. storms that'
           ' ended strictly before that datetime will be ignored',
           '    max_datetime\tDatetime in YYYY-mm-ddTHH:MM:SSZ format defining'
           ' the upper temporal bound for extracted storms, i.e. storms that'
           ' started strictly after that datetime will be ignored',
           '    sources\t\tComma-separated list of sources to consider when'
           ' extracting granules from the input file.\n'
           '    \t\t\tSupported sources are (all are selected by default): '
           f'{", ".join([_ for _ in VARS_BY_SOURCE.keys()])}')
    out = ('',)
    return ('\n'.join(inp), '\n'.join(out))


def get_nc_var_and_slices(var_id: str,
                          varnames: typing.Dict[str, typing.Optional[str]],
                          storm_slices: typing.List[slice]
                          ) -> typing.Tuple[typing.Optional[str],
                                            typing.List[slice]]:
    slices = list(storm_slices)

    # see https://groups.google.com/g/ibtracs-qa/c/J0wXCeE5PC0/m/5d2BSykyDQAJ
    if var_id.endswith('_ne'):
        slices.append(slice(0, 1, 1))
        nc_var = varnames.get(var_id[:-3])
    elif var_id.endswith('_se'):
        slices.append(slice(1, 2, 1))
        nc_var = varnames.get(var_id[:-3])
    elif var_id.endswith('_sw'):
        slices.append(slice(2, 3, 1))
        nc_var = varnames.get(var_id[:-3])
    elif var_id.endswith('_nw'):
        slices.append(slice(3, 4, 1))
        nc_var = varnames.get(var_id[:-3])
    else:
        nc_var = varnames.get(var_id)

    return nc_var, slices


def get_storm_data(f_handler: netCDF4.Dataset,
                   storm_index: int,
                   output_opts: OutputOptions,
                   time_full: numpy.typing.NDArray[numpy.float64],
                   time_units: str,
                   sources: typing.List[str],
                   ) -> typing.Any:
    """"""
    storm_id_chars = f_handler.variables['sid'][storm_index, :]
    storm_id = netCDF4.chartostring(storm_id_chars)

    storm_slice = slice(storm_index, storm_index + 1, 1)

    # Compute indices within valid time range
    time_full_mask = numpy.ma.getmaskarray(time_full)
    _time_ind = numpy.where(~time_full_mask)
    date_min_index = _time_ind[0].min()
    date_max_index = _time_ind[0].max()
    datetime_slice = slice(date_min_index, date_max_index + 1, 1)

    storm_slices = [storm_slice, datetime_slice]

    # Only keep valid time values
    _time = numpy.ma.getdata(time_full[datetime_slice])
    _time_mask = numpy.ma.getmaskarray(_time)
    if _time_mask.any():
        logger.warning(f'Masked times in {storm_id}')

    _storm_name = f_handler.variables['name'][storm_index, :]
    storm_name = netCDF4.chartostring(_storm_name)

    # extract a single ATCF identifier for the storm
    _storm_atcf_id = f_handler.variables['usa_atcf_id'][storm_index, :, :]
    _storm_atcf_id = netCDF4.chartostring(_storm_atcf_id)

    non_empty_ind = numpy.where(_storm_atcf_id != '')
    _storm_atcf_id = numpy.unique(_storm_atcf_id[non_empty_ind])
    storm_atcf_id = None
    if 0 < _storm_atcf_id.size:
        storm_atcf_id = _storm_atcf_id[0]
        if 1 < _storm_atcf_id.size:
            logger.warning(f'Several ATCF IDs for {storm_id}, only the first '
                           f'one will be saved: {", ".join(_storm_atcf_id)}')

    for source in sources:
        varnames = VARS_BY_SOURCE.get(source, None)
        if varnames is None:
            logger.warning(f'Source "{source}" not supported')
            continue

        lat_var = varnames.get('lat')
        lon_var = varnames.get('lon')

        _lon = idf_converter.lib.extract_variable_values(f_handler, lon_var,
                                                         idx=storm_slices)[0]
        _lat = idf_converter.lib.extract_variable_values(f_handler, lat_var,
                                                         idx=storm_slices)[0]

        _lon_mask = numpy.ma.getmaskarray(_lon)
        _lat_mask = numpy.ma.getmaskarray(_lat)
        coords_mask = (_time_mask | _lon_mask | _lat_mask)
        if coords_mask.all():
            continue

        valid_ind = numpy.where(~coords_mask)

        storm_lon = _lon[valid_ind]
        storm_lat = _lat[valid_ind]
        _t = _time[valid_ind]

        # Convert to seconds since 1970-01-01T00:00:00Z, as expected by IDF
        _dt = netCDF4.num2date(_t, time_units)
        storm_time: numpy.typing.NDArray[numpy.float64]
        storm_time = netCDF4.date2num(_dt,
                                      'seconds since 1970-01-01T00:00:00Z')

        # Longitude continuity fix (required for distance computation later on)
        lon0 = numpy.mean(storm_lon)
        mod_lon, _ = idf_converter.lib._safe_mod_angle(storm_lon - lon0, 360,
                                                       9)
        storm_lon = lon0 + mod_lon
        storm_lon[numpy.where(storm_lon > lon0 + 180)] -= 360
        storm_lon[numpy.where(storm_lon < lon0 - 180)] += 360

        idf_version = output_opts.get('idf_version', '1.0')
        granule = idf_converter.lib.create_granule(idf_version, DATA_MODEL)
        granule.vars = {'wind': {'name': 'wind',
                                 'options': {}},
                        'pres': {'name': 'pressure',
                                 'options': {}},
                        'r34_ne': {'name': 'r34_ne',
                                   'options': {}},
                        'r34_se': {'name': 'r34_se',
                                   'options': {}},
                        'r34_sw': {'name': 'r34_sw',
                                   'options': {}},
                        'r34_nw': {'name': 'r34_nw',
                                   'options': {}},
                        'r50_ne': {'name': 'r50_ne',
                                   'options': {}},
                        'r50_se': {'name': 'r50_se',
                                   'options': {}},
                        'r50_sw': {'name': 'r50_sw',
                                   'options': {}},
                        'r50_nw': {'name': 'r50_nw',
                                   'options': {}},
                        'r64_ne': {'name': 'r64_ne',
                                   'options': {}},
                        'r64_se': {'name': 'r64_se',
                                   'options': {}},
                        'r64_sw': {'name': 'r64_sw',
                                   'options': {}},
                        'r64_nw': {'name': 'r64_nw',
                                   'options': {}},
                        'rmw': {'name': 'rmax',
                                'options': {}}
                        }

        # Extract data variables
        storm_data = {}
        for var_id in granule.vars.keys():
            nc_var, slices = get_nc_var_and_slices(var_id, varnames,
                                                   storm_slices)

            if nc_var is None:
                band = numpy.full(numpy.shape(storm_lat), numpy.nan)
            else:
                idf_converter.lib.extract_variable_attributes(f_handler,
                                                              nc_var,
                                                              granule,
                                                              var_id)
                _band = idf_converter.lib.extract_variable_values(f_handler,
                                                                  nc_var,
                                                                  idx=slices)
                band = numpy.reshape(_band, (_band.size,))[valid_ind]
            storm_data[var_id] = band

        storm_granule = idf_converter.lib.create_granule(idf_version,
                                                         DATA_MODEL)
        for var_id in granule.vars.keys():
            storm_granule.vars[var_id] = {'options': {}}

            # Copy attributes from the "main" granule object
            for attr_name, attr_value in granule.vars[var_id].items():
                if 'array' == attr_name:
                    continue
                storm_granule.vars[var_id][attr_name] = attr_value

            band = storm_data[var_id].astype(numpy.float32)
            if numpy.isnan(band).all():
                vmin = storm_granule.vars[var_id].get('valid_min', 0)
                vmax = storm_granule.vars[var_id].get('valid_max', 1)
            else:
                vmin = numpy.nanmin(band)
                vmax = numpy.nanmax(band)

            # 1 knot = 1 international nautical mile per hour
            if var_id in VARS_IN_KNOTS:
                band = band * numpy.float64(1852.0 / 3600.0)
                storm_granule.vars[var_id]['units'] = 'm.s-1'
                storm_granule.vars[var_id]['valid_min'] = vmin * 1852 / 3600
                storm_granule.vars[var_id]['valid_max'] = vmax * 1852 / 3600

            # 1 international nautical mile = 1852 meters
            if var_id in VARS_IN_NM:
                band = band * 1852
                storm_granule.vars[var_id]['units'] = 'm'
                storm_granule.vars[var_id]['valid_min'] = vmin * 1852
                storm_granule.vars[var_id]['valid_max'] = vmax * 1852

            # 1 millibar = 100 Pa
            if var_id in VARS_IN_MB:
                band = band * 100
                storm_granule.vars[var_id]['units'] = 'Pa'
                storm_granule.vars[var_id]['valid_min'] = vmin * 100
                storm_granule.vars[var_id]['valid_max'] = vmax * 100

            storm_granule.vars[var_id]['array'] = band
            storm_granule.vars[var_id]['datatype'] = band.dtype

        # Locate gaps and introduce dummy coordinates immediately after the
        # last known coordinate and immediately before the next one so that the
        # lack of information can be represented (IBTrACS data should 3-hourly)
        time_diff = storm_time[1:] - storm_time[:-1]
        gap_ind = numpy.where(time_diff > 3 * 3600)[0]
        if gap_ind.any():
            for index in sorted(gap_ind, reverse=True):
                storm_lon = numpy.insert(storm_lon,
                                         index + 1, storm_lon[index + 1])
                storm_lon = numpy.insert(storm_lon,
                                         index + 1, storm_lon[index])
                storm_lat = numpy.insert(storm_lat,
                                         index + 1, storm_lat[index + 1])
                storm_lat = numpy.insert(storm_lat,
                                         index + 1, storm_lat[index])
                storm_time = numpy.insert(storm_time,
                                          index + 1, storm_time[index + 1] - 1)
                storm_time = numpy.insert(storm_time,
                                          index + 1, storm_time[index] + 1)
                for var_id in granule.vars.keys():
                    original_data = storm_granule.vars[var_id]['array']
                    original_data = numpy.insert(original_data,
                                                 index + 1, numpy.nan)
                    original_data = numpy.insert(original_data,
                                                 index + 1, numpy.nan)
                    storm_granule.vars[var_id]['array'] = original_data

        # Add coordinates variables
        storm_granule.vars['lat'] = {'units': 'degrees north',
                                     'array': storm_lat,
                                     'datatype': storm_lat.dtype,
                                     'options': {}}
        storm_granule.vars['lon'] = {'units': 'degrees east',
                                     'array': storm_lon,
                                     'datatype': storm_lon.dtype,
                                     'options': {}}

        out_time_units = 'seconds since 1970-01-01T00:00:00.000Z'
        storm_granule.vars['time'] = {'units': out_time_units,
                                      'array': storm_time,
                                      'datatype': numpy.double,
                                      'options': {}}

        # Set Global parameters
        spatial_res_meters = 1.e07
        storm_granule.meta['idf_subsampling_factor'] = 0
        storm_granule.meta['idf_spatial_resolution'] = spatial_res_meters
        storm_granule.meta['idf_spatial_resolution_units'] = 'm'

        if storm_atcf_id is not None:
            storm_granule.meta['atcf_id'] = storm_atcf_id
        storm_granule.meta['storm_name'] = storm_name
        storm_granule.meta['storm_id'] = storm_id
        storm_granule.meta['storm_track_source'] = source

        start_dt = datetime.datetime.utcfromtimestamp(storm_time[0])
        stop_dt = datetime.datetime.utcfromtimestamp(storm_time[-1])
        storm_granule.meta['time_coverage_start'] = start_dt
        storm_granule.meta['time_coverage_end'] = stop_dt

        yield storm_granule


def read_data(input_opts: InputOptions,
              output_opts: OutputOptions
              ) -> typing.Iterator[ReaderResult]:
    """Read input file, extract data and metadata, store them in a Granule
    object then prepare formatting instructions to finalize the conversion to
    IDF format.

    Parameters
    ----------
    input_opts: dict
        Options and information related to input data
    output_opts: dict
        Options and information related to formatting and serialization to IDF
        format

    Returns
    -------
    tuple(dict, dict, idf_converter.lib.Granule, list)
        A tuple which contains four elements:

        - the input_options :obj:dict passed to this method

        - the output_options :obj:dict passed to this method

        - the :obj:`idf_converter.lib.Granule` where the extracted information
          has been stored

        - a :obj:list of :obj:dict describing the formatting operations that
          the converter must perform before serializing the result in IDF
          format
    """
    channels = ['wind', 'pres', 'r34_ne', 'r34_se', 'r34_sw', 'r34_nw',
                'r50_ne', 'r50_se', 'r50_sw',  'r50_nw', 'r64_ne', 'r64_se',
                'r64_sw', 'r64_nw', 'rmw',]

    _input_path = input_opts.get('path', None)
    if _input_path is None:
        raise InputPathMissing()
    input_path = os.path.normpath(_input_path)
    granule_name = os.path.splitext(os.path.basename(input_path))[0]

    _dt_user_min = input_opts.get('min_datetime', None)
    dt_user_min: typing.Optional[datetime.datetime] = None
    if _dt_user_min is not None:
        dt_user_min = datetime.datetime.strptime(_dt_user_min,
                                                 '%Y-%m-%dT%H:%M:%SZ')

    _dt_user_max = input_opts.get('max_datetime', None)
    dt_user_max: typing.Optional[datetime.datetime] = None
    if _dt_user_max is not None:
        dt_user_max = datetime.datetime.strptime(_dt_user_max,
                                                 '%Y-%m-%dT%H:%M:%SZ')

    _sources = input_opts.get('sources', None)
    sources: typing.List[str]
    if _sources is None:
        sources = list(VARS_BY_SOURCE.keys())
    else:
        _sources = [_.strip() for _ in _sources.split(',')
                    if 0 < len(_.strip())]
        if 0 >= len(_sources):
            logger.error('The "sources" input option is empty, either remove '
                         'this option (all supported sources will be selected '
                         'by default), or set its value as a comma-separated '
                         'list of supported sources '
                         f'({", ".join([_ for _ in VARS_BY_SOURCE.keys()])})')
            raise SourcesMissing()
        sources = [_ for _ in _sources if _ in VARS_BY_SOURCE.keys()]
        if len(sources) < len(_sources):
            unknown_sources = [_ for _ in _sources
                               if _ not in VARS_BY_SOURCE.keys()]
            if 0 < len(unknown_sources):
                logger.error('The following values are not supported by the '
                             '"sources" input option: '
                             f'{", ".join(unknown_sources)}\n'
                             'Please use only supported values: '
                             f'{", ".join([_ for _ in VARS_BY_SOURCE.keys()])}'
                             )
                raise UnsupportedSources(unknown_sources)

    f_handler = netCDF4.Dataset(input_path, 'r')
    get_values = idf_converter.lib.extract_variable_values
    time_units = f_handler.variables['time'].units
    time_full = get_values(f_handler, 'time')

    time_mask = numpy.full(time_full.shape, numpy.False_, dtype=bool)

    if dt_user_min is not None:
        time_user_min = netCDF4.date2num(dt_user_min, time_units)
        time_mask = (time_mask | (time_full < time_user_min))

    if dt_user_max is not None:
        time_user_max = netCDF4.date2num(dt_user_max, time_units)
        time_mask = (time_mask | (time_full > time_user_max))

    rows_mask = numpy.logical_and.reduce(time_mask, axis=1)
    storm_indices = numpy.where(~rows_mask)[0]

    for i in storm_indices:
        for storm_granule in get_storm_data(f_handler, i, output_opts,
                                            time_full[i], time_units, sources):
            if storm_granule is None:
                continue

            storm_id = storm_granule.meta['storm_id']
            storm_name = storm_granule.meta['storm_name']
            _source = storm_granule.meta['storm_track_source']
            if storm_name not in ('', 'NOT NAMED', 'NOT_NAMED'):
                _granule_name = f'{storm_id}_{storm_name}_{granule_name}'
            else:
                _granule_name = f'{storm_id}_{granule_name}'
            storm_granule.meta['idf_granule_id'] = f'{_granule_name}_{_source}'

            transforms: TransformsList = []

            transforms.append(('remove_extra_lon_degrees',
                               {'lon_name': 'lon'}))

            output_opts['__export'] = channels

            # data_model, dims, vars, attrs, formatter_jobs
            yield (input_opts, output_opts, storm_granule, transforms)
    f_handler.close()
