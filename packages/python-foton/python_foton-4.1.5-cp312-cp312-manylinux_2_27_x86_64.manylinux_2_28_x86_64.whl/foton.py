"""Provides access to foton IIR filters and filter files

The two main interfaces are the FilterFile class for parsing foton filter files,
and the FilterDesign class for constructing and editing filter designs. See
below for some common use cases.

Examples:
    Look up a filter using a channel prefix:
    >>> matches = find_filter('X1:LSC-CARM')
    >>> matches
    [('/opt/rtcds/tst/x1/chans/X1OMC.txt', 'LSC_CARM')]
    >>> filepath, fmname = matches[0]

    Examine a filter design from a foton file:
    >>> ff = FilterFile(filepath)
    >>> ff[fmname]  # show filter module contents
    <Module [<Section 0 '4:0'>, <Section 5 'Comb60'>]>
    >>> ff[fmname][0].design  # filter section 0 corresponds to FM1 in medm
    'zpk([4],[0],4,"n")'

    Read zero-pole-gain values or SOS coefficients from a foton file:
    >>> ff = FilterFile('X1LSC.txt')
    >>> mich_fm1 = ff['LSC_MICH'][0]
    >>> mich_fm1.get_zpk(plane='n')
    (array([4.+0.j]), array([0.+0.j]), 3.9999999999994653)
    >>> sos = mich_fm1.get_sos()  # SOS coef array in scipy.signal format

    Compute time-domain and frequency-domain responses:
    >>> filt = Filter(mich_fm1)  # initialize a time-domain filter
    >>> filt.apply([1]+[0]*16383)  # get an impulse response
    array([1.00076679, 0.00153398, 0.00153398, ..., 0.00153398, 0.00153398,
           0.00153398])    
    >>> freq = np.logspace(-1, 3, 1000)
    >>> tf = mich_fm1.freqresp(freq)

    Write a new design using foton's filter languge:
    >>> mich_fm1.design = 'zpk([5],[0],4,"n")'
    >>> mich_fm1.output_switch = 'Ramp'
    >>> mich_fm1.ramp = 1  # configure filter switching and ramp time
    >>> mich_fm1.name = '5:0'  # update name string in medm
    >>> ff.write()

    Write a new design using FilterDesign methods:
    >>> mich_fm1.set_zpk([5], [0], 4, plane='n')
    >>> mich_fm1.design
    'zpk([4.999999999999504],[0],3.999999999999602,"n")'
    >>> ff.write()

    Duplicate a filter section:
    >>> for coil in ['LL', 'LR', 'UR']:
    ...     ff['BS_M2_COILOUTF_' + coil][0].copyfrom(ff['BS_M2_COILOUTF_UL'][0])
    ...
"""

import sys
import os
import os.path
import re
import glob
import collections.abc
import functools
import warnings
import logging
log = logging.getLogger(__name__)

import array
import numpy as np
import scipy.signal as signal

import ctypes

import pydmtsigp as dmtsigp
import pyfilterfile as filterfile


__version__ = '3.0'
__all__ = ['find_filter', 'FilterFile', 'Module', 'Section', 'FilterDesign', 'Filter']


def find_filter(chan, chans_path=None):
    """Searches through filter files to find a match for a channel prefix

    Example:
        >>> find_filter('X1:SUS-BS_M2_LOCK_L')  # standard naming scheme
        [('/opt/rtcds/tst/x1/chans/X1SUSBS.txt', 'BS_M2_LOCK_L')]
        >>> find_filter('X1:LSC-CARM')  # 'top_names' can be less obvious
        [('/opt/rtcds/tst/x1/chans/X1OMC.txt', 'LSC_CARM')]

    Args:
        chan: FM channel prefix (any suffix such as '_GAIN' must be removed)
        chans_path: path to directory containing filter files

    chans_path must also hold a daq subdirectory with the DAQ .ini files, which
    are used to help track down the filter file associated with chan.

    If chans_path is not given, ifo will be parsed from chan, and chans_path
    will be guessed as the first match for '/opt/rtcds/*/ifo/chans'.

    Returns:
        list of tuples (filter file path, filter module name)

    If no matching filter module is found, an empty list will be returned.
    Multiple matches may be returned in some situations, for example if
    chans_path is cluttered with backup copies or other spurious files. Users
    of this function should be careful to check for both of these conditions.
    """
    def pygrep(fileglob, pattern):
        matches = []
        pattern = re.compile(pattern)
        for filename in glob.iglob(fileglob):
            # checks for broken symbolic links
            if os.path.exists(filename):
                with open(filename, 'r') as f:
                    try:
                        if pattern.search(f.read()):
                            matches.append(filename)
                            continue
                    except UnicodeDecodeError:
                        continue
            return matches

    def ini_to_filterfile(filename):
        return os.path.splitext(os.path.basename(filename))[0] + '.txt'

    # Split off the IFO and the top level system
    # X1:LSC-CARM -> fm_ifo=X1, fm_sys=LSC, fm_partname=CARM
    try:
        fm_ifo, fm_split = chan.split(':', 1)
    except ValueError:
        fm_ifo = chan
        fm_split = ''
    try:
        fm_sys, fm_partname = fm_split.split('-', 1)
    except ValueError:
        fm_sys = fm_split
        fm_partname = ''

    # Guess chans_path if necessary
    if not chans_path:
        ifo = fm_ifo.lower()
        chans_paths = list(glob.iglob('/opt/rtcds/*/{}/chans'.format(ifo)))
        if chans_paths:
            chans_path = chans_paths[0]
        else:
            raise Exception('failed to guess chans_path')

    # Grep for the FM's excitation channel in the DAQ .ini files to track down
    # what the corresponding filter file is.  This provides a consistency check
    # in case of spurious files in the filter file directory.
    excpat = r'\[{}_EXCMON\]'.format(chan)
    iniglob = chans_path + '/daq/' + '*.ini'
    inifiles = pygrep(iniglob, excpat)
    filterfile_candidates = [ini_to_filterfile(filename) for filename in inifiles]

    matches = []
    for filename in filterfile_candidates:
        filepath = '{}/{}'.format(chans_path, filename)
        fmpat = r'\b{}\b'
        # try standard naming scheme
        if filename.startswith(fm_ifo + fm_sys):
            fm_name = fm_partname
            if pygrep(filepath, fmpat.format(fm_name)):
                matches += [(filepath, fm_name)]
                continue
        # try 'top_names'
        fm_name = '{}_{}'.format(fm_sys, fm_partname)
        if pygrep(filepath, fmpat.format(fm_name)):
            matches += [(filepath, fm_name)]
            continue

    return matches


class FilterFile(collections.abc.MutableMapping):
    """Reads and edits foton file data

    A FilterFile object contains a collection of named modules (each of which
    contains up to ten sections).  Modules are accessed by name, and sections
    are accessed by index (0-9).

    Args:
        filename: foton file to read
    """
    def __init__(self, filename=None, create_if_not_exist=True, read_only=False):
        self.ff = filterfile.FilterFile()
        self.filename = filename
        self.create_if_not_exist = create_if_not_exist
        self.read_only = read_only
        if filename:
            self.read(filename)

    def __getitem__(self, key):
        lookup = lambda: self.ff.find(key)
        # The subtlety here is that find() returns a C pointer that
        # can be invalidated when modules are added or removed -- so a
        # 'Module' needs to carry around this lookup function to
        # retrieve a valid pointer.
        try:
            item = lookup()
        except:
            raise KeyError(key)
        if item is None:
            raise KeyError(key)

        # must test item == None (null pointer), not item is None
        if item is None:
            raise KeyError(key)
        return Module(lookup)

    def __setitem__(self, key, val):
        if not isinstance(val, Module):
            raise ValueError(val)
        self.ff.add(key, val.rate)
        for sec in val:
            self[key][sec.index] = sec

    def __delitem__(self, key):
        self.ff.remove(key)

    def __iter__(self):
        for fm in self.ff.modules():
            yield fm.getName()

    def __len__(self):
        return len(self.ff.modules())

    def refresh(self):
        """Updates all sections of all modules

        Note that the update may not be complete if one or more sections fail.

        Returns:
            True if successful
        """
        # rename update as refresh so it's not confused with dict's update method
        return self.ff.update()

    def valid(self):
        """Checks if filters are valid

        Returns:
            True if all filters are valid
        """
        val = True
        for name, fm in self.items():
            for sec in fm:
                if not sec.valid():
                    val = False
                    log.warning('{}[{}] invalid'.format(name, sec.index))
        return val

    def read(self, filename):
        """Reads filter file

        Args:
            filename: foton file to read

        Returns:
            True if successful
        """
        self.filename = os.path.abspath(filename)
        if (not self.create_if_not_exist) and (not os.path.exists(self.filename)):
            raise OSError(f"Could not read filter file '{self.filename}'.  'create_if_not_exist' was false and the file did not exist.")
        if self.read_only and (not os.path.exists(self.filename)):
            raise OSError(f"Could not read filter file '{self.filename}', but 'read_only' flag was set to True.")
        return self.ff.read_file(self.filename)

    def write_file(self, *args):
        if self.read_only:
            raise OSError("FilterFile object set to read-only")
        if (not self.create_if_not_exist) and len(args) >= 1 and isinstance(args[0], str) and (not os.path.exists(args[0])):
            raise OSError(f"Could not write to filter file '{args[0]}'.  'create_if_not_exist' was false and the file did not exist.")
        self.ff.write_file(*args)

    def write_string(self):
        return self.ff.write_string()

    def write(self, *args):
        """Writes filter file

        Returns:
            True if successful
        """
        if not self.filename:
            raise Exception("undefined filename")
        if not (self.valid() and self.refresh() and self.valid()):
            raise Exception("invalid filters")
        if len(args) == 0:
            if self.read_only:
                raise OSError("FilterFile object set to read-only")
            if (not self.create_if_not_exist) and (not os.path.exists(self.filename)):
                raise OSError(f"Could not write to filter file '{self.filename}'.  'create_if_not_exist' was false and the file did not exist.")
            return self.ff.write_file(self.filename)
        else:
            # handle any code that relies on direct use of C++
            # overloads: (fname) for writing a file,
            # $ (fname, errmsg) for passing custom error message
            # (buffer, bufferlen) for writing to a buffer
            if len(args) == 1 or (len(args)==2 and isinstance(args[1], str)):
                fname = args[len(args)-1]
                if self.read_only:
                    raise OSError("FilterFile object set to read-only")
                if (not self.create_if_not_exist) and (not os.path.exists(fname)):
                    raise OSError(f"Could not write to filter file '{fname}'.  'create_if_not_exist' was false and the file did not exist.")
                return self.ff.write_file(*args)
            elif isinstance(args[1], int):
                filtercontent = self.ff.write_string()
                if isinstance(args[0], ctypes.Array):
                    args[0].from_buffer_copy(filtercontent)
                else:
                    raise BufferError("buffer was not a recognized type. Must be ctypes.Array")
                return len(filtercontent)

    def __repr__(self):
        return "<{} {} {}>".format(
            self.__class__.__name__,
            repr(self.filename),
            repr([k for k in self.keys()]),
        )


class Module(collections.abc.MutableSequence):
    """Reads and edits foton file data for a filter module

    A Module object contains ten filter sections, which are accessed by index
    (0-9).
    """
    def __init__(self, lookup):
        self._lookup = lookup

    @property
    def fm(self):
        return self._lookup()

    @property
    def name(self):
        """Module name"""
        return self.fm.getName()

    @name.setter
    def name(self, val):
        self.fm.setName(val)

    @property
    def rate(self):
        """Sample rate (Hz)"""
        return self.fm.getFSample()

    @rate.setter
    def rate(self, val):
        self.fm.setFSample(val)

    def __getitem__(self, n):
        if n in range(len(self)):
            return Section(self._lookup, n)
        else:
            raise IndexError(n)

    def __setitem__(self, n, val):
        self[n].copyfrom(val)

    def __delitem__(self, n):
        raise Exception('filter sections cannot be deleted')

    def insert(self, n, val):
        raise Exception('filter sections cannot be inserted')

    def __len__(self):
        return filterfile.kMaxFilterSections

    def find_name(self, name):
        """Returns a list of filter sections that have the requested name
        
        Section names are not required to be unique, so it is possible to have
        zero, one, or multiple sections in the returned list.
        """
        return [sec for sec in self if sec.name == name]

    def __repr__(self):
        return '<{} {}>'.format(
            self.__class__.__name__,
            repr([sec for sec in self if not sec.is_empty]),
        )


class FilterDesign:
    """Designs IIR (infinite impulse response) filters

    Args:
        design: filter design string (or dmtsigp.FilterDesign object)
        rate: sample rate (Hz)

    FilterDesign is not a filter class by itself, but rather a "factory" class
    that produces filters based on a user specification.

    Any number of filters can be added in series. Filters can be designed by
    calling their corresponding creation methods (such as ellip), or by parsing
    a string formula.

    FilterDesign supports a configuration line parser which follows the matlab
    syntax. This way a filter can be written by a product of designer functions.
    For example, 'zpk([100;100],[1;1],1,"n") /. setgain(0, 10)' represents a
    filter consisting of two poles at 100 Hz, two zeros at 1 Hz, and a dc gain
    of 10. For a list of supported designer functions, see below.

    FilterDesign can also calculate the frequency response. Filters can be
    simulated using the Filter class to obtain their time-domain response to
    any signal (such as impulse response or step response).

    By default the filter design class will return a unity gain filter
    (identity operator), if no filter has been added.

    The filter types are: "LowPass" for low pass, "HighPass" for high pass,
    "BandPass" for band pass and "BandStop" for a band stop filter.

    FILTER FORMULA SPECIFICATION
    Filter formulas are written as a product of real numbers and designer
    functions. Optionally one can add a gain condition at the end. Designer
    functions are of the form "f(a1,a2,...aN)" where "f" must be a supported
    function and "a1", .. "aN" must be the corresponding arguments. A complex
    number argument is written as "real+i*imag" or "real+imag*i". Number
    arguments must be constants and expressions are not allowed. A vector of
    numbers is written as "[e1;e2;...eN]". The gain condition is introduced by
    the "/." symbol and it must be followed by the "setgain(f,g)" where g is
    the desired gain and f is the frequency at which it should be true. The
    multiplication operator "*" is optional and can be omitted or replaced by a
    space.

    Examples:
        Make an elliptic high pass filter:
        >>> fd = FilterDesign(rate=16384)  # specify sampling frequency
        >>> fd.ellip('LowPass', 8, 1, 60, 100)  # make elliptic low pass

        Make a whitening filter with a resonant gain and obtain its frequency
        response:
        >>> fd = FilterDesign(design='zpk([1;1],[100;100],1,"n")*resgain(12,30)', rate=16384)  # specify filter string and sampling frequency
        >>> fd.freqresp(np.logspace(-1, 3, 1000))  # get frequency response

        Read DARM filter from online system and add a 60Hz comb:
        >>> ff = FilterFile('X1LSC.txt')
        >>> fd = ff['LSC_DARM'][0].get_filterdesign()
        >>> fd.notch(60, 100)  # add Q=100 notch
        >>> ff['LSC_DARM'][0].set_filterdesign(fd)

        Numerical design data in zpk, rpoly, sos, zroots, or direct format
        can be read, written, and converted between formats:
        >>> fd = FilterDesign(rate=16384)
        >>> zeros = [4, 40]
        >>> poles = [0, 10]
        >>> gain = 1
        >>> fd.set_zpk(zeros, poles, gain, plane='n')
        >>> fd.get_sos()
        array([[ 0.06290589, -0.12475772,  0.0618533 ,  1.        , -1.99617238,
                 0.99617238]])
    """
    def __init__(self, design='', rate=None):
        if isinstance(design, str):
            # generate dmtsigp.FilterDesign from design string
            # sample rate must be provided
            if rate is None:
                raise Exception("sample rate must be given")
            self.filt = dmtsigp.FilterDesign(design, rate)
        else:
            # design is already a FilterDesign or dmtsigp.FilterDesign
            # make a copy to avoid modifying the original
            if hasattr(design, 'filt'):
                self.filt = dmtsigp.FilterDesign(design.filt)
            else:
                self.filt = dmtsigp.FilterDesign(design)

    @property
    def name(self):
        """Filter name"""
        return self.filt.getName()

    @name.setter
    def name(self, val):
        self.filt.setName(val)

    @property
    def design(self):
        """Design string"""
        return self.filt.getFilterSpec()

    @design.setter
    def design(self, val):
        self.reset()
        self.add(val)

    @property
    def string(self):
        """DEPRECATED: use FilterDesign.design instead"""
        warnings.warn('FilterDesign.string is deprecated: use FilterDesign.design instead', DeprecationWarning)
        return self.design

    @string.setter
    def string(self, val):
        """DEPRECATED: use FilterDesign.design instead"""
        warnings.warn('FilterDesign.string is deprecated: use FilterDesign.design instead', DeprecationWarning)
        self.design = val

    @property
    def rate(self):
        """Sample rate (Hz)"""
        return self.filt.getFSample()

    @rate.setter
    def rate(self, val):
        """Sets the sample rate and resets the filter"""
        self.filt.setFSample(val)

    @property
    def prewarp(self):
        """Prewarping flag"""
        return self.filt.getPrewarp()

    @prewarp.setter
    def prewarp(self, val):
        self.filt.setPrewarp(val)

    @property
    def soscount(self):
        """Number of second order sections"""
        return dmtsigp.iirsoscount(self.filt.get())

    @property
    def polecount(self):
        """Number of poles"""
        return dmtsigp.iirpolecount(self.filt.get())

    @property
    def zerocount(self):
        """Number of zeros"""
        return dmtsigp.iirzerocount(self.filt.get())

    @property
    def polezerocount(self):
        """Number of poles and zeros"""
        return dmtsigp.iirpolezerocount(self.filt.get())

    @property
    def order(self):
        """Filter order"""
        return dmtsigp.iirorder(self.filt.get())

    @property
    def is_unity(self):
        """True if filter is unity gain"""
        return self.filt.isUnityGain()

    def cmp(self, f2):
        """Returns true if filter f2 is equal to this one (same coeffs)"""
        return dmtsigp.iircmp(self.filt.get(), f2.filt.get())

    def reset(self):
        """Resets the filter to identity"""
        self.filt.reset()

    def add(self, formula):
        """Adds a filter from a design string

        Args:
            formula: design string

        Returns True if successful
        """
        return self.filt.filter(formula)

    def gain(self, g, format='scalar'):
        """Multiplies the filter by the specified gain

        Args:
            g: gain
            format: 'scalar' or 'dB'

        Returns True if successful
        """
        return self.filt.gain(g, format)

    def pole(self, f, gain, plane='s'):
        """Adds a pole

        Poles and zeros can be specified in the s-plane using units of rad/s
        (set plane to "s") or units of Hz ("f"). In both cases the frequency is
        expected to be POSITIVE. Alternatively, one can also specify normalized
        poles and zeros ("n"). Normalized poles and zeros are expected to have
        POSITIVE frequencies, and their respective low and high frequency gains
        are set to 1, unless they are located at 0 Hz.

        For the s-plane the formula is:
            pole(f0) = 1/(s + w0) ["s"] or
            pole(f0) = 1/(s + 2 pi f0) ["f"].
        For a normalized pole ["n"] the formula is:
            pole(f0) = 1/(1 + i f/f0); f0 > 0 and
            pole(f0) = 1/(i f); f0 = 0.

        Args:
            f: pole frequency
            gain: gain
            plane: location where poles/zeros are specified

        Returns True if successful
        """
        return self.filt.pole(f, gain, plane)

    def zero(self, f, gain, plane='s'):
        """Adds a zero

        Poles and zeros can be specified in the s-plane using units of rad/s
        (set plane to "s") or units of Hz ("f"). In both cases the frequency is
        expected to be POSITIVE. Alternatively, one can also specify normalized
        poles and zeros ("n"). Normalized poles and zeros are expected to have
        POSITIVE frequencies, and their respective low and high frequency gains
        are set to 1, unless they are located at 0 Hz.

        For the s-plane the formula is:
            zero(f0) = (s + w0) ["s"] or
            zero(f0) = (s + 2 pi f0) ["f"].
        For a normalized zero ["n"] the formula is:
            zero(f0) = (1 + i f/f0); f0 > 0 and
            zero(f0) = (i f); f0 = 0.

        Args:
            f: zero frequency
            gain: gain
            plane: location where poles/zeros are specified

        Returns True if successful
        """
        return self.filt.zero(f, gain, plane)

    def pole2(self, f, Q, gain, plane='s'):
        """Adds a complex pole pair
        
        Poles and zeros can be specified in the s-plane using units of rad/s
        (set plane to "s") or units of Hz ("f"). In both cases the frequency is
        expected to be POSITIVE. Alternatively, one can also specify normalized
        poles and zeros ("n"). Normalized poles and zeros are expected to have
        POSITIVE frequencies, and their respective low and high frequency gains
        are set to 1, unless they are located at 0 Hz.

        For the s-plane the formula is:
            pole2(f0, Q) = 1/(s^2 + w0 s / Q + w0^2) ["s"] or
            pole2(f0, Q) = 1/(s^2 + 2 pi f0 s / Q + (2 pi f0)^2) ["f"].
        For a normalized pole ["n"] the formula is:
            pole2(f0) = 1/(1 + i f/f0 + (f/f0)^2) with f0 > 0.
        The quality factor Q must be greater than 0.5.

        Args:
            f: pole frequency
            Q: quality factor
            gain: gain
            plane: location where poles/zeros are specified

        Returns True if successful
        """
        return self.filt.pole2(f, Q, gain, plane)

    def zero2(self, f, Q, gain, plane='s'):
        """Adds a complex zero pair

        Poles and zeros can be specified in the s-plane using units of rad/s
        (set plane to "s") or units of Hz ("f"). In both cases the frequency is
        expected to be POSITIVE. Alternatively, one can also specify normalized
        poles and zeros ("n"). Normalized poles and zeros are expected to have
        POSITIVE frequencies, and their respective low and high frequency gains
        are set to 1, unless they are located at 0 Hz.

        For the s-plane the formula is:
            zero2(f0, Q) = (s^2 + w0 s / Q + w0^2) ["s"] or
            zero2(f0, Q) = (s^2 + 2 pi f0 s / Q + (2 pi f0)^2 ["f"].
        For a normalized zero ["n"] the formula is:
            zero2(f0) = (1 + i f/f0 + (f/f0)^2) with f0 > 0.
        The quality factor Q must be greater than 0.5.

        Args:
            f: zero frequency
            Q: quality factor
            gain: gain
            plane: location where poles/zeros are specified

        Returns True if successful
        """
        return self.filt.zero2(f, Q, gain, plane)

    def zpk(self, zeros, poles, gain, plane='s'):
        """Adds a zero-pole-gain (zpk) filter

        Poles and zeros can be specified in the s-plane using units of rad/s
        (set plane to "s") or units of Hz ("f"). In both cases, the real part of
        the roots are expected to be NEGATIVE. Alternatively, one can also
        specify normalized poles and zeros ("n"). Normalized poles and zeros are
        expected to have POSITIVE real parts, and their respective low and high
        frequency gains are set to 1, unless they are located at 0 Hz.

        For the s-plane, the formula is:
            zpk(s) = k ((s - s_1)(s - s_2) ...) / ((s - p_1)(s - p_2) ...)
        with s_1, s_2, ... the locations of the zeros and p_1, p_2, ... the
        location of the poles. By replacing s_1->2 pi fz_1 and p_1 -> 2 pi fp_1
        one obtains the "f" representation. For normalized poles and zeros ["n"]
        one uses poles of the form:
            pole(f0) = 1/(1 + i f/f0); f0 > 0 and 
            pole(f0) = 1/(i f); f0 = 0.
        The zeros are then of the form:
            zero(f0) = (1 + i f/f0); f0 > 0 and 
    	    zero(f0) = (i f); f0 = 0.
        Poles and zeros with a non-zero imaginary part must come in pairs of
        complex conjugates.

        Args:
            zeros: array of zeros
            poles: array of poles
            gain: gain
            plane: location where poles/zeros are specified

        Returns True if successful
        """
        zeros = [dmtsigp.dComplex(np.real(z), np.imag(z)) for z in zeros]
        poles = [dmtsigp.dComplex(np.real(p), np.imag(p)) for p in poles]
        return self.filt.zpk(zeros, poles, gain, plane)

    def rpoly(self, numer, denom, gain):
        """Adds a rational polynomial (rpoly) in s

        A rational polynomial in s is specified by the polynomial coefficients
        in the numerator and the denominator, in descending order of s.

        The formula is:
            rpoly(s) = k (a_n s^n_z + a_n-1 s^(n_z-1) ...) / 
                         (b_n s^n_p + b_n-1 s^(n_p-1} ...)
        where a_n,  a_n-1, ..., a_0 are the coefficients of the polynomial in
        the numerator and b_n, b_n-1, ..., b_0 are the coefficients of the
        polynomial in the denominator. The polynomial coefficients are real.

        Args:
            numer: array of numerator coefficients
            denom: array of denominator coefficients
            gain: gain

        Returns True if successful
        """
        nnumer = len(numer)
        ndenom = len(denom)
        numer = array.array('d', numer)
        denom = array.array('d', denom)
        return self.filt.rpoly(numer, denom, gain)

    def biquad(self, b0, b1, b2, a1, a2):
        """Adds a second order section

        Returns true if successful
        """
        return self.filt.biquad(b0, b1, b2, a1, a2)

    def sos(self, coef, format='py'):
        """Adds a filter from second order section coefficients

        If the format is 'py', coefficients are provided in scipy.signal format.

        If the format is 's' or 'o', the number of coefficients must be 4 times
        the number of second order sections plus one.
        If the format is 's' (standard), coefficients are ordered like:
            gain, b1_1, b2_1, a1_1, a2_1, b1_2, b2_2, a1_2, a2_2, ...
        whereas for the format 'o' (online) the order is:
            gain, a1_1, a2_1, b1_1, b2_1, a1_2, a2_2, b1_2, b2_2, ...

        Args:
            coef: coefficients
            format: coefficient format

        Returns True if successful
        """
        real_format = format
        if format == 'py':
            real_format = 's'
            if len(coef.shape) < 2 or coef.shape[1] != 6:
                raise Exception('coeffs are not in scipy.signal format')
            soses = [coef[n, :] for n in range(coef.shape[0])]
            coef = [1,]
            for sos in soses:
                coef[0] *= sos[0]/sos[3]
                coef += [sos[1]/sos[0], sos[2]/sos[0], sos[4]/sos[3], sos[5]/sos[3]]
            coef = np.array(coef)
        coef = array.array('d', coef)
        return self.filt.sos(coef, real_format)

    def zroots(self, zeros, poles, gain=1.0):
        """Adds a filter from z-plane roots

        To be stable the z-plane poles must lie within the unit circle.

        Args:
            zero: array of zeros
            pole: array of poles
            gain: gain

        Returns True if successful
        """

        zeros = [dmtsigp.dComplex(np.real(z), np.imag(z)) for z in zeros]
        poles = [dmtsigp.dComplex(np.real(p), np.imag(p)) for p in poles]
        return self.filt.zroots(zeros, poles, gain)

    def direct(self, b, a):
        """Adds a filter from the direct form

        The direct form can be written as:
            H(z) = (b_0 + b_1 z^-1 + ... + b_nb z^-nb) /
	               (1 - a_1 z^-1 - ... - a_na z^-na)

        Cascaded second order sections are formed by finding the roots of the
        direct form. The specified coefficients are b_0, b_1, ..., b_nb for the
        numerator and a_1, a_2, ..., a_na for the denominator.

        Avoid the direct form since even fairly simple filters will run into
        precision problems.

        Args:
            b: array of numerator coefficients
            a: array of denominator coefficients exclusive of a0

        Returns True if successful
        """
        b = array.array('d', b)
        a = array.array('d', a)
        return self.filt.direct(b, a)

    def ellip(self, typ, order, rp, As, f1, f2=0.0):
        """Adds an elliptic filter

        Args:
            typ: filter type
            order: filter order
            rp: pass band ripple (dB)
            As: stop band attenuation (dB)
            f1: pass band edge (Hz)
            f2: another pass band edge (Hz)

        Returns True if successful
        """
        return self.filt.ellip(filter_type(typ), order, rp, As, f1, f2)

    def cheby1(self, typ, order, rp, f1, f2=0.0):
        """Adds a Chebyshev filter of type 1

        Args:
            typ: filter type
            order: filter order
            rp: pass band ripple (dB)
            f1: pass band edge (Hz)
            f2: another pass band edge (Hz)

        Returns True if successful
        """
        return self.filt.cheby1(filter_type(typ), order, rp, f1, f2)

    def cheby2(self, typ, order, As, f1, f2=0.0):
        """Adds a Chebyshev filter of type 2

        Args:
            typ: filter type
            order: filter order
            As: stop band attenuation (dB)
            f1: pass band edge (Hz)
            f2: another pass band edge (Hz)

        Returns True if successful
        """
        return self.filt.cheby2(filter_type(typ), order, As, f1, f2)

    def butter(self, typ, order, f1, f2=0.0):
        """Adds a Butterworth filter

        Args:
            typ: filter type
            order: filter order
            f1: pass band edge (Hz)
            f2: another pass band edge (Hz)

        Returns True if successful
        """
        return self.filt.butter(filter_type(typ), order, f1, f2)

    def notch(self, f0, Q, depth=0.0):
        """Adds a notch filter

        Args:
            f0: center frequency
            Q: quality factor (Q = center freq/width)
            depth: depth of the notch (dB)

        Returns True if successful
        """
        return self.filt.notch(f0, Q, depth)

    def resgain(self, f0, Q, height=0.0):
        """Adds a resonant gain filter

        Args:
            f0: center frequency
            Q: quality factor (Q = center freq/width)
            height: height of the peak (dB)

        Returns True if successful
        """
        return self.filt.resgain(f0, Q, height)

    def comb(self, f0, Q, amp=0.0, N=0):
        """Adds a comb filter

        Args:
            f0: fundamental frequency
            Q: quality factor (Q = center freq/width)
            amp: depth/height of notches/peaks (dB)
            N: number of harmonics

        Returns True if successful
        """
        return self.filt.comb(f0, Q, amp, N)

    def setgain(self, f, gain):
        """Sets the filter gain at specified frequency

        Args:
            f: frequency
            gain: set point

        Returns True if successful
        """
        return self.filt.setgain(f, gain)

    def closeloop(self, k=1.0):
        """Forms the closed loop response of the current filter

        1/(1+k*G(f))

        Args:
            k: additional gain

        Returns True if successful
        """
        return self.filt.closeloop(k)

    # zpk, rpoly, sos, zroots, direct are not implemented as properties, because
    # it would be hard to correctly support things like elementwise operations
    # on arrays
    def get_zpk(self, plane='s', unwarp=True):
        """Returns ZPK (zeros, poles, gain)

        See also FilterDesign.zpk().

        Args:
            plane: plane in which poles and zeros are specified
            unwarp: unwarp the frequency response
        """
        ret, zeros, poles, gain = dmtsigp.iir2zpk(self.filt.get(), plane, unwarp)
        if ret != True:
            raise Exception('iir2zpk failed')
        zeros = np.array([z.Real() + 1j*z.Imag() for z in zeros])
        poles = np.array([p.Real() + 1j*p.Imag() for p in poles])
        return (zeros, poles, gain)

    def set_zpk(self, zeros, poles, gain, plane='s'):
        """Sets ZPK (zeros, poles, gain)

        See also FilterDesign.zpk().

        Args:
            zeros: array of zeros
            poles: array of poles
            gain: gain
            plane: location where poles/zeros are specified

        Returns True if successful
        """
        self.reset()
        return self.zpk(zeros, poles, gain, plane)

    def get_rpoly(self, unwarp=True):
        """Returns rational polynomial (numer, denom, gain)

        See also FilterDesign.rpoly().

        Args:
            unwarp: unwarp the frequency response
        """
        ret, numer, denom, gain = dmtsigp.iir2poly(self.filt.get(), unwarp)
        if ret != True:
            raise Exception('iir2poly failed')
        return (np.array(numer), np.array(denom), gain)

    def set_rpoly(self, numer, denom, gain):
        """Sets rational polynomial (numer, denom, gain)

        See also FilterDesign.rpoly().

        Args:
            numer: numerator array
            denom: denominator array
            gain: gain

        Returns True if successful
        """
        self.reset()
        return self.rpoly(numer, denom, gain)

    def get_sos(self, format='py'):
        """Returns SOS (second order section) coefficients.

        Use format='s' to generate compatible second-order-sections for
        awg.Excitation.set_filter()

        See also FilterDesign.sos()
        """
        real_format = format
        if format == 'py':
            real_format = 's'
        ret, coef = dmtsigp.iir2z_sos(self.filt.get(), real_format)
        if ret != True:
            raise Exception('iir2z failed')
        assert(len(coef)%4 == 1)
        coef = np.array(coef)
        if format == 'py':
            # put coefficients in scipy.signal format
            gain = coef[0]
            soses = []
            for n in range(1, len(coef), 4):
                soses += [np.array([1, coef[n], coef[n+1], 1, coef[n+2], coef[n+3]])]
            if len(soses) == 0:
                # gain-only filter
                soses += [np.array([gain, 0, 0, 1, 0, 0])]
            else:
                # apply overall gain factor to first SOS section
                soses[0][:3] *= gain
            coef = np.vstack(soses)
        return coef

    def set_sos(self, coef, format='py'):
        """Sets SOS (second order section) coefficients

        See also FilterDesign.sos().

        Args:
            coef: second order section coefficients

        Returns True if successful
        """
        self.reset()
        return self.sos(coef, format=format)

    def get_zroots(self):
        """Returns z-plane roots (zeros, poles, gain)

        See also FilterDesign.zroots().
        """
        ret, zvec, pvec, gain = dmtsigp.iir2z(self.filt.get())
        if ret != True:
            raise Exception('iir2z failed')
        zeros = np.array([z.Real() + 1j*z.Imag() for z in zvec])
        poles = np.array([p.Real() + 1j*p.Imag() for p in pvec])
        return (zeros, poles, gain)

    def set_zroots(self, zeros, poles, gain):
        """Sets z-plane roots (zeros, poles, gain)

        See also FilterDesign.zroots().

        Args:
            zeros: array of zeros
            poles: array of poles
            gain: gain

        Returns True if successful
        """
        self.reset()
        return self.zroots(zeros, poles, gain)

    def get_direct(self):
        """Returns direct form coefficients (b, a)

        See also FilterDesign.direct().
        """
        ret, b, a = dmtsigp.iir2direct(self.filt.get())
        if ret != True:
            raise Exception('iir2direct failed')
        return (np.array(b), np.array(a))

    def set_direct(self, b, a):
        """Sets direct form coefficients (b, a)

        See also FilterDesign.direct().

        Args:
            b: numerator coefficients
            a: denominator coefficients

        Returns True if successful
        """
        self.reset()
        return self.direct(b, a)

    def freqresp(self, freq):
        """Returns filter frequency response at specified frequencies (in Hz)"""
        w = 2*np.pi*np.array(freq)/self.rate
        return signal.sosfreqz(self.get_sos(), worN=w)[1]

    def __repr__(self):
        return '{}(design={}, rate={})'.format(
            self.__class__.__name__,
            repr(self.design),
            repr(self.rate),
        )


def filter_type(val):
    """Returns Filter_Type enum value"""
    enum = {
        'LowPass': dmtsigp.Filter_Type.kLowPass,
        'HighPass': dmtsigp.Filter_Type.kHighPass,
        'BandPass': dmtsigp.Filter_Type.kBandPass,
        'BandStop': dmtsigp.Filter_Type.kBandStop,
    }
    return enum[val]


class DelegateToFilterDesign:
    """Descriptor for methods delegated from Section to FilterDesign"""
    # inspired by https://pypi.org/project/delegateto/
    def __init__(self, method, readonly=False):
        self.method = method
        self.readonly = readonly
        functools.update_wrapper(self, getattr(FilterDesign, method))

    def __get__(self, obj, objecttype):
        @functools.wraps(getattr(FilterDesign, self.method))
        def delegated(*args, **kwargs):
            fd = obj.get_filterdesign()
            fdmethod = getattr(fd, self.method)
            ret = fdmethod(*args, **kwargs)
            if not self.readonly:
                obj.set_filterdesign(fd)
            return ret
        return delegated


class DelegatePropertyToFilterDesign:
    """Descriptor for readonly properties delegated from Section to FilterDesign"""
    # inspired by https://pypi.org/project/delegateto/
    def __init__(self, prop):
        self.prop = prop
        functools.update_wrapper(self, getattr(FilterDesign, prop))

    def __get__(self, obj, objecttype):
        return getattr(obj.get_filterdesign(), self.prop)

    def __set__(self, obj, val):
        raise AttributeError


class Section:
    """Reads and edits foton file data for a filter module section

    Settable properties are available for the display name, design string, and
    switching settings.  Settings can be replicated using Section.copyfrom().

    As an alternative to parsing and writing design strings, most FilterDesign
    methods can be used directly on a Section.  One can also get a FilterDesign
    object with Section.get_filterdesign(), modify it, and apply it using
    Section.set_filterdesign().

    Args:
        lookup_fm: lookup function for the enclosing Module
        n: section index (0-9)
    """
    def __init__(self, lookup_fm, n):
        self._lookup_fm = lookup_fm
        self._idx = n

    _delegated = [
        'biquad',
        'butter',
        'cheby1',
        'cheby2',
        'closeloop',
        'comb',
        'direct',
        'ellip',
        'gain',
        'notch',
        'pole',
        'pole2',
        'reset',
        'resgain',
        'rpoly',
        'set_direct',
        'set_rpoly',
        'set_sos',
        'set_zpk',
        'set_zroots',
        'setgain',
        'sos',
        'zero',
        'zero2',
        'zpk',
        'zroots',
    ]
    for _x in _delegated:
        vars()[_x] = DelegateToFilterDesign(_x)

    _delegated_readonly = [
        'freqresp',
        'get_direct',
        'get_rpoly',
        'get_sos',
        'get_zpk',
        'get_zroots',
    ]
    for _x in _delegated_readonly:
        vars()[_x] = DelegateToFilterDesign(_x, readonly=True)

    _delegated_properties = [
        'order',
        'polecount',
        'polezerocount',
        'prewarp',
        'soscount',
        'zerocount',
    ]
    for _x in _delegated_properties:
        vars()[_x] = DelegatePropertyToFilterDesign(_x)

    del _x

    @property
    def sec(self):
        return self._lookup_fm()[self._idx]

    @property
    def index(self):
        """Section index"""
        return self.sec.getIndex()

    @index.setter
    def index(self, val):
        self.sec.setIndex(val)

    @property
    def name(self):
        """Section name"""
        return self.sec.getName()

    @name.setter
    def name(self, val):
        self.sec.setName(val)

    @property
    def design(self):
        """Design string"""
        return self.sec.getDesign()

    @design.setter
    def design(self, val):
        self.sec.setDesign(val)
        self.refresh()

    @property
    def input_switch(self):
        """Input switching

        Available input switching settings are:
            AlwaysOn
            ZeroHistory
        """
        enum = {
            filterfile.input_switching.kAlwaysOn: 'AlwaysOn',
            filterfile.input_switching.kZeroHistory: 'ZeroHistory',
        }
        return enum[self.sec.getInputSwitch()]

    @input_switch.setter
    def input_switch(self, val):
        enum = {
            'AlwaysOn': filterfile.input_switching.kAlwaysOn,
            'ZeroHistory': filterfile.input_switching.kZeroHistory,
        }
        self.sec.setInputSwitch(enum[val])

    @property
    def output_switch(self):
        """Output switching

        Available output switching settings are:
            Immediately
            Ramp
            InputCrossing
            ZeroCrossing
        """
        enum = {
            filterfile.output_switching.kImmediately: 'Immediately',
            filterfile.output_switching.kRamp: 'Ramp',
            filterfile.output_switching.kInputCrossing: 'InputCrossing',
            filterfile.output_switching.kZeroCrossing: 'ZeroCrossing',
        }
        return enum[self.sec.getOutputSwitch()]

    @output_switch.setter
    def output_switch(self, val):
        enum = {
            'Immediately': filterfile.output_switching.kImmediately,
            'Ramp': filterfile.output_switching.kRamp,
            'InputCrossing': filterfile.output_switching.kInputCrossing,
            'ZeroCrossing': filterfile.output_switching.kZeroCrossing,
        }
        self.sec.setOutputSwitch(enum[val])

    @property
    def ramp(self):
        """Ramp time"""
        return self.sec.getRamp()

    @ramp.setter
    def ramp(self, val):
        self.sec.setRamp(val)

    @property
    def tolerance(self):
        """Switching tolerance"""
        return self.sec.getTolerance()

    @tolerance.setter
    def tolerance(self, val):
        self.sec.setTolerance(val)

    @property
    def timeout(self):
        """Switching timeout"""
        return self.sec.getTimeout()

    @timeout.setter
    def timeout(self, val):
        self.sec.setTimeout(val)

    @property
    def header(self):
        return self.sec.getHeader()

    @header.setter
    def header(self, val):
        self.sec.setHeader(val)

    @property
    def rate(self):
        """Sample rate (Hz)"""
        return self._lookup_fm().getFSample()

    @property
    def is_unity(self):
        """True if filter is unity gain"""
        return self.sec.empty()

    @property
    def is_empty(self):
        """True if filter design is empty"""
        return self.sec.designEmpty()

    def empty(self):
        """DEPRECATED: use Section.is_empty instead"""
        warnings.warn('Section.empty() is deprecated: use Section.is_empty instead', DeprecationWarning)
        return self.is_empty

    # filterdesign is not implemented as a property because it would be hard
    # to ensure the Section updates correctly when calling FilterDesign methods
    @property
    def filt(self):
        """DEPRECATED: use Section.get_filterdesign() instead"""
        warnings.warn('Section.filt is deprecated: use Section.get_filterdesign() instead', DeprecationWarning)
        return self.get_filterdesign()

    def get_filterdesign(self):
        """Returns a FilterDesign object for the filter"""
        return FilterDesign(design=self.design, rate=self.rate)

    def set_filterdesign(self, val):
        """Sets the filter using the design string of a FilterDesign object"""
        if self.rate != val.rate:
            raise Exception('sample rates are different')
        self.design = val.design

    def check(self):
        """Checks filter (compare design string and FilterDesign)"""
        return self.sec.check()

    def valid(self):
        """Checks validity of design string"""
        return self.sec.valid()

    def refresh(self):
        """Updates FilterDesign from design string"""
        # rename update as refresh so it's not confused with dict's update method
        return self.sec.update()

    def add(self, cmd):
        """Appends a design string to the design"""
        return self.sec.add(cmd)

    def copyfrom(self, src):
        """Makes section identical to src"""
        self.name = src.name
        self.design = src.design
        self.input_switch = src.input_switch
        self.output_switch = src.output_switch
        self.ramp = src.ramp
        self.tolerance = src.tolerance
        self.timeout = src.timeout

    def __repr__(self):
        return '<{} {} {}>'.format(
            self.__class__.__name__,
            repr(self.index),
            repr(self.name),
        )

    def clear(self):
        """
        Clear a section.  Make it an empty gain1 filter as understood by GDS dmtsigp.
        :return: None
        """
        self.sec.setName("")
        self.sec.setDesign("")


class Filter:
    """Implements a time-domain IIR filter, specified by a FilterDesign

    The implementation uses scipy.signal.sosfilt().

    Args:
        design: FilterDesign object
        ic: array of initial conditions, whose shape is (design.soscount, 2)
    """
    def __init__(self, design, ic=None):
        self.design = design
        self.ic = ic
        self.coef = design.get_sos()
        if ic is None:
            self.clear_history()

    def clear_history(self):
        """Zeros filter state (initial conditions)"""
        self.ic = np.zeros((self.coef.shape[0], 2))

    def apply(self, data):
        """Returns results of filter applied to data array

        Filter history is maintained between calls to Filter.apply(). It can be
        erased with Filter.clear_history().
        """
        out, ic = signal.sosfilt(self.coef, data, zi=self.ic)
        self.ic = ic
        return out

    def __repr__(self):
        return '{}({}, ic={})'.format(
            self.__class__.__name__,
            repr(self.design),
            repr(self.ic),
        )


def iir2zpk(filt, plane='s', prewarp=True):
    """DEPRECATED: use FilterDesign methods instead"""
    warnings.warn('iir2zpk is deprecated: use FilterDesign methods instead', DeprecationWarning)
    try:
        arg = filt.filt.get()
    except AttributeError:
        arg = filt.get()
    success, zpk = dmtsigp.iir2zpk_design(arg, plane, prewarp)
    if not success:
        raise Exception("iir2zpk failed")
    return zpk


def iir2z(filt, format='s'):
    """DEPRECATED: use FilterDesign methods instead"""
    warnings.warn('iir2z is deprecated: use FilterDesign methods instead', DeprecationWarning)
    try:
        arg = filt.filt.get()
    except AttributeError:
        arg = filt.get()
    success, ba = dmtsigp.iir2z_sos(arg, format)
    if not success:
        raise Exception("iir2z failed")
    return ba


def iir2poly(filt, unwarp=True):
    """DEPRECATED: use FilterDesign methods instead"""
    warnings.warn('iir2poly is deprecated: use FilterDesign methods instead', DeprecationWarning)
    try:
        arg = filt.filt.get()
    except AttributeError:
        arg = filt.get()
    success, numer, denom, gain = dmtsigp.iir2poly(arg, unwarp)
    if not success:
        raise Exception("ii2poly failed")
    return numer, denom, gain


def iir2direct(filt):
    """DEPRECATED: use FilterDesign methods instead"""
    warnings.warn('iir2direct is deprecated: use FilterDesign methods instead', DeprecationWarning)
    try:
        arg = filt.filt.get()
    except AttributeError:
        arg = filt.get()
    success, b, a = dmtsigp.iir2direct(arg)
    if not success:
        raise Exception("iir2direct failed")
    return b, a
