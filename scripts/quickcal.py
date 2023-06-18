import urllib.request
import json


# deltaR as calculated by 14chrono web app with respect to marine20 calibration curve - using the 9 data points nearest to Kirkwall
deltaR_orkney = -112
deltaR_orkney_error = 34

# note SUERC use -150 +/- 52 (see lab report for SUERC-100073 from The Cairns)
# note value is -268 +/- 98 calculated using http://calib.org/deltar/ and data from Ashcough 2006 (St Boniface)
# note value is ~ -300 +/- 60 calculated using http://calib.org/deltar/ and data from Ashcough 2006 and Ashcough 2017

def atmosphere_calibration(cj):
    return (calibrate_atmosphere_function(cj), parse_quickcal)

def marine_calibration(cj):
    return (calibrate_marine_function(cj), parse_marine_quickcal)

def mixed_calibration(cj):
    return (calibrate_mixed_function(cj), parse_mixed_quickcal)


def calibrate_atmosphere_function(cj):

	def create_data(sample_name, date_bp, error, floruits):
		options = 'Floruit=TRUE;' if floruits else ''
		qc_data = f'Options(){{{options}}};Plot(){{R_Date(\"{sample_name}\", {date_bp}, {error});}};'
		# print(qc_data)
		return qc_data.encode('utf-8')

	def qc_result(sample_name, date_bp, error, floruits):
		qc_data = create_data(sample_name, date_bp, error, floruits)
		return run_oxcal(qc_data, cj)

	return lambda sample_name, date_bp, error, floruits: qc_result(sample_name, date_bp, error, floruits)


def calibrate_marine_function(cj):

	def create_data(sample_name, date_bp, error, floruits):
		options = 'Floruit=TRUE;' if floruits else ''
		qc_data = f'Options(){{{options}}};Plot(){{Curve(\"Marine20\",\"marine20.14c\");Delta_R(\"LocalMarine\",{deltaR_orkney},{deltaR_orkney_error});R_Date(\"{sample_name}\", {date_bp}, {error});}};'
		# print(qc_data)
		return qc_data.encode('utf-8')

	def qc_result(sample_name, date_bp, error, floruits):
		qc_data = create_data(sample_name, date_bp, error, floruits)
		return run_oxcal(qc_data, cj)
	
	return lambda sample_name, date_bp, error, floruits: qc_result(sample_name, date_bp, error, floruits)


def calibrate_mixed_function(cj):

	def create_data(sample_name, date_bp, error, marine_ratio, marine_ratio_error, floruits):
		options = 'Floruit=TRUE;' if floruits else ''
		qc_data = f'Options(){{{options}}};Plot(){{Curve(\"IntCal20\",\"intcal20.14c\");Curve(\"Marine20\",\"marine20.14c\");Delta_R(\"LocalMarine\",{deltaR_orkney},{deltaR_orkney_error});Mix_Curves(\"Mixed\",\"IntCal20\",\"LocalMarine\",{marine_ratio},{marine_ratio_error});R_Date(\"{sample_name}\", {date_bp}, {error});}};'
		# print(qc_data)
		return qc_data.encode('utf-8')

	def qc_result(sample_name, date_bp, error, marine_ratio, marine_ratio_error, floruits):
        # note: might be better to get results from the "log" file (or another one?)
		qc_data = create_data(sample_name, date_bp, error, marine_ratio, marine_ratio_error, floruits)
		oxcal_result = run_oxcal(qc_data, cj)
		return oxcal_result

	return lambda sample_name, date_bp, error, marine_ratio, marine_ratio_error, floruits : qc_result(sample_name, date_bp, error, marine_ratio, marine_ratio_error, floruits)


def run_oxcal(qc_data, cj):
	store_model_url = 'https://c14.arch.ox.ac.uk/mydata/Quick.oxcal'
	store_model_req = urllib.request.Request(store_model_url, method='POST')
	store_model_req.add_header('Content-Type', 'test/plain;charset-UTF-8')
	cj.add_cookie_header(store_model_req)

	store_model_json = urllib.request.urlopen(store_model_req, data=qc_data).read()
	# expect {"status":true,"message":"Data written to file "}
	store_model_result = json.loads(store_model_json)
	if not store_model_result['status']:
		print('ERROR storing model')
		print('RESPONSE: ' + store_model_json)
		return store_model_json
	
	run_url = 'https://c14.arch.ox.ac.uk/mydata/Quick.oxcal?action=oxcal&lock=true'
	run_req = urllib.request.Request(run_url)
	cj.add_cookie_header(run_req)
	run_json = urllib.request.urlopen(run_req).read()
	run_result = json.loads(run_json)
	if not run_result['status']:
		print('ERROR running oxcal')
		print('RESPONSE: ' + run_json)

	qc_url = 'https://c14.arch.ox.ac.uk/mydata/Quick.js'
	qc_req = urllib.request.Request(qc_url)
	cj.add_cookie_header(qc_req)
	qc_js = urllib.request.urlopen(qc_req).read()

	return qc_js


def parse_quickcal(qc_lines):
    return parse_qc_lines(qc_lines, 'ocd[1].')


def parse_qc_lines(qc_lines, ocd_prefix):
    name = ''
    date = ''
    error = ''
    likelihood_comments = []

    for line in qc_lines:
        if line.endswith('\n'):
            line = line[:-1]
        if line.endswith(';'):
            line = line[:-1]

        if line.startswith(ocd_prefix):
            (variable, value) = line.split('=')

            variable = variable[len(ocd_prefix):]
            # print (variable)
            # print (value)

            if value.startswith('"') and value.endswith('"'):
                value = value[1:-1]

            if variable == 'name':
                name = value
            elif variable == 'date':
                date = int(value)
            elif variable == 'error':
                error = int(value)
            elif variable.startswith('likelihood.comment['):
                likelihood_comments.append(value)

    return (name, date, error, likelihood_comments)


def parse_likelihood_comments(likelihood_comments, quantiles):
	if quantiles:
		return parse_likelihood_comments_for_quantiles(likelihood_comments)
	else:
		return parse_likelihood_comments_for_segments(likelihood_comments)


def parse_likelihood_comments_for_segments(likelihood_comments):
    # print('parse likelihood comments')
    (segments_1s, segments_2s) = extract_segments(likelihood_comments)

    start_1s = None
    end_1s = None
    start_2s = None
    end_2s = None

    (start_1s, end_1s, segments_1s) = parse_segments(segments_1s)
    (start_2s, end_2s, segments_2s) = parse_segments(segments_2s)

    return (start_1s, end_1s, start_2s, end_2s, segments_1s, segments_2s)


def parse_likelihood_comments_for_quantiles(likelihood_comments):
    # print('parse likelihood comments for quantiles')
    (segments_1s, segments_2s) = extract_segments(likelihood_comments)

    start_1s = None
    end_1s = None
    start_2s = None
    end_2s = None

    (start_1s, end_1s, segments_1s) = parse_quantile(segments_1s)
    (start_2s, end_2s, segments_2s) = parse_quantile(segments_2s)

    return (start_1s, end_1s, start_2s, end_2s, None, None)


def parse_segments(segments):
    # print(segments)
    start = None
    segment_string = ''
    first = True
    last_segment = None
    for segment in segments:
        # print(segment)
        last_segment = segment
        if first:
            first = False
            start = segment[:segment.index('(')].strip()
        segment_string += segment.strip() + '; '

    end = last_segment[last_segment.index(')') + 1:].strip()
    segment_string = segment_string[:-2]

    return (start, end, segment_string)

def parse_quantile(segments):
    # print(segments)
    if len(segments) != 1:
        print(str(len(segments)) + ' segments when there should be 1')
        return (None, None, None)
	
    segment = segments[0].strip()
    # print(segment)
    start = segment[:segment.index(' ')]
    end = segment[segment.index(' ') + 1:].strip()

    return (start, end, None)


def extract_segments(likelihood_comments):
    # print('extract segments')

    NEW = 0
    ONE_SIGMA = 1
    TWO_SIGMA = 2

    ONE_SIGMA_MARKER = '68.3% probability'
    TWO_SIGMA_MARKER = '95.4% probability'
    segments_1s = []
    segments_2s = []

    state = NEW
    for comment in likelihood_comments:
        if state == NEW:
            if ONE_SIGMA_MARKER in comment:
                state = ONE_SIGMA
            elif TWO_SIGMA_MARKER in comment:
                state = TWO_SIGMA
        elif state == ONE_SIGMA:
            if TWO_SIGMA_MARKER in comment:
                state = TWO_SIGMA
            else:
                segments_1s.append(comment.strip())
        elif state == TWO_SIGMA:
            if ONE_SIGMA_MARKER in comment:
                state = ONE_SIGMA
            else:
                segments_2s.append(comment.strip())
        else:
            raise Exception('Unexpected parse state')

    return (segments_1s, segments_2s)


def parse_marine_quickcal(qc_lines):
    # print('parse marine quickcal')
    return parse_qc_lines(qc_lines, 'ocd[3].')


def parse_mixed_quickcal(qc_lines):
    # print('parse mixed quickcal')
    return parse_qc_lines(qc_lines, 'ocd[5].')
