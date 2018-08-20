#!/usr/bin/python
# (c) 2018 Ian Leiman, ian.leiman@gmail.com
# vdw_calc.py
# GNU General Public License v3.0
# use at your own risk, no guarantees, no liability!
# github project https://github.com/eianlei
# Python-3 functions:
#    vdw_calc() calculates trimix blending using Van der Waals gas law instead of ideal gas law

def vdw_calc(filltype: object = "pp", start_bar: object = 0, end_bar: object = 200,
             start_o2: object = 21, start_he: object = 35, end_o2: object = 21, end_he: object = 35
             ) -> object:
    vdw_result = {'status_code': 99,  # 99 remains if something fatal happens
                  'status_text': 'Van Der Waals calculator not implemented yet\n',  # this is overwritten by something else
                  'tbar_2': 0,
                  'add_he': 0,
                  'add_o2': 0,
                  'add_nitrox': 0,
                  'nitrox_pct': 0,
                  'add_tmx': 0,
                  'tmx_o2_pct': 0,
                  'tmx_he_pct': 0,
                  'mix_o2_pct': 0,
                  'mix_he_pct': 0,
                  'mix_n_pct': 0
                  }

    return vdw_result