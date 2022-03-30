import datetime
import re
from fhirpy import SyncFHIRClient
from fhirpy.base.searchset import *
from fhirpy.base.exceptions import ResourceNotFound
from dateutil.relativedelta import relativedelta

CLIENT = SyncFHIRClient('http://localhost:8080/fhir')


def get_resources(id, table, default_time, dataAliveTime):
    if table['type'].lower() == 'observation':
        # How to differentiate the code that user give is code or component-code?
        resources = CLIENT.resources('Observation')
        search = resources.search(subject=id, date__ge=(default_time - relativedelta(
            years=dataAliveTime['years'],
            months=dataAliveTime['months'],
            days=dataAliveTime['days'],
            hours=dataAliveTime['hours'],
            minutes=dataAliveTime['minutes'],
            seconds=dataAliveTime['seconds'])).strftime('%Y-%m-%d'), code=table['code']).sort('-date').limit(1)
        resources = search.fetch()
        is_in_component = False
        if len(resources) == 0:
            resources = CLIENT.resources('Observation')
            search = resources.search(subject=id, date__ge=(default_time - relativedelta(
                years=dataAliveTime['years'],
                months=dataAliveTime['months'],
                days=dataAliveTime['days'],
                hours=dataAliveTime['hours'],
                minutes=dataAliveTime['minutes'],
                seconds=dataAliveTime['seconds'])).strftime('%Y-%m-%d'), component_code=table['code']).sort('-date').limit(1)
            resources = search.fetch()
            is_in_component = True
            if len(resources) == 0:
                raise ResourceNotFound(
                    'Could not find the resources {code} under time {time}, no enough data for the patient'.format(code=table['code'], time=default_time - relativedelta(
                        years=dataAliveTime['years'],
                        months=dataAliveTime['months'],
                        days=dataAliveTime['days'],
                        hours=dataAliveTime['hours'],
                        minutes=dataAliveTime['minutes'],
                        seconds=dataAliveTime['seconds'])))
        for resource in resources:
            return {'resource': resource, 'is_in_component': is_in_component, 'component-code': table['code'] if is_in_component else '', 'type': 'laboratory'}

    elif table['type'].lower() == 'condition':
        resources = CLIENT.resources('Condition')
        search = resources.search(
            # subject=id, code=table['code']).sort('-date').limit(1) doesn't know why it would go wrong in HAPI
            subject=id, code=table['code']).limit(1)
        resources = search.fetch()
        if len(resources) == 0:  # 沒有此condition的搜尋結果
            return {'resource': None, 'is_in_component': False, 'type': 'diagnosis'}
        else:
            for resource in resources:
                return {'resource': resource, 'is_in_component': False, 'type': 'diagnosis'}

    else:
        raise Exception('unknown type of data')


def get_age(id, default_time):
    # TODO: 把取得Patient資料的這個流程加入到get_resources中
    # Getting patient data from server
    resources = CLIENT.resources('Patient')
    resources = resources.search(_id=id).limit(1)
    patient = resources.get()
    patient_birthdate = datetime.datetime.strptime(
        patient.birthDate, '%Y-%m-%d')
    # If we need the data that is 1 year before or so, return the real age at the time
    age = default_time - patient_birthdate
    return int(age.days / 365)


def get_resource_value(dictionary):
    # For value that are not a json format
    if type(dictionary) is not dict:
        return dictionary
    # dictionary = {'resource': resource, 'is_in_component': type(boolean), 'component-code': type(str), 'type': 'laboratory' or 'diagnosis'}
    if dictionary['type'] == 'diagnosis':
        return False if dictionary['resource'] is None else True
    elif dictionary['type'] == 'laboratory':
        # Two situation: one is to get the value of resource, the other is to get the value of resource.component
        if dictionary['is_in_component']:
            for component in dictionary['resource'].component:
                for coding in component.code.coding:
                    if coding.code == dictionary['component-code']:
                        return component.valueQuantity.value
        else:
            try:
                return dictionary['resource'].valueQuantity.value
            except KeyError:
                return dictionary['resource'].valueString


def get_resource_datetime(dictionary, default_time):
    # dictionary = {'resource': resource, 'is_in_component': type(boolean), 'component-code': type(str), 'type': 'laboratory' or 'diagnosis'}
    # 如果給過來的資料並非是object，就直接回傳該數值的time格式
    if type(dictionary) is not dict:
        return default_time.strftime("%Y-%m-%d")

    if dictionary['type'] == 'diagnosis':
        try:
            return returnDateTimeFormatter(dictionary['resource'].recordedDate)
        except AttributeError:
            return None
    elif dictionary['type'] == 'laboratory':
        try:
            return returnDateTimeFormatter(dictionary['resource'].effectiveDateTime)
        except KeyError:
            try:
                return returnDateTimeFormatter(dictionary['resource'].effectivePeriod.start)
            except KeyError:
                return None


def returnDateTimeFormatter(self):
    """
        This is a function that returns a standard DateTime format
        While using it, make sure the self parameter is datetime string
    """

    date_regex = '([0-9]([0-9]([0-9][1-9]|[1-9]0)|[1-9]00)|[1-9]000)(-(0[1-9]|1[0-2])(-(0[1-9]|[1-2][0-9]|3[0-1])))'
    dateTimeWithoutSec_regex = '([0-9]([0-9]([0-9][1-9]|[1-9]0)|[1-9]00)|[1-9]000)(-(0[1-9]|1[0-2])(-(0[1-9]|[1-2][0-9]|3[0-1])(T([01][0-9]|2[0-3]):[0-5][0-9])))'
    if type(self) == str:
        if re.search(dateTimeWithoutSec_regex, self):
            return self[:16]
        elif re.search(date_regex, self):
            return self[:10]+'T00:00'

    return None
