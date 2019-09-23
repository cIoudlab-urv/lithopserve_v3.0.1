import os
import sys
from pywren_ibm_cloud.utils import version_str

RUNTIME_DEFAULT_35 = 'ibmfunctions/pywren:3.5'
RUNTIME_DEFAULT_36 = 'ibmfunctions/action-python-v3.6'
RUNTIME_DEFAULT_37 = 'ibmfunctions/action-python-v3.7'

RUNTIME_TIMEOUT_DEFAULT = 600000  # Default: 600000 milliseconds => 10 minutes
RUNTIME_MEMORY_DEFAULT = 256  # Default memory: 256 MB

FH_ZIP_LOCATION = os.path.join(os.getcwd(), 'pywren_ibmcf.zip')


def load_config(config_data):
    if 'runtime_memory' not in config_data['pywren']:
        config_data['pywren']['runtime_memory'] = RUNTIME_MEMORY_DEFAULT
    if 'runtime_timeout' not in config_data['pywren']:
        config_data['pywren']['runtime_timeout'] = RUNTIME_TIMEOUT_DEFAULT
    if 'runtime' not in config_data['pywren']:
        this_version_str = version_str(sys.version_info)
        if this_version_str == '3.5':
            config_data['pywren']['runtime'] = RUNTIME_DEFAULT_35
        elif this_version_str == '3.6':
            config_data['pywren']['runtime'] = RUNTIME_DEFAULT_36
        elif this_version_str == '3.7':
            config_data['pywren']['runtime'] = RUNTIME_DEFAULT_37

    if 'ibm_cf' not in config_data:
        raise Exception("ibm_cf section is mandatory in the configuration")

    required_parameters_0 = ('endpoint', 'namespace')
    required_parameters_1 = ('endpoint', 'namespace', 'api_key')
    required_parameters_2 = ('endpoint', 'namespace', 'namespace_id', 'ibm:iam_api_key')

    # Check old format. Convert to new format
    if set(required_parameters_0) <= set(config_data['ibm_cf']):
        endpoint = config_data['ibm_cf'].pop('endpoint')
        namespace = config_data['ibm_cf'].pop('namespace')
        api_key = config_data['ibm_cf'].pop('api_key', None)
        namespace_id = config_data['ibm_cf'].pop('namespace_id', None)
        region = endpoint.split('//')[1].split('.')[0].replace('-', '_')

        for k in list(config_data['ibm_cf']):
            # Delete unnecessary keys
            del config_data['ibm_cf'][k]

        config_data['ibm_cf']['regions'] = {}
        config_data['pywren']['compute_backend_region'] = region
        config_data['ibm_cf']['regions'][region] = {'endpoint': endpoint, 'namespace': namespace}
        if api_key:
            config_data['ibm_cf']['regions'][region]['api_key'] = api_key
        if namespace_id:
            config_data['ibm_cf']['regions'][region]['namespace_id'] = namespace_id
    # -------------------

    if 'ibm' in config_data and config_data['ibm'] is not None:
        config_data['ibm_cf'].update(config_data['ibm'])

    for region in config_data['ibm_cf']['regions']:
        if not set(required_parameters_1) <= set(config_data['ibm_cf']['regions'][region]) \
           and (not set(required_parameters_0) <= set(config_data['ibm_cf']['regions'][region])
           or 'namespace_id' not in config_data['ibm_cf']['regions'][region] or 'iam_api_key' not in config_data['ibm_cf']):
            raise Exception('You must provide {} or {} to access to IBM Cloud '
                            'Functions'.format(required_parameters_1, required_parameters_2))

    if 'compute_backend_region' not in config_data['pywren']:
        config_data['pywren']['compute_backend_region'] = list(config_data['ibm_cf']['regions'].keys())[0]

    cbr = config_data['pywren']['compute_backend_region']
    if cbr is not None and cbr not in config_data['ibm_cf']['regions']:
        raise Exception('Invalid Compute backend region: {}'.format(cbr))
