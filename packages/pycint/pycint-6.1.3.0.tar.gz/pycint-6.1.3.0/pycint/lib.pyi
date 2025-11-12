from typing import Callable

import numpy as np

from pycint.typing import CArray, CData, Ptr

type CallbackFunc = Callable[..., int]
type VoidCallbackFunc = Callable[..., None]

class PairData(CData):
    """Corresponds to C PairData struct."""

    rij: CArray[float]  # double rij[3]
    eij: float
    cceij: float

class CINTOpt(CData):
    """Corresponds to C CINTOpt struct."""

    index_xyz_array: Ptr[Ptr[int]]  # int **index_xyz_array
    non0ctr: Ptr[Ptr[int]]  # int **non0ctr
    sortedidx: Ptr[Ptr[int]]  # int **sortedidx
    nbas: int
    log_max_coeff: Ptr[Ptr[float]]  # double **log_max_coeff
    pairdata: Ptr[Ptr[PairData]]  # PairData **pairdata

class CINTEnvVars(CData):
    """Corresponds to C CINTEnvVars struct."""

    atm: Ptr[int]  # int *atm
    bas: Ptr[int]  # int *bas
    env: Ptr[float]  # double *env
    shls: Ptr[int]  # int *shls
    natm: int
    nbas: int

    i_l: int
    j_l: int
    k_l: int
    l_l: int
    nfi: int  # number of cartesian components
    nfj: int

    # union for nfk/grids_offset
    nfk: int
    grids_offset: int

    # union for nfl/ngrids
    nfl: int
    ngrids: int

    nf: int  # = nfi*nfj*nfk*nfl
    rys_order: int  # = nrys_roots for regular ERIs. can be nrys_roots/2 for SR ERIs
    x_ctr: CArray[int]  # int x_ctr[4]

    gbits: int
    ncomp_e1: int  # = 1 if spin free, = 4 when spin included
    ncomp_e2: int  # corresponds to POSX,POSY,POSZ,POS1, see cint.h
    ncomp_tensor: int  # e.g. = 3 for gradients

    # values may diff based on the g0_2d4d algorithm
    li_ceil: int  # power of x, == i_l if nabla is involved, otherwise == i_l
    lj_ceil: int
    lk_ceil: int
    ll_ceil: int
    g_stride_i: int  # nrys_roots * shift of (i++,k,l,j)
    g_stride_k: int  # nrys_roots * shift of (i,k++,l,j)
    g_stride_l: int  # nrys_roots * shift of (i,k,l++,j)
    g_stride_j: int  # nrys_roots * shift of (i,k,l,j++)
    nrys_roots: int
    g_size: int  # ref to cint2e.c g = malloc(sizeof(double)*g_size)

    g2d_ijmax: int
    g2d_klmax: int
    common_factor: float
    expcutoff: float
    rirj: CArray[float]  # double rirj[3]
    rkrl: CArray[float]  # double rkrl[3]
    rx_in_rijrx: Ptr[float]  # double *rx_in_rijrx
    rx_in_rklrx: Ptr[float]  # double *rx_in_rklrx

    ri: Ptr[float]  # double *ri
    rj: Ptr[float]  # double *rj
    rk: Ptr[float]  # double *rk

    # union for rl/grids
    rl: Ptr[float]  # double *rl (in int2e or int3c2e)
    grids: Ptr[float]  # double *grids (in int1e_grids)

    f_g0_2e: CallbackFunc  # int (*f_g0_2e)()
    f_g0_2d4d: VoidCallbackFunc  # void (*f_g0_2d4d)()
    f_gout: VoidCallbackFunc  # void (*f_gout)()
    opt: Ptr[CINTOpt]  # CINTOpt *opt

    # values are assigned during calculation
    idx: Ptr[int]  # int *idx
    ai: CArray[float]  # double ai[1]
    aj: CArray[float]  # double aj[1]
    ak: CArray[float]  # double ak[1]
    al: CArray[float]  # double al[1]
    fac: CArray[float]  # double fac[1]
    rij: CArray[float]  # double rij[3]
    rkl: CArray[float]  # double rkl[3]

# Length and counting functions
def CINTlen_cart(l: int) -> int: ...
def CINTlen_spinor(bas_id: int, bas: Ptr[int]) -> int: ...
def CINTcgtos_cart(bas_id: int, bas: Ptr[int]) -> int: ...
def CINTcgtos_spheric(bas_id: int, bas: Ptr[int]) -> int: ...
def CINTcgtos_spinor(bas_id: int, bas: Ptr[int]) -> int: ...
def CINTcgto_cart(bas_id: int, bas: Ptr[int]) -> int: ...
def CINTcgto_spheric(bas_id: int, bas: Ptr[int]) -> int: ...
def CINTcgto_spinor(bas_id: int, bas: Ptr[int]) -> int: ...
def CINTtot_pgto_spheric(bas: Ptr[int], nbas: int) -> int: ...
def CINTtot_pgto_spinor(bas: Ptr[int], nbas: int) -> int: ...
def CINTtot_cgto_cart(bas: Ptr[int], nbas: int) -> int: ...
def CINTtot_cgto_spheric(bas: Ptr[int], nbas: int) -> int: ...
def CINTtot_cgto_spinor(bas: Ptr[int], nbas: int) -> int: ...

# Offset functions
def CINTshells_cart_offset(ao_loc: CArray[int], bas: Ptr[int], nbas: int) -> None: ...
def CINTshells_spheric_offset(
    ao_loc: CArray[int], bas: Ptr[int], nbas: int
) -> None: ...
def CINTshells_spinor_offset(ao_loc: CArray[int], bas: Ptr[int], nbas: int) -> None: ...

# Transformation functions
def CINTc2s_bra_sph(
    sph: Ptr[float], nket: int, cart: Ptr[float], l: int
) -> Ptr[float]: ...
def CINTc2s_ket_sph(
    sph: Ptr[float], nket: int, cart: Ptr[float], l: int
) -> Ptr[float]: ...
def CINTc2s_ket_sph1(
    sph: Ptr[float], cart: Ptr[float], lds: int, ldc: int, l: int
) -> Ptr[float]: ...

# Normalization function
def CINTgto_norm(n: int, a: float) -> float: ...

# Optimizer management functions
def CINTinit_2e_optimizer(
    opt: Ptr[Ptr[CINTOpt]],
    atm: Ptr[int],
    natm: int,
    bas: Ptr[int],
    nbas: int,
    env: Ptr[float],
) -> None: ...
def CINTinit_optimizer(
    opt: Ptr[Ptr[CINTOpt]],
    atm: Ptr[int],
    natm: int,
    bas: Ptr[int],
    nbas: int,
    env: Ptr[float],
) -> None: ...
def CINTdel_2e_optimizer(opt: Ptr[Ptr[CINTOpt]]) -> None: ...
def CINTdel_optimizer(opt: Ptr[Ptr[CINTOpt]]) -> None: ...

# Two-electron integral functions
def cint2e_cart(
    opijkl: Ptr[float],
    shls: Ptr[int],
    atm: Ptr[int],
    natm: int,
    bas: Ptr[int],
    nbas: int,
    env: Ptr[float],
    opt: Ptr[CINTOpt],
) -> int: ...
def cint2e_cart_optimizer(
    opt: Ptr[Ptr[CINTOpt]],
    atm: Ptr[int],
    natm: int,
    bas: Ptr[int],
    nbas: int,
    env: Ptr[float],
) -> None: ...
def cint2e_sph(
    opijkl: Ptr[float],
    shls: Ptr[int],
    atm: Ptr[int],
    natm: int,
    bas: Ptr[int],
    nbas: int,
    env: Ptr[float],
    opt: Ptr[CINTOpt],
) -> int: ...
def cint2e_sph_optimizer(
    opt: Ptr[Ptr[CINTOpt]],
    atm: Ptr[int],
    natm: int,
    bas: Ptr[int],
    nbas: int,
    env: Ptr[float],
) -> None: ...
def cint2e(
    opijkl: Ptr[float],
    shls: Ptr[int],
    atm: Ptr[int],
    natm: int,
    bas: Ptr[int],
    nbas: int,
    env: Ptr[float],
    opt: Ptr[CINTOpt],
) -> int: ...
def cint2e_optimizer(
    opt: Ptr[Ptr[CINTOpt]],
    atm: Ptr[int],
    natm: int,
    bas: Ptr[int],
    nbas: int,
    env: Ptr[float],
) -> None: ...

# Spinor transformation functions
def CINTc2s_ket_spinor_sf1(
    gspa: Ptr[np.complex128],
    gspb: Ptr[np.complex128],
    gcart: Ptr[float],
    lds: int,
    ldc: int,
    nctr: int,
    l: int,
    kappa: int,
) -> None: ...
def CINTc2s_iket_spinor_sf1(
    gspa: Ptr[np.complex128],
    gspb: Ptr[np.complex128],
    gcart: Ptr[float],
    lds: int,
    ldc: int,
    nctr: int,
    l: int,
    kappa: int,
) -> None: ...
def CINTc2s_ket_spinor_si1(
    gspa: Ptr[np.complex128],
    gspb: Ptr[np.complex128],
    gcart: Ptr[float],
    lds: int,
    ldc: int,
    nctr: int,
    l: int,
    kappa: int,
) -> None: ...
def CINTc2s_iket_spinor_si1(
    gspa: Ptr[np.complex128],
    gspb: Ptr[np.complex128],
    gcart: Ptr[float],
    lds: int,
    ldc: int,
    nctr: int,
    l: int,
    kappa: int,
) -> None: ...
