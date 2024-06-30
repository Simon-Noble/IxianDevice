import datetime
import json

date_format = '%Y-%m-%d %H:%M %z'
matches_path = 'matches.json'

matches = {}

with open(matches_path, 'r') as read_file:
    for key, match in json.load(read_file).items():
        dt = datetime.datetime.strptime(match['time'], date_format)
        match['time'] = dt
        matches[int(key)] = match


def get_matches():
    return matches


def save(match_id, match_data):
    matches[match_id] = match_data
    with open(matches_path, 'w') as write_file:
        json.dump(matches, write_file, indent=2, default=_converter)


def delete(match_id):
    if match_id in matches:
        del matches[match_id]
    with open(matches_path, 'w') as write_file:
        json.dump(matches, write_file, indent=2, default=_converter)


def _converter(o):
    if isinstance(o, datetime.datetime):
        return o.strftime(date_format)


def get_help(arg=''):
    path = 'help_' + arg + '.txt'
    try:
        return open(path, 'r').read()
    except FileNotFoundError:
        print('Help file not found: ' + path)
        return open('help.txt', 'r').read()


"""
with open('test.txt', 'w') as write_file:
    json.dump(loaded_data, write_file, indent=2)

def load():
    with open(matches_path, 'r') as rf:
        return json.load(rf)
"""
