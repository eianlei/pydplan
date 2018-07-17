#!/usr/bin/python
# (c) 2018 Ian Leiman, ian.leiman@gmail.com
# tmx_calc.py
# GNU General Public License v3.0
# use at your own risk, no guarantees, no liability!
# github project https://github.com/eianlei/trimix-fill/
# Python-3 functions:
#    tmx_calc() calculates trimix blending for 3 different fill methods
#    tmx_cost_calc() calculates the cost of filling
def tmx_calc(filltype: object = "pp", start_bar: object = 0, end_bar: object = 200,
             start_o2: object = 21, start_he: object = 35, end_o2: object = 21, end_he: object = 35,
             he_ignore: object = False, o2_ignore: object = False) -> object:
    """calculates trimix blending for 3 different fill methods"""
    # input parameters:
    #  filltype: {pp, cfm, tmx}
    #       pp = partial pressure, He + O2 + air
    #       cfm= decant Helium + continuous flow Nitrox,
    #       tmx = tmx cfm
    #       air = plain air fill, ignore targets, calculate mix we get
    #       nx = plain Nitrox CFM fill, ignore helium target
    #  start_bar: tank start pressure in bar, must be >=0 and <= 300
    #  end_bar: tank end pressure in bar, must be >=0 and <= 300
    #  start_o2: tank starting o2%, must be >=0 and <= 100
    #  start_he: tank starting he%, must be >=0 and <= 100
    #  end_o2: wanted 02%, must be >=0 and <= 100
    #  end_he: wanted he%, must be >=0 and <= 100
    #  he_ignore: boolean, true = ignore helium target, plain Nitrox fill
    #  o2_ignore: boolean, true = ignore oxygen target, plain AIR fill
    #
    # return dictionary tmx_result, following keys:
    #  status_code: 0 if all OK, 10...20 input errors 50...60 calculation errors, 99 fatal
    #  status_text: human readable output text, error or result
    #  tbar_2 : for pp fill, the 2nd pressure in bar to fill Helium
    #  add_he: how many bars Helium to pp fill
    #  add_o2 : how many bars Oxygen to pp fill
    #  add_nitrox : how many bars Nitrox to fill by CFM
    #  nitrox_pct : O2% of Nitrox in CFM fill
    #  add_tmx : how many bars TMX to in TMX CFM
    #  tmx_o2_pct :  O2% of TMX to fill
    #  tmx_he_pct :  He% of TMX to fill
    #  mix_o2_pct : resulting O2%, should match end_o2
    #  mix_he_pct : resulting He%, should match end_he
    #  mix_n_pct : resulting N2%
    # TODO: support also imperial units output, ie. PSI instead of BAR
    # input uses only percentages and is PSI/BAR agnostic
    ##########################################################################
    # define the return values dictionary tmx_result
    # initialize with default values
    tmx_result = {'status_code': 99,  # 99 remains if something fatal happens
                  'status_text': 'FATAL ERROR\n',  # this is overwritten by something else
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

    # error checking for input values, anything wrong and we return an error & skip calculations
    if filltype not in ['pp', 'cfm', 'tmx', 'air', 'nx'] :
        tmx_result['status_code'] = 10
        tmx_result['status_text'] = 'ERROR: filltype not supported <' + filltype + '>\n'
        return tmx_result
    if start_bar < 0 :
        tmx_result['status_code'] = 11
        tmx_result['status_text'] = 'ERROR: tank start pressure cannot be <0\n'
        return tmx_result
    if  end_bar < 0 :
        tmx_result['status_code'] = 12
        tmx_result['status_text'] = 'ERROR: tank end pressure cannot be <0\n'
        return tmx_result
    if start_bar > 300 :
        tmx_result['status_code'] = 13
        tmx_result['status_text'] = "ERROR: tank start pressure in Bar cannot be > 300\n"
        return tmx_result
    if end_bar > 301 :
        tmx_result['status_code'] = 14
        tmx_result['status_text'] = "ERROR: tank end pressure in Bar cannot be > 300\n"
        return tmx_result

    if end_bar <= start_bar :
        tmx_result['status_code'] = 15
        tmx_result['status_text'] = "ERROR: wanted tank end pressure must be higher than start pressure\n"
        return tmx_result
    if start_o2 < 0 :
        tmx_result['status_code'] = 16
        tmx_result['status_text'] = "ERROR: starting oxygen content cannot be <0%\n"
        return tmx_result
    if start_he < 0 :
        tmx_result['status_code'] = 17
        tmx_result['status_text'] = "ERROR: starting helium content cannot be <0%\n"
        return tmx_result
    if end_o2 < 0 :
        tmx_result['status_code'] = 18
        tmx_result['status_text'] = "ERROR: wanted oxygen content cannot be <0%\n"
        return tmx_result
    if end_he < 0 :
        tmx_result['status_code'] = 19
        tmx_result['status_text'] = "ERROR: wanted helium content cannot be <0%\n"
        return tmx_result
    if start_o2 > 100 :
        tmx_result['status_code'] = 20
        tmx_result['status_text'] = "ERROR: starting oxygen content cannot be >100%\n"
        return tmx_result
    if start_he > 100 :
        tmx_result['status_code'] = 21
        tmx_result['status_text'] = "ERROR: starting helium content cannot be >100%\n"
        return tmx_result
    if end_o2 > 100 :
        tmx_result['status_code'] = 22
        tmx_result['status_text'] = "ERROR: wanted oxygen content cannot be >100%\n"
        return tmx_result
    if end_he > 100 :
        tmx_result['status_code'] = 23
        tmx_result['status_text'] = "ERROR: wanted helium content cannot be >100%\n"
        return tmx_result
    if start_o2 + start_he > 100 :
        tmx_result['status_code'] = 24
        tmx_result['status_text'] = "ERROR: starting O2 + He percentage cannot exceed 100%\n"
        return tmx_result
    if end_o2 + end_he > 100 :
        tmx_result['status_code'] = 25
        tmx_result['status_text'] = "ERROR: wanted O2 + He percentage cannot exceed 100%\n"
        return tmx_result

    # check if filling just air
    if filltype == "air" :
        o2_ignore = True
        he_ignore = True
    # check if filling just Nitrox
    if filltype == "nx" :
        he_ignore = True


    # do the calculations
    start_he_bar = start_bar * start_he / 100 # how many bars Helium in tank at start?
    # two cases: for plain Nitrox and actual Trimix fill
    if he_ignore:
        # calculate for Nitrox fill, igonore end_he target, no Helium is going in
        end_he_bar = start_he_bar             # not add any He, so at the end we have same He bar
        end_he = 100 * start_he_bar / end_bar # % He after the tank is filled full
        add_he = 0                            # no Helium will be added
        # end he_ignore == True
    else:
        # calculate for a trimix fill, Helium is added
        end_he_bar = end_bar * end_he / 100   # how may bar He me want to have after fill
        add_he = end_he_bar - start_he_bar    # how many bar of He we need to add
        # end else he_ignore == False
    # COMMON PART OF CALCULATIONS
    # tbar_2 is the tank pressure after we have filled Helium with PP method
    tbar_2 = start_bar + add_he               # if he_ignore : add_he=0, and then tbar_2 = start_bar

    # are we not adding any oxygen?
    if o2_ignore :
        add_air = end_bar - start_bar         # if o2_ignore then just top with air
        tbar_3 = start_bar
        add_o2 = 0
    else :
        # how many bar of air we must top after Helium and Oxygen are in
        add_air = (end_bar * (1 - end_he / 100 - end_o2 / 100)
               - start_bar * (1 - start_o2 / 100 - start_he / 100)) / 0.79
        tbar_3 = end_bar - add_air                # tbar_3 is pressure after He+O2 is in before topping air
        add_o2 = tbar_3 - tbar_2                  # how many bar O2 we need to fill before air
    # end else
    start_o2_bar = start_bar * start_o2 / 100 # how many bars O2 in tank at start?
    # we have now calculated all output needed for pp fill case
    # now we can verify the end mix, we can later check if we get what we want
    mix_o2_pct = 100 * (start_o2_bar + add_o2 + add_air * 0.21) / end_bar
    mix_he_pct = 100 * (start_he_bar + add_he) / end_bar
    mix_n_pct = 100 - mix_he_pct - mix_o2_pct
    # additional output needed for cfm fill case
    add_nitrox = end_bar - tbar_2             # bars of Nitrox after Helium is in
    end_o2_bar = end_bar * end_o2 / 100       # bars of Oxygen that the Nitrox needs to contain
    nitrox_pct = 100 * ((end_o2_bar - start_o2_bar) / add_nitrox) # %O2 of the Nitrox needed
    # additional output needed for tmx fill case
    add_tmx = end_bar - start_bar             # bars of TMX mix we need to fill
    tmx_he_pct = 100 * (end_he_bar - start_he_bar) / add_tmx  # %He that the TMX needs to have
    tmx_o2_pct = 100 * (end_o2_bar - start_o2_bar) / add_tmx  # %O2 that the TMX needs to have
    tmx_preo2_pct = tmx_o2_pct * ((100 - tmx_he_pct) / 100)   # what the O2 analyzer shows at start

    # error checking for results, anything wrong and we return error code
    if (filltype in ("cfm","nx"))  and nitrox_pct < 21:
        tmx_result['status_code'] = 52
        tmx_result['status_text'] = "ERROR: Nitrox CFM O2% <21% cannot be made!\n"\
        " - would require {:.1f}% O2 CFM input\n".format(nitrox_pct)
        return tmx_result
    if (filltype in ("cfm","nx")) and nitrox_pct > 36:
        tmx_result['status_code'] = 53
        tmx_result['status_text'] = "ERROR: Nitrox CFM O2% >36% cannot be made!\n" \
        " - would require {:.1f}% O2 CFM input\n".format(nitrox_pct)
        return tmx_result

    if filltype == "tmx" and tmx_he_pct > 36:
        tmx_result['status_code'] = 54
        tmx_result['status_text'] = "ERROR: Trimix CFM Helium % >36% cannot be made!\n"
        return tmx_result
    if filltype == "tmx" and tmx_o2_pct > 36:
        tmx_result['status_code'] = 55
        tmx_result['status_text'] = "ERROR: Trimix CFM where Oxygen % >36% cannot be made!\n"
        return tmx_result
    if filltype == "tmx" and tmx_preo2_pct < 12:
        tmx_result['status_code'] = 56
        tmx_result['status_text'] = "ERROR: Trimix CFM where Oxygen % <18% cannot be made!\n"
        return tmx_result

    ## impossible mixes
    if add_he < 0  :
        tmx_result['status_code'] = 61
        tmx_result['status_text'] = \
            "ERROR: Blending this mix is not possible!\n" \
            " negative Helium \n" \
            "<add_he {}, add_o2 {}, add_air {}> \n".format(add_he, add_o2, add_air)
        return tmx_result
    if add_o2 < -0.000000001 :
        tmx_result['status_code'] = 62
        tmx_result['status_text'] = \
            "ERROR: Blending this mix is not possible!\n" \
            " - starting O2% is {:.1f}% and you want {:.1f}% \n" \
            " - removing {:.1f} bar O2 is not possible \n".format(start_o2, end_o2, add_o2)
        return tmx_result
    if add_air < 0 :
        tmx_result['status_code'] = 63
        tmx_result['status_text'] = \
            "ERROR: Blending this mix is not possible!\n" \
            " negative Air \n" \
            "<add_he {}, add_o2 {}, add_air {}> \n".format(add_he, add_o2, add_air)
        return tmx_result


    # since we are here, then all error checking has passed, and numerical results should be valid
    # build nice text to return at tmx_result['status_text']
    if add_he > 0:
        he_fill = "From {:.1f} bars add {:.1f} bar Helium," \
            .format(start_bar, add_he)
    else:
        he_fill = " - no helium added"
    if add_o2 > 0.1:
        o2_fill = "From {:.1f} bars add {:.1f} bar Oxygen," \
            .format(tbar_2, add_o2)
    else:
        o2_fill = " - no oxygen added"
    if add_nitrox > 0:
        nitrox_fill = "From {:.1f} bars add {:.1f} bar {:.1f}% NITROX BY CFM,"\
            .format(tbar_2, add_nitrox, nitrox_pct)
    else:
        nitrox_fill = " - no Nitrox added"
    if add_tmx > 0:
        tmx_fill = "From {:.1f} bars add {:.1f} bar {:.1f}/{:.1f} TRIMIX BY CFM,"\
            .format(start_bar, add_tmx, tmx_o2_pct, tmx_he_pct)
    else:
        tmx_fill = " - no Trimix added"

    result_mix = "Resulting mix will be {:.0f}/{:.0f}/{:.0f} (O2/He/N).".format(
        mix_o2_pct, mix_he_pct, mix_n_pct)
    if start_bar > 0 :
        start_mix = "Starting from {} bar with mix {:.0f}/{:.0f}/{:.0f} (O2/He/N).".format(
            start_bar, start_o2, start_he, (100-start_o2-start_he) )
    else :
        start_mix = "Starting from EMPTY TANK "

    # # sanity check, what are we actually making and what not
    if filltype == "tmx" and add_he == 0 :
        filltype = "nx" # NOT TRIMIX, just plain NX by CFM

    if add_o2 == 0 and add_he == 0 :
        filltype = "air" # we are filling only air for sure

    # finally build the output strings
    if filltype == "air" :
        result = "{}\n" \
                 "PLAIN AIR FILL:\n"\
                 " - no Helium \n"\
                 " - no extra Oxygen \n"\
                 " - From {:.1f} bars add {:.1f} bar air to {:.1f} bar.  \n"\
                 "{}\n".format(
                 start_mix, start_bar, add_air, end_bar, result_mix)

    elif filltype == "nx" :
        result = "{}\n"\
                 "Nitrox CFM FILL:\n" \
                 " - no Helium \n"\
                 " - Oxygen enriched \n" \
                 "{} \n" \
                 "{}\n".format(
                start_mix, nitrox_fill, result_mix)

    elif filltype == "pp":
        result = "{}\n" \
                 "PARTIAL PRESSURE BLENDING:\n"\
                 " - {}\n"\
                 " - {}\n"\
                 " - From {:.1f} bars add {:.1f} bar air to {:.1f} bar.  \n"\
                 "{}\n".format(
                 start_mix, he_fill, o2_fill, tbar_3, add_air, end_bar, result_mix)

    elif filltype == "cfm":
        result = "{}\n" \
                 "Pure Helium + Nitrox CFM blending:\n"\
                 " - {}\n"\
                 " - {}\n"\
                 "{}\n".format(
                 start_mix, he_fill, nitrox_fill, result_mix)

    elif filltype == "tmx":
        result = \
                 "{}\n" \
                 "TMX CFM blending:\n"\
                 "{} \n"\
                 " - first open helium flow and adjust O2 to {:.1f}% \n"\
                 " - then open oxygen flow and adjust O2 to {:.1f}% \n"\
                 "{} \n".format(
                 start_mix, tmx_fill, tmx_preo2_pct, tmx_o2_pct, result_mix)

    ### now copy the calculated values from locals to dictionary we return
    tmx_result['status_code'] = 0         # ok, results are valid
    tmx_result['status_text'] = result    # human readable recipe text
    tmx_result['tbar_2'] = tbar_2
    tmx_result['add_he'] = add_he
    tmx_result['add_o2'] = add_o2
    tmx_result['add_nitrox'] = add_nitrox
    tmx_result['nitrox_pct'] = nitrox_pct
    tmx_result['add_tmx'] = add_tmx
    tmx_result['tmx_o2_pct'] = tmx_o2_pct
    tmx_result['tmx_he_pct'] = tmx_he_pct
    tmx_result['mix_o2_pct'] = mix_o2_pct
    tmx_result['mix_he_pct'] = mix_he_pct
    tmx_result['mix_n_pct'] = mix_n_pct
    return tmx_result
# end tmx_calc()

# tmx_cost_calc() calculates the cost of filling trimix
def tmx_cost_calc(liters, fill_bar, add_o2, add_he, o2_cost_eur, he_cost_eur, fill_cost_eur) :
     """calculate the cost of a trimix fill"""
     # input parameters
     #      liters : size of your tank to be filled in liters (water colume)
     #      fill_bar : end pressure of the tank in bars
     #      add_o2 : bars of pure oxygen filled (not including what is in air fill)
     #      add_he : bars of pure helium filled by pp or cfm
     #          note that remaining part of gas to fill is assumed to be air
     #      o2_cost_eur : cost of pure oxygen in Euros per cubic meter
     #      he_cost_eur : cost of pure helium in Euros per cubic meter
     #      fill_cost_eur : one time cost for using the compressor to top with air or cfm gas
     # TODO: could allow also air fill cost per liters filled, other currencies, imperial units
     # define the return values dictionary tmx_cost_result
     #      'status_code':
     #      'result_txt' :
     #      'cost' :
     # initialize with default values
     tmx_cost_result = {'status_code': 99,
                        'result_txt' : "ERROR",
                        'cost' : 0}

     # cost calculation
     o2_lit = liters * fill_bar * (add_o2 / fill_bar)
     he_lit = liters * fill_bar * (add_he / fill_bar)
     o2_eur = o2_lit * o2_cost_eur / 1000
     he_eur = he_lit * he_cost_eur / 1000
     total_cost_eur = fill_cost_eur + o2_eur + he_eur
     total_cost_string = \
        "Total cost of the fill is:\n{:.2f} EUR\n" \
        " - {:.0f} liters Oxygen costing {:.2f} EUR\n" \
        " - {:.0f} liters Helium costing {:.2f} EUR\n"\
        " - cfm/air fill costing {:.2f} EUR\n"\
        .format(total_cost_eur, o2_lit, o2_eur, he_lit, he_eur, fill_cost_eur)
     # return the results
     tmx_cost_result['cost'] =  total_cost_eur
     tmx_cost_result['status_code'] = 0 # OK
     tmx_cost_result['result_txt'] = total_cost_string
     return tmx_cost_result

def mod_calc(pp02 = 1.4, o2pct =21) :
    """calculates Maximum Operating Depth in meters for given ppO2 and o2%
    input ppO2 in bar/ATA and o2pct in percents"""
    mod_m = 10 * ((pp02 / (o2pct / 100))- 1)
    return mod_m
