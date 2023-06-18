from quickcal import atmosphere_calibration, marine_calibration, mixed_calibration, parse_likelihood_comments
import calibrated_dates
import oxcal_files
import time
import urllib
from util import clamp, ratio

# c14_dates_filepath = './data/C14Dates.csv'

# D13C_LAND = -20.6
# D13C_SEA = -12.0

# values used by SUERC (see lab report on SUERC-100073 from The Cairns)
# note they only use a mixed calibration if d13C > -20.0
D13C_LAND = -21.0
D13C_SEA = -12.5

D13C_MARINE_THRESHOLD = -20.0
MARINE_PC_ERROR = 10


def calibrate(cj, c14_records):
    (calibrate, parse) = atmosphere_calibration(cj)
    (mcalibrate, mparse) = marine_calibration(cj)
    (mix_calibrate, mix_parse) = mixed_calibration(cj)

    cal_list = []
    for c14 in c14_records:

        print(c14.lab_id)

        cal = calibrated_dates.CalibratedDate()
        cal.site_name = c14.site_name
        cal.sample_ref = c14.sample_ref
        cal.lab_id = c14.lab_id
        cal.bp = c14.bp
        cal.error = c14.error
        cal.human = c14.human
        cal.marine = c14.marine
        cal.d13C = c14.d13C
        cal.d15N = c14.d15N
        cal.CN = c14.CN


        # marine calibration also
        if c14.marine == 'yes':
            print('marine calibration')
            cal.marine_fraction = 1.00

            # CALIBRATION QUANTILES - MARINE (using floruits)
            mcal_output = mcalibrate(c14.lab_id, c14.bp, c14.error, True)
            mcal_text = mcal_output.decode()
            # print(mcal_text)

            mcal_lines = mcal_text.split('\n')
            (lab_id, bp, error, likelihood_comments) = mparse(mcal_lines)
            if lab_id != c14.lab_id or bp != c14.bp or error != c14.error:
                raise Exception('wrong result file?')
    
            (marine_cal_start_1s, marine_cal_end_1s, marine_cal_start_2s, marine_cal_end_2s, 
             marine_segments_1s_ignored, marine_segments_2s_ignored) = parse_likelihood_comments(likelihood_comments, True)

            cal.cal_start_2s = marine_cal_start_2s
            cal.cal_end_2s = marine_cal_end_2s
            cal.cal_start_1s = marine_cal_start_1s
            cal.cal_end_1s = marine_cal_end_1s


            # CALIBRATION SEGMENTS - MARINE
            mcal_output = mcalibrate(c14.lab_id, c14.bp, c14.error, False)
            mcal_text = mcal_output.decode()
            # print(mcal_text)

            mcal_lines = mcal_text.split('\n')
            (lab_id, bp, error, likelihood_comments) = mparse(mcal_lines)
            if lab_id != c14.lab_id or bp != c14.bp or error != c14.error:
                raise Exception('wrong result file?')
    
            (marine_cal_start_1s_ignored, marine_cal_end_1s_ignored, marine_cal_start_2s_ignored, marine_cal_end_2s_ignored, 
             marine_segments_1s, marine_segments_2s) = parse_likelihood_comments(likelihood_comments, False)

            cal.segments_1s = marine_segments_1s
            cal.segments_2s = marine_segments_2s

        elif c14.human == 'yes' and c14.d13C and c14.d13C > D13C_MARINE_THRESHOLD:
            print('mixed calibration')

            d13C = clamp(c14.d13C, D13C_LAND, D13C_SEA)
            marine_fraction = ratio(d13C, D13C_SEA, D13C_LAND)
            cal.marine_fraction = round(marine_fraction, 3)
            marine_pc = marine_fraction * 100

            # CALIBRATION QUANTILES - MIXED (using floruits)
            mix_output = mix_calibrate(c14.lab_id, c14.bp, c14.error, marine_pc, MARINE_PC_ERROR, True)
            mix_text = mix_output.decode()
            # print(mix_text)

            mix_lines = mix_text.split('\n')
            (lab_id, bp, error, likelihood_comments) = mix_parse(mix_lines)
            if lab_id != c14.lab_id or bp != c14.bp or error != c14.error:
                dump = open('./data/dump.oxcal', 'w')
                dump.write(mix_text)
                dump.close()
                raise Exception('wrong result file?')
            # print(likelihood_comments)

            (mix_cal_start_1s, mix_cal_end_1s, mix_cal_start_2s, mix_cal_end_2s, 
             mix_segments_1s_ignored, mix_segments_2s_ignored) = parse_likelihood_comments(likelihood_comments, True)

            cal.cal_start_2s = mix_cal_start_2s
            cal.cal_end_2s = mix_cal_end_2s
            cal.cal_start_1s = mix_cal_start_1s
            cal.cal_end_1s = mix_cal_end_1s


            # CALIBRATION SEGMENTS - MIXED
            mix_output = mix_calibrate(c14.lab_id, c14.bp, c14.error, marine_pc, MARINE_PC_ERROR, False)
            mix_text = mix_output.decode()
            # print(mix_text)

            mix_lines = mix_text.split('\n')
            (lab_id, bp, error, likelihood_comments) = mix_parse(mix_lines)
            if lab_id != c14.lab_id or bp != c14.bp or error != c14.error:
                dump = open('./data/dump.oxcal', 'w')
                dump.write(mix_text)
                dump.close()
                raise Exception('wrong result file?')
            # print(likelihood_comments)

            (mix_cal_start_1s_ignored, mix_cal_end_1s_ignored, mix_cal_start_2s_ignored, mix_cal_end_2s_ignored, 
             mix_segments_1s, mix_segments_2s) = parse_likelihood_comments(likelihood_comments, False)

            cal.segments_1s = mix_segments_1s
            cal.segments_2s = mix_segments_2s

        else:

            # CALIBRATION QUANTILES (using floruits)
            cal_output = calibrate(c14.lab_id, c14.bp, c14.error, True)
            cal_text = cal_output.decode()
            # print(cal_text)
            cal_lines = cal_text.split('\n')

            (lab_id, bp, error, likelihood_comments) = parse(cal_lines)
            # print(lab_id + '...')
            # print(likelihood_comments)
            if lab_id != c14.lab_id or bp != c14.bp or error != c14.error:
                dump = open('./data/dump.oxcal', 'x')
                dump.write(cal_text)
                dump.close()
                print('result for ' + lab_id)
                raise Exception('wrong result file?')

            (cal_start_1s, cal_end_1s, cal_start_2s, cal_end_2s, 
            segments_1s_ignored, segments_2s_ignored) = parse_likelihood_comments(likelihood_comments, True)

            cal.cal_start_2s = cal_start_2s
            cal.cal_end_2s = cal_end_2s
            cal.cal_start_1s = cal_start_1s
            cal.cal_end_1s = cal_end_1s


            # CALIBRATION SEGMENTS
            cal_output = calibrate(c14.lab_id, c14.bp, c14.error, False)
            cal_text = cal_output.decode()
            cal_lines = cal_text.split('\n')

            (lab_id, bp, error, likelihood_comments) = parse(cal_lines)
            # print(lab_id + '...')
            # print(likelihood_comments)
            if lab_id != c14.lab_id or bp != c14.bp or error != c14.error:
                dump = open('./data/dump.oxcal', 'x')
                dump.write(cal_text)
                dump.close()
                print('result for ' + lab_id)
                raise Exception('wrong result file?')

            (cal_start_1s_ignored, cal_end_1s_ignored, cal_start_2s_ignored, cal_end_2s_ignored, 
            segments_1s, segments_2s) = parse_likelihood_comments(likelihood_comments, False)
            cal.segments_1s = segments_1s
            cal.segments_2s = segments_2s


        cal_list.append(cal)

    return cal_list

def process_model_files(model_filepath, oxcal_filepath, results_dir, cj):
    oxcal_files.upload(model_filepath, oxcal_filepath, cj)
    run_model(oxcal_filepath, cj)
    store_model_results(oxcal_filepath, results_dir, cj)


def run_model(oxcal_filepath, cj):
    file_suffix = oxcal_filepath.rsplit('.', 1)[1]
    if (file_suffix != 'oxcal'):
        raise Exception('unexpected file suffix (.oxcal expected)')

    # (1) POST https://c14.arch.ox.ac.uk/mydata/<oxcal_filepath> BODY = .oxcal file

    # ASSUME FOR NOW THE ABOVE STEP IS NOT REQUIRED IF FILE IS ALREADY UPLOADED

    # (2) GET https://c14.arch.ox.ac.uk/mydata/<oxcal_filepath>?action=oxcal&lock=false
    #       expect response body {"status":true,"message":"OxCal running"}

    opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj))

    # NOTE: {oxcal_filepath} must already exist in oxcal file manager
    start_mcmc_url = f'https://c14.arch.ox.ac.uk/mydata/{oxcal_filepath}?action=oxcal&lock=false'
    opener.open(start_mcmc_url)
    # could check response here for JSON {"status":true,"message":"OxCal running"}

    # Poll while MCMC calculation is running
    # (3) GET https://c14.arch.ox.ac.uk/mydata/<oxcal_filepath> <- replace '.oxcal' with '.work'
    #       expect text response with info about MCMC progress (Content-Type: application/force-download)
    #       e.g.
    #       work.program="OxCal v4.4.4";
    #       work.operation="MCMC";
    #       work.done=56.8; work.passes=0; work.ok="Resolving order:  Finding R_Date Birm-765";
    #
    #       when calculation is finished, a 404 response is returned
    #       (oxcal seems to wait for 2 successive 404 responses)

    work_filepath = oxcal_filepath.replace('.oxcal', '.work')
    progress_url = f'https://c14.arch.ox.ac.uk/mydata/{work_filepath}'
    
    while True:
        try:
            progress_response = opener.open(progress_url)
            # could extract progress % and current step from response

        except urllib.error.HTTPError as error:
            if error.code == 404:
                break
        
        time.sleep(1)
    
    print('MCMC complete')


def store_model_results(oxcal_filepath, results_dir, cj):
    # (4) GET https://c14.arch.ox.ac.uk/mydata/<oxcal_filepath> <- replace '.oxcal' with '.js'

    oxcal_filename = oxcal_filepath.rsplit('/', 1)[1]
    local_filepath = results_dir + '/' + oxcal_filename

    oxcal_log_filepath = oxcal_filepath.replace('.oxcal', '.log')
    local_log_filepath = local_filepath.replace('.oxcal', '.log')

    oxcal_files.download(oxcal_log_filepath, local_log_filepath, cj)

    # QUESTION: Are the svg files generated automatically when running the model?
    # ANSWER: NO
    oxcal_svg_filepath = oxcal_filepath.replace('.oxcal', '.svg')
    local_svg_filepath = local_filepath.replace('.oxcal', '.svg')

    oxcal_files.download(oxcal_svg_filepath, local_svg_filepath, cj)

    return local_log_filepath
