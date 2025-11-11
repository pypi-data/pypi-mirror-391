# Copyright (c) 2021-2025 Cubillos & Blecic
# Pyrat Bay is open-source software under the GNU GPL-2.0 license (see LICENSE)

import os
import pathlib
import tempfile

from conftest import make_config

import pyratbay as pb
import pyratbay.atmosphere as pa
import pyratbay.constants as pc
import pyratbay.io as io
import pyratbay.opacity as op
import pyratbay.spectrum as ps
from pyratbay.constants import ROOT

tmp_path = tempfile.TemporaryDirectory()
tmp_path = pathlib.Path(tmp_path.name)
tmp_path.mkdir()

INPUTS = f'{ROOT}tests/inputs/'
OUTPUTS = f'{ROOT}tests/outputs/'

os.chdir(tmp_path)

# Relative tolerance of less than 0.01% difference:
rtol = 0.01 / 100.0

# ::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
# Atmosphere:
nlayers = 51
ptop = '1e-6 bar'
pbottom = '100 bar'
pressure_cgs = pa.pressure(ptop, pbottom, nlayers)
tp_guillot = pa.tmodels.Guillot(pressure_cgs)
temp_guillot = tp_guillot([-4.83, -0.8, 0, 0, 1200, 100])

species = "H2 He H Na K H2O CH4 CO CO2".split()
abundances = [
    0.85, 0.149, 1.0e-06, 3.0e-06, 5.0e-08,
    4.0e-04, 1.0e-04, 5.0e-04, 1.0e-07,
]
vmr = pa.uniform(pressure_cgs, temp_guillot, species, abundances)
io.write_atm(
    'inputs/atmosphere_uniform_test.atm',
    pressure_cgs, temp_guillot, species, vmr, punits='bar',
)

# ::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
# Transmission:
keys = [
    'sampled_cs', 'tli', 'lec', 'cia', 'alkali', 'deck',
    'patchy', 'patchy_clear', 'patchy_cloudy', 'h_ion', 'all',
    'tmodel', 'vert', 'scale', 'fit1', 'fit2', 'fit3', 'fit4',
    'bandflux4', 'resolution', 'wl_step',
    'skip_ls', 'skip_lbl', 'skip_cia', 'skip_H2_H2_cia',
    'skip_alkali', 'skip_sodium', 'skip_rayleigh', 'skip_dalgarno',
    'skip_cloud', 'skip_deck', 'all_ls'
]

expected = {
    key:np.load(f"{ROOT}tests/expected/"
                f"expected_spectrum_transmission_{key}_test.npz")['arr_0']
    for key in keys
}

# ::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
# Emission:
keys = [
    'sampled_cs', 'tli', 'lec', 'cia', 'alkali', 'deck', 'all',
    'patchy', 'patchy_clear', 'patchy_cloudy', 'quadrature',
    'resolution', 'two_stream', 'tmodel', 'vert', 'scale',
    ]

expected = {
    key:np.load(f"{ROOT}tests/expected/"
                f"expected_spectrum_emission_{key}_test.npz")['arr_0']
    for key in keys
}

# ::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
# Eclipse:
keys = [
    'lec', 'cia', 'alkali', 'deck', 'tli', 'all', 'quadrature', 'sampled_cs',
    'patchy', 'patchy_clear', 'patchy_cloudy',
    'resolution', 'two_stream', 'tmodel', 'vert', 'scale',
    ]

expected = {
    key:np.load(f"{ROOT}tests/expected/"
                f"expected_spectrum_eclipse_{key}_test.npz")['arr_0']
    for key in keys
}



# Run test from tests/test_transmission.py, e.g.:
key = 'lec'

plt.figure(1)
plt.clf()
plt.plot(pyrat.spec.wl, pyrat.spec.spectrum, c='xkcd:blue')
plt.plot(1e4/pyrat.spec.wn, expected[key], c='salmon', alpha=0.7)
plt.ylabel('spectrum')
plt.tight_layout()

plt.figure(2)
plt.clf()
plt.plot(1e4/pyrat.spec.wn, 100*(1-pyrat.spec.spectrum/expected[key]))
plt.ylabel('Diff (%)')
plt.tight_layout()

# For eclipse runs
plt.figure(0)
plt.clf()
plt.plot(pyrat.spec.wl, pyrat.spec.fplanet, c='xkcd:blue', label='run')
#plt.plot(pyrat.spec.wl, expected[key], c='salmon', alpha=0.7, label='expected')
#plt.plot(pyrat.spec.wl, fp_max, c='0.5', dashes=(4,2))
#plt.plot(pyrat.spec.wl, fp_min, c='0.5', dashes=(4,2))
plt.ylabel('Fp')
plt.legend(loc='best')
plt.tight_layout()

# ::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::

key = 'all_ls'

plt.figure(1)
plt.clf()
plt.plot(pyrat.spec.wl, pyrat.spec.spectrum, c='xkcd:blue',label='run')
plt.plot(pyrat.spec.wl, expected[key], c='salmon', alpha=0.7,label='exp')
plt.legend(loc='best')
plt.tight_layout()

plt.figure(2)
plt.clf()
plt.plot(1e4/pyrat.spec.wn, 100*(1-pyrat.spec.spectrum/expected[key]))
plt.ylabel('diff (%)')
plt.tight_layout()


# Eclipse
np.savez(
    f'{ROOT}tests/expected/expected_spectrum_eclipse_{key}_test.npz',
    pyrat.spec.spectrum,
)

# Transmission
np.savez(
    f'{ROOT}tests/expected/expected_spectrum_transmission_{key}_test.npz',
    pyrat.spec.spectrum,
)

# Emission
np.savez(
    f'{ROOT}tests/expected/expected_spectrum_emission_{key}_test.npz',
    pyrat.spec.spectrum,
)



with np.printoptions(formatter={'float':'{:.8e}'.format}):
    print(repr(ev_bandflux))


np.savez(
    f'{ROOT}tests/expected/expected_spectrum_transmission_bandflux4_test.npz',
    model4[1],
)


    with np.printoptions(formatter={'float':'{:.7e}'.format}):
        print(repr(interp_cs[0,j,:,k]))


# ::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
# ::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
savefile = '/Users/pato/Dropbox/IWF/projects/2014_pyratbay/pyratbay/tests/expected/expected_spectrum_transmission_KEY_test.npz'

    cfg = make_config(
        tmp_path,
        ROOT+'tests/configs/spectrum_transmission_test.cfg',
        remove=['tlifile', 'continuum_cross_sec', 'alkali', 'clouds'],
    )
    pyrat = pb.run(cfg)
    np.savez(savefile.replace('KEY','lec'), pyrat.spec.spectrum)

    cfg = make_config(
        tmp_path,
        ROOT+'tests/configs/spectrum_transmission_test.cfg',
        remove=['tlifile', 'rayleigh', 'alkali', 'clouds'],
    )
    pyrat = pb.run(cfg)
    np.savez(savefile.replace('KEY','cia'), pyrat.spec.spectrum)

    cfg = make_config(
        tmp_path,
        ROOT+'tests/configs/spectrum_transmission_test.cfg',
        remove=['tlifile', 'continuum_cross_sec', 'rayleigh', 'clouds'],
        reset={'wl_low':'0.45 um', 'wl_high':'1.0 um'},
    )
    pyrat = pb.run(cfg)
    np.savez(savefile.replace('KEY','alkali'), pyrat.spec.spectrum)

    cfg = f'{ROOT}tests/configs/spectrum_transmission_h_ion.cfg'
    pyrat = pb.run(cfg)
    np.savez(savefile.replace('KEY','h_ion'), pyrat.spec.spectrum)

    cfg = make_config(
        tmp_path,
        ROOT+'tests/configs/spectrum_transmission_test.cfg',
        remove=['continuum_cross_sec', 'rayleigh', 'clouds', 'alkali'],
    )
    pyrat = pb.run(cfg)
    np.savez(savefile.replace('KEY','tli'), pyrat.spec.spectrum)

    cfg = make_config(
        tmp_path,
        ROOT+'tests/configs/spectrum_transmission_test.cfg',
        remove=['clouds'],
    )
    pyrat = pb.run(cfg)
    np.savez(savefile.replace('KEY','all'), pyrat.spec.spectrum)

    reset = {
        'fpatchy': '0.5',
        'rpars': '10.0 -15.0',
    }
    cfg_file = ROOT+'tests/configs/spectrum_transmission_test.cfg'
    cfg = make_config(tmp_path, cfg_file, reset=reset)
    pyrat = pb.run(cfg)
    np.savez(savefile.replace('KEY','patchy'), pyrat.spec.spectrum)
    np.savez(savefile.replace('KEY','patchy_clear'), pyrat.spec.clear)
    np.savez(savefile.replace('KEY','patchy_cloudy'), pyrat.spec.cloudy)

    cfg = make_config(
        tmp_path,
        ROOT+'tests/configs/spectrum_transmission_test.cfg',
        reset={'resolution':'5000.0'},
        remove=['clouds'],
    )
    pyrat = pb.run(cfg)
    np.savez(savefile.replace('KEY','resolution'), pyrat.spec.spectrum)

    cfg = make_config(
        tmp_path,
        ROOT+'tests/configs/spectrum_transmission_test.cfg',
        reset={'wlstep': '1e-4 um'},
        remove=['clouds'],
    )
    pyrat = pb.run(cfg)
    np.savez(savefile.replace('KEY','wl_step'), pyrat.spec.spectrum)

    cfg = make_config(
        tmp_path,
        ROOT+'tests/configs/spectrum_transmission_test.cfg',
        remove=['tlifile', 'clouds'],
        reset={'extfile':f'{OUTPUTS}exttable_test_300-3000K_1.1-1.7um.npz'},
    )
    pyrat = pb.run(cfg)
    np.savez(savefile.replace('KEY','etable'), pyrat.spec.spectrum)

    cfg = make_config(
        tmp_path,
        ROOT+'tests/configs/spectrum_transmission_test.cfg',
        remove=['clouds', 'cpars'],
        reset={'tmodel':'guillot', 'tpars':'-4.67 -0.8 -0.8 0.5 1486.0 100.0'},
    )
    pyrat = pb.run(cfg)
    np.savez(savefile.replace('KEY','tmodel'), pyrat.spec.spectrum)

    reset = {
        'molvars': 'log_H2O',
        'molpars': '-5',
        'bulk': 'H2 He',
    }
    cfg = make_config(
        tmp_path,
        ROOT+'tests/configs/spectrum_transmission_test.cfg',
        remove=['clouds', 'cpars'],
        reset=reset,
    )
    pyrat = pb.run(cfg)
    np.savez(savefile.replace('KEY','vert'), pyrat.spec.spectrum)

    reset = {
        'molvars': 'scale_H2O',
        'molpars': '-1',
        'bulk': 'H2 He',
    }
    cfg = make_config(
        tmp_path,
        ROOT+'tests/configs/spectrum_transmission_test.cfg',
        remove=['clouds', 'cpars'],
        reset=reset,
    )
    pyrat = pb.run(cfg)
    np.savez(savefile.replace('KEY','scale'), pyrat.spec.spectrum)

    retrieval_params = """
        log_kappa'  -4.67
        log_gamma1  -0.8
        log_gamma2  -0.8
        alpha        0.5
        T_irr        1486.0
        T_int        100.0
        log_H2O      -4.0
        log_k_ray     0.0
        alpha_ray    -4.0
        log_p_cl      2.0
    """
    reset = {
        'tmodel': 'guillot',
        'cpars': '2.0',
        'molvars': 'log_H2O',
        'bulk': 'H2 He',
        'retrieval_params': retrieval_params,
    }
    cfg = make_config(
        tmp_path,
        ROOT+'tests/configs/spectrum_transmission_test.cfg',
        reset=reset,
    )
    pyrat = pb.run(cfg)
    np.savez(savefile.replace('KEY','fit1'), pyrat.spec.spectrum)
    # Cloud deck:
    params = [-4.67, -0.8, -0.8, 0.5, 1486.0, 100.0, -4.0, 0.0, -4.0, -3.0]
    model2 = pyrat.eval(params, retmodel=True)
    rmin = np.amin(np.sqrt(pyrat.spec.spectrum)) * pyrat.atm.rstar
    cloud_deck = pyrat.opacity.models[5]
    rexpected = cloud_deck.rsurf
    np.testing.assert_allclose(rmin, rexpected, rtol=rtol)
    np.savez(savefile.replace('KEY','fit2'), pyrat.spec.spectrum)
    # Check pyrat.ret.params has been updated:
    np.testing.assert_allclose(pyrat.ret.params, params, rtol=rtol)
    params = [-4.67, -0.8, -0.8, 0.5, 1486.0, 100.0, -8.0, 0.0, -4.0, 2.0]
    model3 = pyrat.eval(params, retmodel=True)
    np.savez(savefile.replace('KEY','fit3'), pyrat.spec.spectrum)

    pyrat = pb.run(ROOT+'tests/configs/spectrum_transmission_filters_test.cfg')
    model4 = pyrat.eval(pyrat.ret.params, retmodel=True)
    np.savez(savefile.replace('KEY','fit4'), pyrat.spec.spectrum)
    np.savez(f'{ROOT}tests/expected/expected_spectrum_transmission_bandflux4_test.npz', model4[1])

# ::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
savefile = '/Users/pato/Dropbox/IWF/projects/2014_pyratbay/pyratbay/tests/expected/expected_spectrum_emission_KEY_test.npz'

    cfg = make_config(
        tmp_path,
        ROOT+'tests/configs/spectrum_emission_test.cfg',
        remove=['tlifile', 'continuum_cross_sec', 'alkali', 'clouds'],
    )
    pyrat = pb.run(cfg)
    np.savez(savefile.replace('KEY','lec'), pyrat.spec.spectrum)

    cfg = make_config(
        tmp_path,
        ROOT+'tests/configs/spectrum_emission_test.cfg',
        remove=['tlifile', 'rayleigh', 'alkali', 'clouds'],
    )
    pyrat = pb.run(cfg)
    np.savez(savefile.replace('KEY','cia'), pyrat.spec.spectrum)

    cfg = make_config(
        tmp_path,
        ROOT+'tests/configs/spectrum_emission_test.cfg',
        remove=['tlifile', 'continuum_cross_sec', 'rayleigh', 'clouds'],
        reset={'wl_low':'0.45 um', 'wl_high':'1.0 um'},
    )
    pyrat = pb.run(cfg)
    np.savez(savefile.replace('KEY','alkali'), pyrat.spec.spectrum)

    cfg = make_config(
        tmp_path,
        ROOT+'tests/configs/spectrum_emission_test.cfg',
        remove=['tlifile', 'continuum_cross_sec', 'rayleigh', 'alkali'],
    )
    pyrat = pb.run(cfg)
    np.savez(savefile.replace('KEY','deck'), pyrat.spec.spectrum)


    cfg = make_config(
        tmp_path,
        ROOT+'tests/configs/spectrum_emission_test.cfg',
        remove=['continuum_cross_sec', 'rayleigh', 'clouds', 'alkali'],
    )
    pyrat = pb.run(cfg)
    np.savez(savefile.replace('KEY','tli'), pyrat.spec.spectrum)

    cfg = make_config(
        tmp_path,
        ROOT+'tests/configs/spectrum_emission_test.cfg',
        remove=['clouds'],
    )
    pyrat = pb.run(cfg)
    np.savez(savefile.replace('KEY','all'), pyrat.spec.spectrum)

    cfg = make_config(
        tmp_path,
        ROOT+'tests/configs/spectrum_emission_test.cfg',
        reset={'quadrature': '5'},
        remove=['clouds'],
    )
    pyrat = pb.run(cfg)
    spectrum = pyrat.spec.spectrum
    np.savez(savefile.replace('KEY','quadrature'), pyrat.spec.spectrum)

    cfg = make_config(
        tmp_path,
        ROOT+'tests/configs/spectrum_emission_test.cfg',
        reset={'rt_path': 'emission_two_stream'},
        remove=['clouds'],
    )
    pyrat = pb.run(cfg)
    np.savez(savefile.replace('KEY','two_stream'), pyrat.spec.spectrum)


    cfg = make_config(
        tmp_path,
        ROOT+'tests/configs/spectrum_emission_test.cfg',
        reset={'resolution':'5000.0'},
        remove=['clouds'],
    )
    pyrat = pb.run(cfg)
    np.savez(savefile.replace('KEY','resolution'), pyrat.spec.spectrum)


    reset = {
        'extfile': f'{OUTPUTS}exttable_test_300-3000K_1.1-1.7um.npz',
    }
    cfg = make_config(
        tmp_path,
        ROOT+'tests/configs/spectrum_emission_test.cfg',
        remove=['tlifile', 'clouds'],
        reset=reset,
    )
    pyrat = pb.run(cfg)
    np.savez(savefile.replace('KEY','etable'), pyrat.spec.spectrum)


    reset = {
        'tmodel':'guillot',
        'tpars':'-4.67 -0.8 -0.8 0.5 1486.0 100.0',
    }
    cfg = make_config(
        tmp_path,
        ROOT+'tests/configs/spectrum_emission_test.cfg',
        remove=['clouds', 'cpars'],
        reset=reset,
    )
    pyrat = pb.run(cfg)
    np.savez(savefile.replace('KEY','tmodel'), pyrat.spec.spectrum)

    reset={
        'molvars': 'log_H2O',
        'molpars': '-5',
        'bulk': 'H2 He',
    }
    cfg = make_config(
        tmp_path,
        ROOT+'tests/configs/spectrum_emission_test.cfg',
        remove=['clouds', 'cpars'],
        reset=reset,
    )
    pyrat = pb.run(cfg)
    np.savez(savefile.replace('KEY','vert'), pyrat.spec.spectrum)

    reset={
        'molvars': 'scale_H2O',
        'molpars': '-1',
        'bulk': 'H2 He',
    }
    cfg = make_config(
        tmp_path,
        ROOT+'tests/configs/spectrum_emission_test.cfg',
        remove=['clouds', 'cpars'],
        reset=reset,
    )
    pyrat = pb.run(cfg)
    np.savez(savefile.replace('KEY','scale'), pyrat.spec.spectrum)


# ::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
# ::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
# Opacities:

nlayers = 6
pressure = pa.pressure('1e-8 bar', '1e2 bar', nlayers)
temperature = np.tile(1000.0, nlayers)
species = ['Na', 'K', 'H2', 'H', 'He']

vmr = pa.abundance(pressure, temperature, species)
number_densities = pa.ideal_gas_density(vmr, pressure, temperature)
Na_density = number_densities[:,0]
K_density = number_densities[:,1]


    wn_min = 1e4/0.65
    wn_max = 1e4/0.55
    resolution = 15000.0
    wn = ps.constant_resolution_spectrum(wn_min, wn_max, resolution)
    alkali = op.alkali.SodiumVdW(pressure, wn, cutoff=1000.0)

    temperature1 = np.tile(1000.0, nlayers)
    ec1 = alkali.calc_extinction_coefficient(temperature1, Na_density)
    expected_cs1 = np.copy(alkali.cross_section)

    temperature2 = np.tile(2500.0, nlayers)
    ec2 = alkali.calc_extinction_coefficient(temperature2, Na_density)
    expected_cs2 = np.copy(alkali.cross_section)

    np.savez(
        'tests/expected/expected_alkali_Na_opacity.npz',
        expected_cs1=expected_cs1,
        expected_cs2=expected_cs2,
        expected_ec1=ec1,
        expected_ec2=ec2,
    )

    wn_min = 1e4/0.84
    wn_max = 1e4/0.70
    resolution = 15000.0
    wn = ps.constant_resolution_spectrum(wn_min, wn_max, resolution)
    alkali = op.alkali.PotassiumVdW(pressure, wn, cutoff=1000.0)

    temperature1 = np.tile(1000.0, nlayers)
    ec1 = alkali.calc_extinction_coefficient(temperature1, K_density)
    expected_cs1 = np.copy(alkali.cross_section)

    temperature2 = np.tile(2500.0, nlayers)
    ec2 = alkali.calc_extinction_coefficient(temperature2, K_density)
    expected_cs2 = np.copy(alkali.cross_section)

    np.savez(
        'tests/expected/expected_alkali_K_opacity.npz',
        expected_cs1=expected_cs1,
        expected_cs2=expected_cs2,
        expected_ec1=ec1,
        expected_ec2=ec2,
    )


    # CIA
    wn_min = 1e4/10.0
    wn_max = 1e4/0.5
    resolution = 15.0
    wn = ps.constant_resolution_spectrum(wn_min, wn_max, resolution)

    nlayers = 6
    pressure = pa.pressure('1e-8 bar', '1e2 bar', nlayers)
    temperature = np.tile(1200.0, nlayers)
    species = ['H2', 'H', 'He']
    vmr = pa.abundance(pressure, temperature, species)
    number_densities = pa.ideal_gas_density(vmr, pressure, temperature)

    cs_file = 'CIA_Borysow_H2H2_0060-7000K_0.6-500um.dat'
    cia = op.Collision_Induced(f'{c_root}{cs_file}', wn)

    cia_indices = [species.index(mol) for mol in cia.species]
    densities = number_densities[:,cia_indices]
    temp1 = np.tile(1200.0, nlayers)
    cross_section1 = cia.calc_cross_section(temp1)
    temp2 = np.tile(3050.0, nlayers)
    cross_section2 = cia.calc_cross_section(temp2)
    temp3 = 1200.0
    cross_section3 = cia.calc_cross_section(temp3)

    extinction1 = cia.calc_extinction_coefficient(temp1, densities)
    extinction3 = cia.calc_extinction_coefficient(temp1[3], densities[3])

    np.savez(
        'tests/expected/expected_cia_H2H2_opacity.npz',
        expected_cs1=cross_section1,
        expected_cs2=cross_section2,
        expected_cs3=cross_section3,
        expected_ec1=extinction1,
        expected_ec3=extinction3,
    )

    # Line sampling
    cs_files = f"{pc.ROOT}tests/outputs/exttable_test_300-3000K_1.1-1.7um.npz"
    ls = op.Line_Sample(cs_files, min_wn=9000.0, max_wn=9040.0)

    temp = np.tile(1200.0, ls.nlayers)
    vmr = np.tile(3e-4, (ls.nlayers,ls.nspec))
    densities = pa.ideal_gas_density(vmr, ls.press, temp)
    cross_section = ls.calc_cross_section(temp)
    extinction = ls.calc_extinction_coefficient(temp, densities)
    np.savez(
        f"{pc.ROOT}tests/expected/expected_ls_H2O_opacity.npz",
        expected_ec=extinction,
        expected_cs=cross_section,
    )


# ::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
# ::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
cfile = f'{ROOT}pyratbay/data/CIA/CIA_Borysow_H2H2_0060-7000K_0.6-500um.dat'
cfg = make_config(
    tmp_path,
    ROOT+'tests/configs/spectrum_transmission_test_tli.cfg',
    reset={'continuum_cross_sec': cfile, 'wl_low': '0.55'},
)
pyrat = pb.run(cfg)
wl = 1e4/pyrat.spec.wn
layer = 31
ec, labels = pyrat.get_ec(layer)

#with np.load(f'{ROOT}tests/expected/expected_get_ec_lbl.npz') as d:
#    expected_extinction = d['ec']

plt.figure(0)
plt.clf()
for i in range(len(labels)):
    plt.semilogy(1e4/pyrat.spec.wn, expected_extinction[i], c='k')
    plt.semilogy(1e4/pyrat.spec.wn, ec[i], label=labels[i])
plt.legend(loc='upper right')

ec_file = f'{ROOT}tests/expected/expected_get_ec_lbl.npz'
np.savez(ec_file, ec=ec)


# def test_get_ec_line_sample(tmp_path):
extfile = ROOT+'tests/outputs/exttable_test_300-3000K_1.1-1.7um.npz'
reset = {
    'extfile': extfile,
    'chemistry': 'tea',
    'species': 'H2 H He Na K H2O CH4 CO CO2 e- H- H+ H2+ Na- Na+ K+ K-',
    'h_ion': 'h_ion_john1988',
}
cfg = make_config(
    tmp_path,
    ROOT+'tests/configs/spectrum_transmission_test.cfg',
    reset=reset,
    remove=['tlifile', 'clouds'],
)
pyrat = pb.run(cfg)
wl = 1e4/pyrat.spec.wn
layer = 31  # around 1e5 barye
ec, labels = pyrat.get_ec(layer)

plt.figure(0)
plt.clf()
for i in range(len(labels)):
    plt.semilogy(wl, expected_extinction[i], c='k')
    plt.semilogy(wl, ec[i], label=labels[i])
plt.legend(loc='best')

ec_file = f'{ROOT}tests/expected/expected_get_ec_ls.npz'
np.savez(ec_file, ec=ec)

