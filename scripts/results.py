from os import chdir
from os.path import dirname

import login
import workflow
import c14dates
import calibrated_dates
from csv import parse_csv_file, write_csv_file

c14_dates_filepath = './dataset/C14Dates.csv'
calibrated_dates_filepath = './results/CalibratedDates.csv'

def calculate():
    cj = login.with_command_line_credentials()
    calibrate(cj)
    process_models(cj)


def calibrate(cj = None):
    chdir(dirname(__file__) + "\\..")
    if cj == None:
        cj = login.with_command_line_credentials()
    
    cal_list = workflow.calibrate(cj, c14_record_list())

    # rebuild calibrations file
    write_csv_file(calibrated_dates.HEADER_LINE, cal_list, calibrated_dates_filepath)


def c14_record_list():
    c14_rows = parse_csv_file(c14_dates_filepath, True)
    return c14dates.c14_list(c14_rows)

def process_models(cj = None):
    chdir(dirname(__file__) + "\\..")
    if cj == None:
        cj = login.with_command_line_credentials()
    
    models = oxcal_models()
    for site in models.keys():
        for model in models[site]:
            process_model(site, model, cj)

def process_model(site, model, cj):
    model_filepath = f'models/{site}/{model}.oxcal'
    oxcal_filepath = f'{site}/{model}.oxcal'
    results_dir = f'results/{site}'
    workflow.process_model_files(model_filepath, oxcal_filepath, results_dir, cj)

def oxcal_models():
    return {
        'orkney': [
            'orkney_burials_under_cairns_plot',
            'orkney_burials_under_cairns_plot.quantile'
        ],
        'brough_road': [
            'brough_road_cairn_1_combination'
        ],
        'bu': [
            'bu_plot'
        ],
        'howe': [
            'howe_sequence',
            'howe_articulated_skeleton_combination'
        ],
        'knowe_of_skea': [
            'knowe_of_skea_floruit'
        ],
        'pierowall_quarry': [
            'pierowall_quarry_plot'
        ],
        'pool': [
            'pool_phase_6_plot'
        ],
        'quanterness': [
            'quanterness_plot'
        ],
        'skaill_deerness': [
            'skaill_deerness_site_6_sequence',
            'skaill_deerness_site_6_sequence.quantile'
        ],
        'st_boniface': [
            'st_boniface_plot'
        ],
        'westness': [
            'westness_pictish_floruit'
        ]
    }