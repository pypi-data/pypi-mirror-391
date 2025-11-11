import json

version_json = '''
{
 "author": "RL",
 "date": 2024.08,
 "version":"0.0.0"
}
'''


def get_versions():
    return json.loads(version_json)
