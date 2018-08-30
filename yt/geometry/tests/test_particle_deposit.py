from yt.utilities.exceptions import \
    YTBoundsDefinitionError

from yt.convenience import \
    load
from yt.testing import \
    fake_random_ds, \
    requires_file
from numpy.testing import \
    assert_raises
import yt
from numpy.testing import assert_array_less
import numpy as np


def test_cic_deposit():
    ds = fake_random_ds(64, nprocs = 8, particles=64**3)
    my_reg = ds.arbitrary_grid(ds.domain_left_edge, ds.domain_right_edge,
            dims=[1, 800, 800])
    f = ("deposit", "all_cic")
    assert_raises(YTBoundsDefinitionError, my_reg.__getitem__, f)

RAMSES = 'output_00080/info_00080.txt'

@requires_file(RAMSES)
def test_one_zone_octree_deposit():
    ds = load(RAMSES)

    # Get a sphere centred on the main halo
    hpos = ds.arr([0.5215110772898429, 0.5215110772898429, 0.5215110772898429], 'code_length')
    hrvir = ds.quan(0.042307235300540924, 'Mpc')

    sp = ds.sphere(hpos, hrvir*10)
    assert sp['deposit', 'io_cic'].shape == (1,)

@requires_file(RAMSES)
def test_mesh_deposition():
    ds = yt.load(RAMSES)
    ds.add_deposited_mesh_field(('index', 'x'), ptype='all')
    ds.add_deposited_mesh_field(('index', 'dx'), ptype='all')

    dx = ds.r['all', 'cell_index_dx']
    x = ds.r['all', 'cell_index_x']
    xpart = ds.r['all', 'particle_position_x']

    dist = (x - xpart) / dx

    upper = np.ones_like(dx) / 2

    # Some particles are out of their domain, skip them
    mask = np.isfinite(dist)

    assert_array_less(dist[mask], upper[mask])
    assert_array_less(-dist[mask], upper[mask])

@requires_file(output_00080)
def test_mesh_deposition_for_filtered_particles():
    ds = yt.load(output_00080)

    @yt.particle_filter(requires=['particle_position_x'], filtered_type='io')
    def left(pfilter, data):
        return data[(pfilter.filtered_type, 'particle_position_x')].to('code_length') < 0.5
    ds.add_particle_filter('left')

    for f in (('index', 'x'), ('index', 'dx'), ('gas', 'density')):
        ds.add_deposited_mesh_field(f, ptype='io')
        ds.add_deposited_mesh_field(f, ptype='left')

    data_sources = (ds.all_data(), ds.box([0]*3, [0.1]*3))

    def test_source(ptype, src):
        # Test accessing
        src[ptype, 'cell_index_x']
        src[ptype, 'cell_index_dx']
        src[ptype, 'cell_gas_density']

    for ptype in ('io', 'left'):
        for src in data_sources:
            yield test_source, ptype, src
