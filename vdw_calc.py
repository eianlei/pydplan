#!/usr/bin/python
# (c) 2018 Ian Leiman, ian.leiman@gmail.com
# vdw_calc.py
# GNU General Public License v3.0
# use at your own risk, no guarantees, no liability!
# github project https://github.com/eianlei
# Python-3 functions:
#    vdw_calc() calculates trimix blending using Van der Waals gas law instead of ideal gas law
#    this is placeholder - the function is not implemented yet"

import math
from scipy.optimize import fsolve

class GasMix():
    def __init__(self, o2_f, he_f, name, mols, pressure, temp_C, volume):
        self.o2_f = o2_f
        self.he_f = he_f
        self.n2_f = 1.0 - o2_f - he_f
        self.name = name
        self.mols = mols
        self.pressure = pressure
        self.temp_C = temp_C
        self.volume = volume
        self.vdw_a = 0.0
        self.vdw_b = 0.0

def ideal_gas_p(n, V, T):
    R= 0.0831451
    return n * R * T / V

def ideal_gas_n(p, V, T):
    R= 0.0831451
    return p * V /(R*T)

def van_der_waals_p(p, *args):
    n, V, T, a, b = args # unpack the args
    R= 0.0831451
    f = (p + (n*n * a) / (V*V)) * (V - (n * b)) - (n * R * T)
    return f

def van_der_waals_n(n, *args):
    p, V, T, a, b = args # unpack the args
    R= 0.0831451
    f = (p + (n*n * a) / (V*V)) * (V - (n * b)) - (n * R * T)
    return f

def vdw_mix_ab(o2_f, he_f, n2_f):
    ''' calculate vdw coefficients a and b for a mix of O2, N2, He
    input the fractions of each gas, return tuple
    '''
    mix_a = 0.0
    mix_b = 0.0
    x = [o2_f, n2_f, he_f]
    # https://en.wikipedia.org/wiki/Van_der_Waals_constants_(data_page)
    a = [1.382, 1.370, 0.0346]
    b = [0.03186, 0.03870, 0.0238]
    for i in range(3):
        for j in range(3):
            mix_a += math.sqrt( a[i]*a[j])* x[i]*x[j]
            mix_b += math.sqrt( b[i]*b[j])* x[i]*x[j]
    return mix_a, mix_b

def vdw_solve_pressure(mols, volume, o2_f, he_f, n2_f, temperature):
    '''
    returns the pressure of a gas mixture of o2, he, n2 by solving Van der Waals equation
    given mols, volume and temperature in Celsius
    :param mols:
    :type mols:
    :param volume:
    :type volume:
    :param o2_f:
    :type o2_f:
    :param he_f:
    :type he_f:
    :param n2_f:
    :type n2_f:
    :param temperature:
    :type temperature:
    :return:
    :rtype:
    '''
    temp_K = temperature +273.0
    mix_a, mix_b = vdw_mix_ab(o2_f, he_f, n2_f)
    seed_p = ideal_gas_p(n=mols, V=volume, T=temp_K)
    solved_p = fsolve(van_der_waals_p, seed_p, (mols, volume, temp_K, mix_a, mix_b))
    return solved_p

def vdw_solve_mols(pressure, volume, o2_f, he_f, n2_f, temperature):
    '''
    returns the total mols in a gas mixture of o2, he, n2 by solving Van der Waals equation
    given pressure, volume and temperature in Celsius
    :param pressure:
    :type pressure:
    :param volume:
    :type volume:
    :param o2_f:
    :type o2_f:
    :param he_f:
    :type he_f:
    :param n2_f:
    :type n2_f:
    :param temperature:
    :type temperature:
    :return:
    :rtype:
    '''
    temp_K = temperature +273.0
    mix_a, mix_b = vdw_mix_ab(o2_f, he_f, n2_f)
    seed_n = ideal_gas_n(pressure, volume, temp_K)
    solved_n = fsolve(van_der_waals_n, seed_n, (pressure, volume, temp_K, mix_a, mix_b))
    return solved_n

def vdw_calc(start_bar: float = 0.0, want_bar: float = 200.0,
             start_o2: float = 21.0, start_he: float = 35.0, want_o2: float = 21.0, want_he: float = 35.0,
             volume = 12.0, start_temp_c = 20.0,
             ) :
    '''
    calculates a partial pressure gas fill using Van der Waals gas law
    :param start_bar:
    :type start_bar:
    :param want_bar:
    :type want_bar:
    :param start_o2:
    :type start_o2:
    :param start_he:
    :type start_he:
    :param want_o2:
    :type want_o2:
    :param want_he:
    :type want_he:
    :param volume:
    :type volume:
    :param start_temp_c:
    :type start_temp_c:
    :return:
    :rtype:
    '''
    vdw_result = {'status_code': 99,  # 99 remains if something fatal happens
                  'status_text': 'Van Der Waals calculator not implemented yet\n',  # this is overwritten by something else
                  }
    # assume end temperature is same as start, could change this later to make things more complicated
    end_temp_c = start_temp_c
    # convert percentages to fractions (_f)
    start_o2_f = start_o2 / 100.0
    start_he_f = start_he / 100.0
    start_n2_f = 1.0 - start_o2_f - start_he_f # remaining part of gas is n2
    want_o2_f = want_o2 / 100.0
    want_he_f = want_he / 100.0
    want_n2_f = 1.0 - want_o2_f - want_he_f

    # how many mols of gas we have at start, in total and of each kind
    solve_start = vdw_solve_mols(start_bar, volume, start_o2_f, start_he_f, start_n2_f, start_temp_c)
    vdw_start_mols_all = solve_start[0]
    vdw_start_mols_o2 = vdw_start_mols_all * start_o2_f
    vdw_start_mols_he = vdw_start_mols_all * start_he_f
    vdw_start_mols_n2 = vdw_start_mols_all * start_n2_f
    # how many mols of gas we want to have, in total and of each kind
    solve_want_mols_all = vdw_solve_mols(want_bar, volume, want_o2_f, want_he_f, want_n2_f, end_temp_c)
    vdw_want_mols_all = solve_want_mols_all[0]
    vdw_want_mols_o2 = vdw_want_mols_all * want_o2_f
    vdw_want_mols_he = vdw_want_mols_all * want_he_f
    vdw_want_mols_n2 = vdw_want_mols_all * want_n2_f
    # how many mols we need to fill
    vdw_fill_mols_all = vdw_want_mols_all - vdw_start_mols_all
    vdw_fill_mols_o2 = vdw_want_mols_o2 - vdw_start_mols_o2
    vdw_fill_mols_he = vdw_want_mols_he - vdw_start_mols_he
    vdw_fill_mols_n2 = vdw_want_mols_n2 - vdw_start_mols_n2

    # first stage of filling is by helium, and we get a new mix "mix_he"
    mix_he_mols_all = vdw_start_mols_all + vdw_fill_mols_he # after filling he, we get this many mols total into new mix
    mix_he_o2_f = vdw_start_mols_o2 / mix_he_mols_all       # this mix has this new fraction of o2
    mix_he_he_f = vdw_want_mols_he  / mix_he_mols_all       #
    mix_he_n2_f = 1.0 - mix_he_o2_f - mix_he_he_f
    # then solve for pressure of this new mix
    solve_mix_helium_bars = vdw_solve_pressure(mix_he_mols_all, volume, mix_he_o2_f, mix_he_he_f, mix_he_n2_f, start_temp_c)
    mix_helium_bars = solve_mix_helium_bars[0]
    vdw_fill_he_bars = mix_helium_bars - start_bar # pressure of helium to fill

    # air is topped last, but we need to calculate how much we need it, so we can calculate for oxygen
    air_o2_mols_o2 = vdw_fill_mols_n2 * (0.21/0.79)    # this much o2 comes with the air we fill
    mix_o2_mols_o2 = vdw_fill_mols_o2 - air_o2_mols_o2 # this much extra o2 we need in mols
    mix_o2_mols_all = mix_he_mols_all + mix_o2_mols_o2 # total mols in the next mix
    mix_o2_o2_f = (mix_o2_mols_o2 + vdw_start_mols_o2) / mix_o2_mols_all
    mix_o2_he_f = vdw_want_mols_he / mix_o2_mols_all
    mix_o2_n2_f = 1.0 - mix_o2_o2_f - mix_o2_he_f
    # then solve for pressure of this new mix
    solve_mix_oxygen_bars = vdw_solve_pressure(mix_o2_mols_all, volume, mix_o2_o2_f, mix_o2_he_f, mix_o2_n2_f, start_temp_c)
    mix_oxygen_bars = solve_mix_oxygen_bars[0]
    vdw_fill_o2_bars = mix_oxygen_bars - mix_helium_bars # pressure of oxygen to fill

    # finally air
    vdw_fill_air_bars = want_bar - mix_oxygen_bars

    vdw_result['fill_he_bars']  = vdw_fill_he_bars
    vdw_result['fill_o2_bars']  = vdw_fill_o2_bars
    vdw_result['fill_air_bars'] = vdw_fill_air_bars

    start_mix = "Starting from {} bar with mix {:.0f}/{:.0f}/{:.0f} (O2/He/N).".format(
        start_bar, start_o2, start_he, (100 - start_o2 - start_he))
    result_mix = "Resulting mix will be {:.0f}/{:.0f}/{:.0f} (O2/He/N).".format(
        want_o2, want_he, 100-want_he-want_o2)
    he_fill = "From {:.1f} bars add {:.1f} bar Helium," \
        .format(start_bar, vdw_fill_he_bars)
    o2_fill = "From {:.1f} bars add {:.1f} bar Oxygen," \
        .format(mix_helium_bars, vdw_fill_o2_bars)

    result = "{}\n" \
             "Van der Waals blend:\n" \
             " - {}\n" \
             " - {}\n" \
             " - From {:.1f} bars add {:.1f} bar air to {:.1f} bar.  \n" \
             "{}\n".format(
        start_mix, he_fill, o2_fill, mix_oxygen_bars, vdw_fill_air_bars, want_bar, result_mix)
    vdw_result['status_text'] = result

    return vdw_result