# vim: ts=4:sts=4:sw=4
#
# @date 2024-08-23
#
# This file is part of IDF converter, a set of tools to convert satellite,
# in-situ and numerical model data into Intermediary Data Format, making them
# compatible with the SEAScope application.
#
# Copyright (C) 2014-2024 OceanDataLab
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

import typing
import logging

import numpy
import numpy.typing
from scipy.ndimage import gaussian_filter

from idf_converter.lib.types import InputOptions, OutputOptions, Granule
from idf_converter.lib.types import FormatterResult

logger = logging.getLogger(__name__)


def compute_swot_roughness(input_opts: InputOptions,
                           output_opts: OutputOptions,
                           granule: Granule,
                           *args: typing.Iterable[typing.Any],
                           targets: typing.Sequence[str],
                           ) -> FormatterResult:
    """"""
    # Inputs
    sigma0 = granule.vars['sigma0']['array']
    sigma0_fill = granule.vars['sigma0']['_FillValue']
    sigma0_data = numpy.ma.getdata(sigma0)
    sigma0_mask = numpy.ma.getmaskarray(sigma0)

    sigp = sigma0_data + 2
    mask = (sigma0_mask | (sigma0_data < 10) | (sigma0_data > 40))
    sigp[numpy.where(mask)] = numpy.nan

    # Avoid runtime warning regarding mean computation on empty slices for
    # columns that contain only NaN values
    profil_mask = (numpy.isnan(sigp).all(axis=0))
    sigp[0, numpy.where(profil_mask)] = 1

    profil = numpy.nanmean(numpy.log(sigp),
                           axis=0)

    # Columns containing only NaN values should have a NoN profil
    profil[profil_mask] = numpy.nan

    # Log can be computed without warning only if sigma0 + 2 > 0
    # When sigma0 == 2, log = -inf
    # When sigma0 < -2, log = nan
    log_sigma0_2_ok_mask = ((~sigma0_mask)
                            & (sigma0_data > -2))
    log_sigma0_2 = numpy.log(sigma0_data + 2,
                             out=numpy.ones_like(sigma0_data,
                                                 dtype=numpy.float64),
                             where=log_sigma0_2_ok_mask)

    # Avoid divide by 0 errors where log_sigma0_2 is null, i.e. where sigma0
    # is -1
    log_sigma0_2_null_mask = (log_sigma0_2 == 0)
    log_sigma0_2[numpy.where(log_sigma0_2_null_mask)] = 1

    ssr = profil[numpy.newaxis, :] / log_sigma0_2

    # ssr should be infinite for pixels where log_sigma0_2 was 0
    ssr[numpy.where(log_sigma0_2_null_mask)] = numpy.inf

    # log_sigma0_2 should be -inf where sigma0 == -2, so ssr should be 0 for
    # these pixels
    ssr[numpy.where(sigma0_data == -2)] = 0

    # Mask where log_sigma0_2 is undefined, i.e. where sigma0 was masked and
    # where sigma0 < -2, as it leads to log(<0)
    ssr = numpy.ma.masked_where((sigma0_mask | (sigma0_data < -2)), ssr)

    granule.vars['roughness']['array'] = ssr
    granule.vars['roughness']['_FillValue'] = sigma0_fill

    return input_opts, output_opts, granule


def compute_swot_ssha_unedited_nolr(input_opts: InputOptions,
                                    output_opts: OutputOptions,
                                    granule: Granule,
                                    *args: typing.Iterable[typing.Any],
                                    targets: typing.Sequence[str],
                                    ) -> FormatterResult:
    """"""
    ssha_unedited = granule.vars['ssha_unedited']['array']
    ssha_unedited_fill = granule.vars['ssha_unedited']['_FillValue']
    ssha_unedited_data = numpy.ma.getdata(ssha_unedited)
    ssha_unedited_mask = numpy.ma.getmaskarray(ssha_unedited)

    vmask = (ssha_unedited_mask
             | (ssha_unedited_data == ssha_unedited_fill)
             | (numpy.abs(ssha_unedited_data) > 100))

    mask = (~vmask).astype(numpy.float32)
    ssha_unedited_data[numpy.where(vmask)] = 0

    gf = gaussian_filter(ssha_unedited_data * mask, sigma=10)

    gaussian_mask = gaussian_filter(mask, sigma=10)

    # Prevent divide by 0
    gaussian_mask_0 = (gaussian_mask == 0)
    gaussian_mask[numpy.where(gaussian_mask_0)] = 1
    gf /= gaussian_mask
    gf[numpy.where(gaussian_mask_0)] = 0

    nolr = ssha_unedited_data - gf
    nolr_mask = (vmask | (nolr > 40))
    nolr = numpy.ma.masked_where(nolr_mask, nolr)

    granule.vars['ssha_unedited_nolr']['array'] = nolr
    granule.vars['ssha_unedited_nolr']['_FillValue'] = ssha_unedited_fill

    return input_opts, output_opts, granule
