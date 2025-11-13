###--------------------------###
###----- manager module -----###
###--------------------------###

'''
This module contains three classes:
    - ApiUser: Parent class
    - ApiAdmin: Child class and parent class, inherits from ApiUser
    - ApiRoot: Child class, inherits from ApiAdmin

These classes are used for interacting with the database through the API.
'''

### load modules
import requests
import json


#---------------------------------------------------------------------------#
#---------------------------------------------------------------------------#

###-------------------------###
###----- ApiUser class -----###

class ApiUser:

    def __init__(self, ip, token):
        self.session = requests.Session()

        self._ip = ip
        self._headers = {"Authorization": f"Bearer {token}"}
        
        self._role = self._get_user_role()
        self._organization = self._get_user_organization()

        self._url = None


    ###----- Utility methods -----###
    ###---------------------------###
    def _check_status_code(self, ret, status_code):
        '''
            Checks if the status code of the response is the expected one.
        '''
        
        if ret.status_code != status_code:
            error_message = {"status_code": ret.status_code, "detail": ret.json()['detail']}
            raise ValueError(error_message)
        else:
            return 0
    

    def _get_user_role(self, username=None):
        '''
            Returns the role of the user.
        '''

        url = f"{self._ip}/users/role"

        params = {}
        if username is not None:
            params['username'] = username

        ret = self.session.get(url, headers=self._headers, params=params)

        if self._check_status_code(ret, 200) == 1:
            ret = self.session.get(url, params=params, headers=self._headers)
        
        self._url = ret.url
        jsonret = ret.json()

        return jsonret
    

    def _get_user_organization(self, username=None):
        '''
            Returns user's organization.
        '''

        url = f"{self._ip}/users/organization"
        
        params = {}
        if username is not None:
            params['username'] = username

        ret = self.session.get(url, params=params, headers=self._headers)

        if self._check_status_code(ret, 200) == 1:
            ret = self.session.get(url, params=params, headers=self._headers)
        
        self._url = ret.url
        jsonret = ret.json()

        return jsonret
    

    ###----- datasets -----###
    ###--------------------###
    def _get_datasetname(self, title, scenario, organization=None):
        '''
            Returns the datasetname of the given title and scenario.
        '''

        if organization is None:
            organization = self._organization

        url = f"{self._ip}/organization/{organization}/dataset/datasetname"
        params = {
            "title": title,
            "scenario": scenario
        }

        ret = self.session.get(url, params=params, headers=self._headers)

        if self._check_status_code(ret, 200) == 1:
            ret = self.session.get(url, params=params, headers=self._headers)

        self._url = ret.url
        jsonret = ret.json()

        return jsonret
    

    def _select_datasetname(self, datasetname=None, title=None, scenario=None, organization=None):
        '''
            Checks if datasetname is None, if so, it returns the datasetname of the given title and scenario.
        '''
        if datasetname is None:
            if (title is not None) and (scenario is not None):
                return self._get_datasetname(title, scenario, organization)
            else:
                return None
        else:
            return datasetname
        

    def _get_datasetnames_list(self, orbit, geometry, organization=None):
        '''
            Returns a list of datasetnames.
        '''

        if organization is None:
            organization = self._organization

        url = f"{self._ip}/organization/{organization}/dataset/datasetnames"
        params = {
            'orbit': orbit,
            'geometry': geometry
        }
        
        ret = self.session.get(url, headers=self._headers, params=params)
        
        if self._check_status_code(ret, 200) == 1:
            ret = self.session.get(url, headers=self._headers)
        
        self._url = ret.url
        jsonret = ret.json()

        return jsonret
    

    def _select_datasetnames_list(self, datasetnames=None, orbit=None, geometry=None, organization=None):
        '''
            Returns a list of datasetnames.
        '''

        if datasetnames is None:
            if (orbit is not None) and (geometry is not None):
                return self._get_datasetnames_list(orbit, geometry, organization)
            else:
                return None
        else:
            return datasetnames
        

    ###----- properties -----###
    ###----------------------###
    def _get_property_id(self, datasetname=None, property=None, organization=None):
        '''
            Returns the property id of the given property.
        '''

        if organization is None:
            organization = self._organization

        url = f"{self._ip}/organization/{organization}/property/{property}/dataset/{datasetname}/property_id"
        params = {
            'datasetname': datasetname,
            'property': property
        }

        ret = self.session.get(url, headers=self._headers, params=params)

        if self._check_status_code(ret, 200) == 1:
            ret = self.session.get(url, headers=self._headers, params=params)

        self._url = ret.url
        jsonret = ret.json()

        return jsonret
    

    def _select_property_id(self, property_id=None, datasetname=None, property=None, organization=None):
        '''
            Returns the property id of the given property.
        '''

        if property_id is None:
            if (datasetname is not None) and (property is not None):
                return self._get_property_id(datasetname, property, organization)
            else:
                return None
        else:
            return property_id
    

    ###----- metrics -----###
    ###-------------------###
    def _get_metric_id(self, datasetname=None, metric=None, organization=None):
        '''
            Returns the metric id of the given metric.
        '''

        if organization is None:
            organization = self._organization

        url = f"{self._ip}/organization/{organization}/metric/{metric}/dataset/{datasetname}/metric_id"
        params = {
            'datasetname': datasetname,
            'metric': metric
        }

        ret = self.session.get(url, headers=self._headers, params=params)

        if self._check_status_code(ret, 200) == 1:
            ret = self.session.get(url, headers=self._headers, params=params)

        self._url = ret.url
        jsonret = ret.json()

        return jsonret
    

    def _select_metric_id(self, metric_id=None, datasetname=None, metric=None, organization=None):
        '''
            Returns the metric id of the given metric.
        '''

        if metric_id is None:
            if (datasetname is not None) and (metric is not None):
                return self._get_metric_id(datasetname, metric, organization)
            else:
                return None
        else:
            return metric_id
        

    def _select_metric_ids_list(self, metric_ids=None, metric=None, organization=None):
        '''
            Returns a list of metric ids.
        '''

        if metric_ids is None:
            metric_ids = []
            if metric is not None:
                for metric in self.get_metrics_metadata(metric=metric, organization=organization):
                    metric_ids.append(metric['metric_id'])
            return None if len(metric_ids) == 0 else metric_ids
        else:
            return metric_ids
                    

    ###----- models -----###
    ###------------------###
    def _get_model_id(self, datasetname=None, model=None, organization=None):
        '''
            Returns the model_id of the given model and datasetname.
        '''

        if organization is None:
            organization = self._organization

        url = f"{self._ip}/organization/{organization}/model/{model}/dataset/{datasetname}/model_id"

        ret = self.session.get(url, headers=self._headers)

        if self._check_status_code(ret, 200) == 1:
            ret = self.session.get(url, headers=self._headers)

        self._url = ret.url
        jsonret = ret.json()

        return jsonret
    

    def _select_model_id(self, model_id=None, datasetname=None, model=None, organization=None):
        '''
            Returns the model_id of the given model and datasetname.
        '''
        
        if model_id is None:
            if (datasetname is not None) and (model is not None):
                return self._get_model_id(datasetname, model, organization)
            else:
                return None
        else:
            return model_id
        

    def _get_kinetic_id(self, model_id=None, kinetic=None, organization=None):
        '''
            Returns the kinetic_id of the given kinetic and model_id.
        '''

        if organization is None:
            organization = self._organization

        url = f"{self._ip}/organization/{organization}/model/{model_id}/kinetic/{kinetic}/kinetic_id"

        ret = self.session.get(url, headers=self._headers)

        if self._check_status_code(ret, 200) == 1:
            ret = self.session.get(url, headers=self._headers)

        self._url = ret.url
        jsonret = ret.json()

        return jsonret
    

    def _select_kinetic_id(self, kinetic_id=None, model_id=None, kinetic=None, organization=None):
        '''
            Returns the kinetic_id of the given kinetic and model_id.
        '''
        
        if kinetic_id is None:
            if (model_id is not None) and (kinetic is not None):
                return self._get_kinetic_id(model_id, kinetic, organization)
            else:
                return None
        else:
            return kinetic_id
        

    ###----- exogenous -----###
    ###---------------------###
    def _get_exogenous_id(self, exogenous=None, scenario=None, organization=None):
        '''
            Returns the exogenous_id of the given exogenous and scenario.
        '''

        if organization is None:
            organization = self._organization

        url = f"{self._ip}/organization/{organization}/exogenous_id"
        params = {
            "exogenous": exogenous,
            "scenario": scenario
        }

        ret = self.session.get(url, headers=self._headers, params=params)

        if self._check_status_code(ret, 200) == 1:
            ret = self.session.get(url, headers=self._headers, params=params)

        self._url = ret.url
        jsonret = ret.json()

        return jsonret
        

    def _select_exogenous_id(self, exogenous_id=None, exogenous=None, scenario=None, organization=None):
        '''
            Returns the exogenous_id of the given exogenous.
        '''

        if exogenous_id is None:
            if (exogenous is not None) and (scenario is not None):
                return self._get_exogenous_id(exogenous, scenario, organization)
            else:
                return None
        else:
            return exogenous_id
        

    ###----- assignations -----###
    ###------------------------###
    def _get_assignation_id(self, datasetname=None, layer_id=None, assignation=None, organization=None):
        '''
            Returns the assignation id of the given assignation.
        '''

        if organization is None:
            organization = self._organization

        url = f"{self._ip}/organization/{organization}/dataset/{datasetname}/assignation_id"
        params = {
            "layer_id": layer_id,
            "assignation": assignation
        }

        ret = self.session.get(url, headers=self._headers, params=params)

        if self._check_status_code(ret, 200) == 1:
            ret = self.session.get(url, headers=self._headers, params=params)

        self._url = ret.url
        jsonret = ret.json()

        return jsonret
    

    def _select_assignation_id(self, assignation_id=None, datasetname=None, layer_id=None, assignation=None, organization=None):
        '''
            Returns the assignation id of the given assignation.
        '''

        if assignation_id is None:
            if (datasetname is not None) and (layer_id is not None) and (assignation is not None):
                return self._get_assignation_id(datasetname, layer_id, assignation, organization)
            else:
                return None
        else:
            return assignation_id
        

    def _select_assignation_ids_list(self, assignation_ids=None, assignation=None, organization=None):
        '''
            Returns a list of assignation ids.
        '''

        if assignation_ids is None:
            assignation_ids = []
            if assignation is not None:
                for assignation in self.get_assignations_metadata(assignation=assignation, organization=organization):
                    assignation_ids.append(assignation['assignation_id'])
            return None if len(assignation_ids) == 0 else assignation_ids
        else:
            return assignation_ids


    ###----- polygons -----###
    ###--------------------###
    def _get_polygon_layer_id(self, layer=None, scenario=None, organization=None):
        '''
            Returns the polygon layer id of the given layer and scenario.
        '''

        if organization is None:
            organization = self._organization

        url = f"{self._ip}/organization/{organization}/polygon/layer_id"
        params = {
            'layer': layer,
            'scenario': scenario
        }

        ret = self.session.get(url, headers=self._headers, params=params)

        if self._check_status_code(ret, 200) == 1:
            ret = self.session.get(url, headers=self._headers, params=params)

        self._url = ret.url
        jsonret = ret.json()

        return jsonret
    

    def _select_polygon_layer_id(self, layer_id=None, layer=None, scenario=None, organization=None):
        '''
            Returns the polygon layer id of the given layer and scenario.
        '''

        if layer_id is None:
            if (layer is not None) and (scenario is not None):
                return self._get_polygon_layer_id(layer, scenario, organization)
            else:
                return None
        else:
            return layer_id
    


    ###----------------------
    ##--------------------
    #--- usable methods

    
    ###----- datasets tables methods -----###
    ###-----------------------------------###
    def get_datasets_metadata(self, datasetname=None, title=None, scenario=None, organization=None):
        '''
            Returns a list of datasets metadata dictionaries.
        '''

        if organization is None:
            organization = self._organization

        datasetname = self._select_datasetname(datasetname, title, scenario, organization)
            
        url = f"{self._ip}/organization/{organization}/datasets"
        params = {
            "datasetname": datasetname
        }
        
        ret = self.session.get(url, headers=self._headers, params=params)
        
        if self._check_status_code(ret, 200) == 1:
            ret = self.session.get(url, headers=self._headers)

        self._url = ret.url
        jsonret = ret.json()

        return jsonret


    def get_dataset(self, datasetname=None, title=None, scenario=None, polygon=None, _ids=None, date_span=None, geometries=False, organization=None):
        '''
            Returns a dataset.
            If polygon and date_span are None, get all the points in the dataset.
            If polygon is given and date_span is None, get the points within the polygon.
            If polygon is None and date_span is given, get the points between the given date range.
            If polygon and date_span are given, get the points within the polygon and between the given date range.
            If _ids is given, only the time data of the given _ids is returned.
        '''

        if organization is None:
            organization = self._organization

        datasetname = self._select_datasetname(datasetname, title, scenario, organization)

        url = f"{self._ip}/organization/{organization}/dataset/{datasetname}"

        if polygon is not None:
            polygon = json.dumps(polygon)

        params = {
            'polygon': polygon,
            '_ids': _ids,
            'date_span': date_span,
            'geometries': geometries
        }

        ret = self.session.get(url, headers=self._headers, params=params)

        if self._check_status_code(ret, 200) == 1:
            ret = self.session.get(url, headers=self._headers, params=params)

        self._url = ret.url
        jsonret = ret.json()

        return jsonret


    ###----- properties tables methods -----###
    ###-------------------------------------###
    def get_properties_metadata(self, datasetname=None, title=None, scenario=None, property=None, organization=None):
        '''
            Returns a list of properties metadata dictionaries.
        '''

        if organization is None:
            organization = self._organization

        datasetname = self._select_datasetname(datasetname, title, scenario, organization)

        url = f"{self._ip}/organization/{organization}/properties"
        params = {
            'datasetname': datasetname,
            'property': property
        }

        ret = self.session.get(url, headers=self._headers, params=params)

        if self._check_status_code(ret, 200) == 1:
            ret = self.session.get(url, headers=self._headers)

        self._url = ret.url
        jsonret = ret.json()

        return jsonret


    def get_property(self, property_id=None, datasetname=None, title=None, scenario=None, property=None, polygon=None, _ids=None, geometries=False, organization=None):
        '''
            Returns a list of property values in dictionaries for a given dataset.
        '''

        if organization is None:
            organization = self._organization

        datasetname = self._select_datasetname(datasetname, title, scenario, organization)
        property_id = self._select_property_id(property_id, datasetname, property, organization)

        url = f"{self._ip}/organization/{organization}/property/{property_id}"

        if polygon is not None:
            polygon = json.dumps(polygon)

        params = {
            'polygon': polygon,
            '_ids': _ids,
            'geometries': geometries
        }

        ret = self.session.get(url, headers=self._headers, params=params)

        if self._check_status_code(ret, 200) == 1:
            ret = self.session.get(url, headers=self._headers, params=params)

        self._url = ret.url
        jsonret = ret.json()

        return jsonret


    ###----- metrics tables methods -----###
    ###----------------------------------###
    def get_metrics_metadata(self, datasetname=None, title=None, scenario=None, metric=None, organization=None):
        '''
            Returns a list of metrics metadata dictionaries.
        '''

        if organization is None:
            organization = self._organization

        datasetname = self._select_datasetname(datasetname, title, scenario, organization)

        url = f"{self._ip}/organization/{organization}/metrics"
        params = {
            'datasetname': datasetname,
            'metric': metric
        }

        ret = self.session.get(url, headers=self._headers, params=params)

        if self._check_status_code(ret, 200) == 1:
            ret = self.session.get(url, headers=self._headers, params=params)

        self._url = ret.url
        jsonret = ret.json()

        return jsonret
    

    def get_metric(self, datasetname=None, title=None, scenario=None, metric_id=None, metric=None, geometries=False, polygon=None, date_span=None, organization=None):
        '''
            Returns a list of metric values in dictionaries for a given dataset.
        '''

        if organization is None:
            organization = self._organization

        datasetname = self._select_datasetname(datasetname, title, scenario, organization)
        metric_id = self._select_metric_id(metric_id, datasetname, metric, organization)

        url = f"{self._ip}/organization/{organization}/metric/{metric_id}"

        if polygon is not None:
            polygon = json.dumps(polygon)

        params = {
            'geometries': geometries,
            'polygon': polygon,
            'date_span': date_span
        }

        ret = self.session.get(url, headers=self._headers, params=params)

        if self._check_status_code(ret, 200) == 1:
            ret = self.session.get(url, headers=self._headers, params=params)

        self._url = ret.url
        jsonret = ret.json()

        return jsonret
    

    ###----- models tables methods -----###
    ###---------------------------------###
    def get_models_metadata(self, datasetname=None, title=None, scenario=None, model_id=None, name=None, organization=None):
        '''
            Returns a list of models metadata dictionaries.
        '''
        
        if organization is None:
            organization = self._organization

        datasetname = self._select_datasetname(datasetname, title, scenario, organization)
        model_id = self._select_model_id(model_id, datasetname, name, organization)

        url = f"{self._ip}/organization/{organization}/models"
        params = {
            'datasetname': datasetname,
            'model_id': model_id
        }

        ret = self.session.get(url, headers=self._headers, params=params)

        if self._check_status_code(ret, 200) == 1:
            ret = self.session.get(url, headers=self._headers)

        self._url = ret.url
        jsonret = ret.json()

        return jsonret
    

    def get_kinetics_metadata(self, datasetname=None, title=None, scenario=None, model_id=None, model=None, kinetic_id=None, kinetic=None, organization=None):
        '''
            Returns a list of kinetics metadata dictionaries.
        '''

        if organization is None:
            organization = self._organization
            
        datasetname = self._select_datasetname(datasetname, title, scenario, organization)
        model_id = self._select_model_id(model_id, datasetname, model, organization)
        kinetic_id = self._select_kinetic_id(kinetic_id, model_id, kinetic, organization)

        url = f"{self._ip}/organization/{organization}/models/kinetics"
        params = {
            'datasetname': datasetname,
            'model_id': model_id,
            'kinetic_id': kinetic_id
        }

        ret = self.session.get(url, headers=self._headers, params=params)

        if self._check_status_code(ret, 200) == 1:
            ret = self.session.get(url, headers=self._headers, params=params)

        self._url = ret.url
        jsonret = ret.json()

        return jsonret
    

    def get_model_data(self, model_id=None, datasetname=None, title=None, scenario=None, model=None, kinetic_id=None, kinetic=None, _ids=None, geometries=False, polygon=None, organization=None):
        '''
            Returns a list of model data dictionaries.
        '''

        if organization is None:
            organization = self._organization

        datasetname = self._select_datasetname(datasetname, title, scenario, organization)
        model_id = self._select_model_id(model_id, datasetname, model, organization)
        kinetic_id = self._select_kinetic_id(kinetic_id, model_id, kinetic, organization)

        url = f"{self._ip}/organization/{organization}/model/{model_id}"

        if polygon is not None:
            polygon = json.dumps(polygon)

        params = {
            '_ids': _ids,
            'geometries': geometries,
            'polygon': polygon,
            'kinetic_id': kinetic_id
        }

        ret = self.session.get(url, headers=self._headers, params=params)

        if self._check_status_code(ret, 200) == 1:
            ret = self.session.get(url, headers=self._headers, params=params)

        self._url = ret.url
        jsonret = ret.json()

        return jsonret


    ###----- exogenous tables methods -----###
    ###------------------------------------###
    def get_exogenous_metadata(self, scenario=None, exogenous_id=None, exogenous=None, organization=None):
        '''
            Returns a list of exogenous metadata dictionaries.
        '''

        if organization is None:
            organization = self._organization

        exogenous_id = self._select_exogenous_id(exogenous_id, exogenous, scenario, organization)

        url = f"{self._ip}/organization/{organization}/exogenous"
        params = {
            'scenario': scenario,
            'exogenous_id': exogenous_id
        }

        ret = self.session.get(url, headers=self._headers, params=params)

        if self._check_status_code(ret, 200) == 1:
            ret = self.session.get(url, headers=self._headers, params=params)

        self._url = ret.url

        jsonret = ret.json()

        return jsonret


    def get_exogenous_geometries(self, exogenous_id=None, exogenous=None, scenario=None, polygon=None, organization=None):
        '''
            Returns a list of exogenous geometries in dictionaries.
        '''

        if organization is None:
            organization = self._organization
            
        exogenous_id = self._select_exogenous_id(exogenous_id, exogenous, scenario, organization)

        url = f"{self._ip}/organization/{organization}/exogenous/geometries"

        if polygon is not None:
            polygon = json.dumps(polygon)

        params = {
            'exogenous_id': exogenous_id,
            'polygon': polygon
        }

        ret = self.session.get(url, headers=self._headers, params=params)

        if self._check_status_code(ret, 200) == 1:
            ret = self.session.get(url, headers=self._headers, params=params)

        self._url = ret.url
        
        jsonret = ret.json()

        return jsonret
    

    def get_exogenous_data(self, exogenous_id=None, geometry_id=None, exogenous=None, scenario=None, polygon=None, date_span=None, geometries=None, organization=None):
        '''
            Returns a list of exogenous data in dictionaries.
        '''

        if organization is None:
            organization = self._organization

        exogenous_id = self._select_exogenous_id(exogenous_id, exogenous, scenario, organization)

        url = f"{self._ip}/organization/{organization}/exogenous/{exogenous_id}/data"

        if polygon is not None:
            polygon = json.dumps(polygon)

        params = {
            'geometry_id': geometry_id,
            'polygon': polygon,
            'date_span': date_span,
            'geometries': geometries
        }

        ret = self.session.get(url, headers=self._headers, params=params)

        if self._check_status_code(ret, 200) == 1:
            ret = self.session.get(url, headers=self._headers, params=params)

        self._url = ret.url

        jsonret = ret.json()

        return jsonret
    

    ###----- assignations tables methods -----###
    ###---------------------------------------###
    def get_assignations_metadata(self, datasetname=None, title=None, scenario=None, assignation_id=None, assignation=None, layer_id=None, layer=None, organization=None):
        '''
            Returns a list of assignations metadata dictionaries.
        '''

        if organization is None:
            organization = self._organization

        datasetname = self._select_datasetname(datasetname, title, scenario, organization)
        layer_id = self._select_polygon_layer_id(layer_id, layer, scenario, organization)
        assignation_id = self._select_assignation_id(assignation_id, datasetname, layer_id, assignation, organization)

        url = f"{self._ip}/organization/{organization}/datasets/assignations"
        params = {
            'datasetname': datasetname,
            'assignation_id': assignation_id
        }

        ret = self.session.get(url, headers=self._headers, params=params)

        if self._check_status_code(ret, 200) == 1:
            ret = self.session.get(url, headers=self._headers, params=params)

        self._url = ret.url

        jsonret = ret.json()

        return jsonret
        
        
    def get_assignation_data(self, assignation_id=None, datasetname=None, title=None, scenario=None, layer_id=None, layer=None, assignation=None, geometries=False, polygon=None, organization=None):
        '''
            Returns a list of assignation data in dictionaries.
        '''

        if organization is None:
            organization = self._organization

        datasetname = self._select_datasetname(datasetname, title, scenario, organization)
        layer_id = self._select_polygon_layer_id(layer_id, layer, scenario, organization)
        assignation_id = self._select_assignation_id(assignation_id, datasetname, layer_id, assignation, organization)

        url = f"{self._ip}/organization/{organization}/dataset/assignation/{assignation_id}"

        if polygon is not None:
            polygon = json.dumps(polygon)

        params = {
            'layer_id': layer_id,
            'assignation': assignation,
            'geometries': geometries,
            'polygon': polygon
        }

        ret = self.session.get(url, headers=self._headers, params=params)

        if self._check_status_code(ret, 200) == 1:
            ret = self.session.get(url, headers=self._headers, params=params)

        self._url = ret.url

        jsonret = ret.json()

        return jsonret
    

    ###----- polygons tables methods -----###
    ###-----------------------------------###
    def get_polygon_layers(self, layer_id=None, layer=None, scenario=None, organization=None):
        '''
            Returns a list of polygon layers in dictionaries.
        '''

        if organization is None:
            organization = self._organization

        layer_id = self._select_polygon_layer_id(layer_id, layer, scenario, organization)

        url = f"{self._ip}/organization/{organization}/polygon/layers"
        params = {
            'layer_id': layer_id
        }

        ret = self.session.get(url, headers=self._headers, params=params)

        if self._check_status_code(ret, 200) == 1:
            ret = self.session.get(url, headers=self._headers, params=params)

        self._url = ret.url
        
        jsonret = ret.json()

        return jsonret
    

    def get_polygon_geometries(self, layer_id=None, layer=None, scenario=None, polygon=None, _polygon_id=None, organization=None):
        '''
            Returns a list of polygon geometries in dictionaries.
        '''

        if organization is None:
            organization = self._organization
        
        layer_id = self._select_polygon_layer_id(layer_id, layer, scenario, organization)

        url = f"{self._ip}/organization/{organization}/polygon/{layer_id}/geometries"
        if polygon is not None:
            polygon = json.dumps(polygon)

        params = {
            'polygon': polygon,
            '_polygon_id': _polygon_id
        }

        ret = self.session.get(url, headers=self._headers, params=params)
        
        if self._check_status_code(ret, 200) == 1:
            ret = self.session.get(url, headers=self._headers, params=params)

        self._url = ret.url
        
        jsonret = ret.json()

        return jsonret
    

    def get_polygon_metrics(self, polygon_metric=None, metric_ids=None, assignation_ids=None, organization=None):
        '''
            Returns a list of polygon metrics in dictionaries.
        '''

        if organization is None:
            organization = self._organization

        url = f"{self._ip}/organization/{organization}/polygon/metrics"

        params = {
            'polygon_metric': polygon_metric,
            'metric_ids': metric_ids,
            'assignation_ids': assignation_ids
        }

        ret = self.session.get(url, headers=self._headers, params=params)

        if self._check_status_code(ret, 200) == 1:
            ret = self.session.get(url, headers=self._headers, params=params)

        self._url = ret.url

        jsonret = ret.json()

        return jsonret


    def get_polygon_data(self, polygon_metric=None, metric=None, metric_ids=None, assignation=None, assignation_ids=None, orbit=None, geometry=None, datasetnames=None, geometries=None, polygon=None, _polygon_id=None, date_span=None, organization=None):
        '''
            Returns a list of polygon data in dictionaries.
        '''

        if organization is None:
            organization = self._organization

        datasetnames = self._select_datasetnames_list(datasetnames, orbit, geometry, organization)
        metric_ids = self._select_metric_ids_list(metric_ids, metric, organization)
        assignation_ids = self._select_assignation_ids_list(assignation_ids, assignation, organization)

        url = f"{self._ip}/organization/{organization}/polygon/data/{polygon_metric}"

        if polygon is not None:
            polygon = json.dumps(polygon)

        params = {
            'metric_ids': metric_ids,
            'assignation_ids': assignation_ids,
            'datasetnames': datasetnames,
            'geometries': geometries,
            'polygon': polygon,
            '_polygon_id': _polygon_id,
            'date_span': date_span
        }

        ret = self.session.get(url, headers=self._headers, params=params)

        if self._check_status_code(ret, 200) == 1:
            ret = self.session.get(url, headers=self._headers, params=params)

        self._url = ret.url

        jsonret = ret.json()

        return jsonret
    

    def get_polygon_data_info(self, polygon_metric=None, metric=None, metric_ids=None, assignation=None, assignation_ids=None, orbit=None, geometry=None, datasetnames=None, polygon=None, _polygon_id=None, date_span=None, organization=None):
        '''
            Returns a list of polygon data in dictionaries.
        '''

        if organization is None:
            organization = self._organization

        datasetnames = self._select_datasetnames_list(datasetnames, orbit, geometry, organization)
        metric_ids = self._select_metric_ids_list(metric_ids, metric, organization)
        assignation_ids = self._select_assignation_ids_list(assignation_ids, assignation, organization)

        url = f"{self._ip}/organization/{organization}/polygon/data/{polygon_metric}/info"

        if polygon is not None:
            polygon = json.dumps(polygon)

        params = {
            'metric_ids': metric_ids,
            'assignation_ids': assignation_ids,
            'datasetnames': datasetnames,
            'polygon': polygon,
            '_polygon_id': _polygon_id,
            'date_span': date_span
        }

        ret = self.session.get(url, headers=self._headers, params=params)

        if self._check_status_code(ret, 200) == 1:
            ret = self.session.get(url, headers=self._headers, params=params)

        self._url = ret.url

        jsonret = ret.json()

        return jsonret
    


    ###----- actions -----###
    ###-------------------###
    def run_action(self, action, data=None, organization=None):
        '''
        Runs the action "action" with the input data "data".
        '''

        if organization is None:
            organization = self._organization

        url = f"{self._ip}/organization/{organization}/action/{action}"

        ret = self.session.post(url, headers=self._headers, json=data)
        
        if self._check_status_code(ret, 200) == 1:
            ret = self.session.post(url, headers=self._headers, json=data)

        self._url = ret.url
        jsonret = ret.json()

        return jsonret
    

#---------------------------------------------------------------------------#
#---------------------------------------------------------------------------#

###--------------------------###
###----- ApiAdmin class -----###

class ApiAdmin(ApiUser):
    '''
        This class can be created only by an admin user.
    '''

    def __init__(self, ip, token):
        super().__init__(ip, token)

        if self._role > 1:
            raise ValueError("User is not admin")


    ###----------------------
    ##--------------------
    #--- usable methods

    ###----- datasets tables methods -----###
    ###-----------------------------------###
    def modify_dataset_metadata(self, datasetname, metadata, organization=None):
        """
            This method changes the metadata of the dataset. 
            'metadata' contains the values to be changed:
                - scenario
                - title
                - heading_angle
                - inc_angle
                - orbit
                - swath
                - geometry
                - pre_process
                - process
                - lon_ref
                - lat_ref
                - user_boundary
            It is not necessary to include all the values, only the ones to be changed.
            If other different values are included, they will be ignored.
        """
        
        if organization is None:
            organization = self._organization

        url = f"{self._ip}/organization/{organization}/dataset/{datasetname}/metadata"

        ret = self.session.post(url, json=metadata, headers=self._headers)

        if self._check_status_code(ret, 201) == 1:
            ret = self.session.post(url, json=metadata, headers=self._headers)

        self._url = ret.url

        return {"status_code": ret.status_code, "detail": ret.json()}


    def add_dataset(self, dataset_json, title=None, scenario=None, organization=None):
        '''
            This method adds a new points dataset.
        '''

        if organization is None:
            organization = self._organization

        if title is not None:
            dataset_json['metadata']['title'] = title
        if scenario is not None:
            dataset_json['metadata']['scenario'] = scenario
        
        url = f"{self._ip}/organization/{organization}/dataset"

        ret = self.session.post(url, json=dataset_json, headers=self._headers)

        if  self._check_status_code(ret, 201) == 1:
            ret = self.session.post(url, json=dataset_json, headers=self._headers)

        self._url = ret.url

        return {"status_code": ret.status_code, "detail": ret.json()}
    

    def delete_dataset(self, datasetname=None, title=None, scenario=None, organization=None):
        '''
            This method deletes a complete dataset.
        '''

        if organization is None:
            organization = self._organization

        datasetname = self._select_datasetname(datasetname, title, scenario, organization)

        url = f"{self._ip}/organization/{organization}/dataset/{datasetname}"

        ret = self.session.delete(url, headers=self._headers)

        if self._check_status_code(ret, 204) == 1:
            ret = self.session.delete(url, headers=self._headers)

        self._url = ret.url

        return ret.status_code


    ###----- properties tables methods -----###
    ###-------------------------------------###
    def add_property(self, property_json, datasetname=None, title=None, scenario=None, organization=None):
        '''
            This method adds a new property to the dataset.
        '''

        if organization is None:
            organization = self._organization

        datasetname = self._select_datasetname(datasetname, title, scenario, organization)

        url = f"{self._ip}/organization/{organization}/properties/dataset/{datasetname}"

        ret = self.session.post(url, json=property_json, headers=self._headers)

        if self._check_status_code(ret, 201) == 1:
            ret = self.session.post(url, json=property_json, headers=self._headers)

        self._url = ret.url

        return {"status_code": ret.status_code, "detail": ret.json()}
    

    def delete_property(self, property_id=None, datasetname=None, title=None, scenario=None, property=None, organization=None):
        '''
            This method deletes a property from the dataset.
        '''

        if organization is None:
            organization = self._organization

        datasetname = self._select_datasetname(datasetname, title, scenario, organization)
        property_id = self._select_property_id(property_id, datasetname, property, organization)

        url = f"{self._ip}/organization/{organization}/property/{property_id}"

        ret = self.session.delete(url, headers=self._headers)

        if self._check_status_code(ret, 204) == 1:
            ret = self.session.delete(url, headers=self._headers)

        self._url = ret.url

        return ret.status_code


    ###----- metrics tables methods -----###
    ###----------------------------------###
    def add_metric(self, metric_json, datasetname=None, title=None, scenario=None, organization=None):
        '''
            This method adds a new metric to the dataset.
        '''

        if organization is None:
            organization = self._organization

        datasetname = self._select_datasetname(datasetname, title, scenario, organization)

        url = f"{self._ip}/organization/{organization}/metrics/dataset/{datasetname}"

        ret = self.session.post(url, json=metric_json, headers=self._headers)

        if self._check_status_code(ret, 201) == 1:
            ret = self.session.post(url, json=metric_json, headers=self._headers)

        self._url = ret.url

        return {"status_code": ret.status_code, "detail": ret.json()}


    def delete_metric(self, metric_id=None, datasetname=None, title=None, scenario=None, metric=None, date_span=None, organization=None):
        '''
            This method deletes a metric from the dataset.
        '''

        if organization is None:
            organization = self._organization

        datasetname = self._select_datasetname(datasetname, title, scenario, organization)
        metric_id = self._select_metric_id(metric_id, datasetname, metric, organization)

        url = f"{self._ip}/organization/{organization}/metric/{metric_id}"
        params = {
            'date_span': date_span
        }

        ret = self.session.delete(url, headers=self._headers, params=params)

        if self._check_status_code(ret, 204) == 1:
            ret = self.session.delete(url, headers=self._headers, params=params)

        self._url = ret.url

        return ret.status_code
        

    ###----- models tables methods -----###
    ###---------------------------------###
    def add_model(self, model_json, datasetname=None, title=None, scenario=None, organization=None):
        '''
            This method adds a new model to the dataset.
        '''

        if organization is None:
            organization = self._organization

        datasetname = self._select_datasetname(datasetname, title, scenario, organization)

        url = f"{self._ip}/organization/{organization}/models/dataset/{datasetname}"

        ret = self.session.post(url, json=model_json, headers=self._headers)

        if self._check_status_code(ret, 201) == 1:
            ret = self.session.post(url, json=model_json, headers=self._headers)

        self._url = ret.url

        return {"status_code": ret.status_code, "detail": ret.json()}
    

    def delete_model(self, model_id=None, datasetname=None, title=None, scenario=None, model=None, organization=None):
        '''
            This method deletes a model from the dataset.
        '''

        if organization is None:
            organization = self._organization

        datasetname = self._select_datasetname(datasetname, title, scenario, organization)
        model_id = self._select_model_id(model_id, datasetname, model, organization)

        url = f"{self._ip}/organization/{organization}/model/{model_id}"

        ret = self.session.delete(url, headers=self._headers)

        if self._check_status_code(ret, 204) == 1:
            ret = self.session.delete(url, headers=self._headers)

        self._url = ret.url

        return ret.status_code


    ###----- exogenous tables methods -----###
    ###-------------------------------------###
    def add_exogenous(self, exogenous_json, exogenous=None, scenario=None, organization=None):
        '''
            This method adds new exogenous data to the dataset.
        '''

        if organization is None:
            organization = self._organization

        if exogenous is not None:
            exogenous_json['metadata']['exogenous'] = exogenous
        if scenario is not None:
            exogenous_json['metadata']['scenario'] = scenario

        url = f"{self._ip}/organization/{organization}/exogenous"

        ret = self.session.post(url, json=exogenous_json, headers=self._headers)

        if self._check_status_code(ret, 201) == 1:
            ret = self.session.post(url, json=exogenous_json, headers=self._headers)

        self._url = ret.url

        return {"status_code": ret.status_code, "detail": ret.json()}
    

    def delete_exogenous(self, exogenous_id=None, exogenous=None, scenario=None, organization=None):
        '''
            This method deletes exogenous data from the dataset.
        '''

        if organization is None:
            organization = self._organization

        exogenous_id = self._select_exogenous_id(exogenous_id, exogenous, scenario, organization)

        url = f"{self._ip}/organization/{organization}/exogenous/{exogenous_id}"

        ret = self.session.delete(url, headers=self._headers)

        if self._check_status_code(ret, 204) == 1:
            ret = self.session.delete(url, headers=self._headers)

        self._url = ret.url

        return ret.status_code
    

    ###----- assignations methods -----###
    ###--------------------------------###
    def add_assignation(self, assignation_json, datasetname=None, title=None, scenario=None, layer_id=None, layer=None, organization=None):
        '''
            This method adds a new assignation to the dataset.
        '''

        if organization is None:
            organization = self._organization

        datasetname = self._select_datasetname(datasetname, title, scenario, organization)
        layer_id = self._select_polygon_layer_id(layer_id, layer, scenario, organization)
        if layer_id is not None:
            assignation_json['metadata']['layer_id'] = layer_id

        url = f"{self._ip}/organization/{organization}/dataset/{datasetname}/assignation"

        ret = self.session.post(url, json=assignation_json, headers=self._headers)

        if self._check_status_code(ret, 201) == 1:
            ret = self.session.post(url, json=assignation_json, headers=self._headers)

        self._url = ret.url

        return {"status_code": ret.status_code, "detail": ret.json()}
    

    def delete_assignation(self, assignation_id=None, datasetname=None, title=None, scenario=None, layer_id=None, layer=None, assignation=None, organization=None):
        '''
            This method deletes an assignation from the dataset.
        '''

        if organization is None:
            organization = self._organization

        datasetname = self._select_datasetname(datasetname, title, scenario, organization)
        layer_id = self._select_polygon_layer_id(layer_id, layer, scenario, organization)
        assignation_id = self._select_assignation_id(assignation_id, datasetname, layer_id, assignation, organization)

        url = f"{self._ip}/organization/{organization}/dataset/assignation/{assignation_id}"

        ret = self.session.delete(url, headers=self._headers)

        if self._check_status_code(ret, 204) == 1:
            ret = self.session.delete(url, headers=self._headers)

        self._url = ret.url

        return ret.status_code


    ###----- polygons methods -----###
    ###----------------------------###
    def add_polygon_layer(self, polygon_json, layer=None, scenario=None, organization=None):
        '''
            This method adds a polygon layer.
        '''

        if organization is None:
            organization = self._organization

        if layer is not None:
            polygon_json['layer_metadata']['layer'] = layer
        if scenario is not None:
            polygon_json['layer_metadata']['scenario'] = scenario

        url = f"{self._ip}/organization/{organization}/polygon/layer"

        ret = self.session.post(url, json=polygon_json, headers=self._headers)

        if self._check_status_code(ret, 201) == 1:
            ret = self.session.post(url, json=polygon_json, headers=self._headers)

        self._url = ret.url

        return {"status_code": ret.status_code, "detail": ret.json()}
    

    def add_polygon_metrics(self, polygon_json, organization=None):
        '''
            This method adds polygon metrics.
        '''

        if organization is None:
            organization = self._organization

        url = f"{self._ip}/organization/{organization}/polygon/metrics"

        ret = self.session.post(url, json=polygon_json, headers=self._headers)

        if self._check_status_code(ret, 201) == 1:
            ret = self.session.post(url, json=polygon_json, headers=self._headers)

        self._url = ret.url

        return {"status_code": ret.status_code, "detail": ret.json()}
    

    def delete_polygon_layer(self, layer_id=None, layer=None, scenario=None, organization=None):
        '''
            This method deletes a polygon layer.
        '''

        if organization is None:
            organization = self._organization

        layer_id = self._select_polygon_layer_id(layer_id, layer, scenario, organization)

        url = f"{self._ip}/organization/{organization}/polygon/layer/{layer_id}"

        ret = self.session.delete(url, headers=self._headers)

        if self._check_status_code(ret, 204) == 1:
            ret = self.session.delete(url, headers=self._headers)

        self._url = ret.url

        return ret.status_code
    

    def delete_polygon_metrics(self, polygon_metric=None, assignation_id=None, metric_id=None, organization=None):
        '''
            This method deletes a polygon metrics.
        '''

        if organization is None:
            organization = self._organization

        url = f"{self._ip}/organization/{organization}/polygon/metrics/"
        params = {
            'polygon_metric': polygon_metric,
            'assignation_id': assignation_id,
            'metric_id': metric_id
        }

        ret = self.session.delete(url, headers=self._headers, params=params)

        if self._check_status_code(ret, 204) == 1:
            ret = self.session.delete(url, headers=self._headers, params=params)

        self._url = ret.url

        return ret.status_code


    ###----- quota methods -----###
    ###-------------------------###
    def get_assigned_quota(self, organization=None):
        '''
            Returns the assigned quota of the selected organization.
        '''

        if organization is None:
            organization = self._organization

        url = f"{self._ip}/organization/{organization}/quota/assigned"

        ret = self.session.get(url, headers=self._headers)

        if self._check_status_code(ret, 200) == 1:
            ret = self.session.get(url, headers=self._headers)

        self._url = ret.url
        jsonret = ret.json()

        return jsonret
    

    def get_consumed_quota(self, organization=None):
        '''
            Returns the consumed quota of the selected organization.
        '''

        if organization is None:
            organization = self._organization

        url = f"{self._ip}/organization/{organization}/quota/consumed"

        ret = self.session.get(url, headers=self._headers)

        if self._check_status_code(ret, 200) == 1:
            ret = self.session.get(url, headers=self._headers)

        self._url = ret.url
        jsonret = ret.json()

        return jsonret
            

    ###----- credits methods -----###
    ###---------------------------###
    def get_credits(self, organization=None):
        '''
            Returns the credits of the selected organization.
        '''

        if organization is None:
            organization = self._organization

        url = f"{self._ip}/organization/{organization}/credits"

        ret = self.session.get(url, headers=self._headers)

        if self._check_status_code(ret, 200) == 1:
            ret = self.session.get(url, headers=self._headers)

        self._url = ret.url
        jsonret = ret.json()

        return jsonret
    

#---------------------------------------------------------------------------#
#---------------------------------------------------------------------------#

###-------------------------###
###----- ApiRoot class -----###

class ApiRoot(ApiAdmin):
    '''
    This class can be created only as a admin user.
    '''

    def __init__(self, ip, token):
        super().__init__(ip, token)

        if self._role != 0:
            raise ValueError("User is not root")


    ###----------------------
    ##--------------------
    #--- usable methods

    ###------------------------###
    ###----- manage users -----###
    def get_users(self):
        '''
            Returns a list of dictionaries. Each dictionary has the information.
        '''

        url = f"{self._ip}/users"
        
        ret = self.session.get(url, headers=self._headers)

        if self._check_status_code(ret, 200) == 1:
            ret = self.session.get(url, headers=self._headers)

        jsonret = ret.json()

        return jsonret


    def create_user(self, keycloak_id, organization, username, role=2, quota=1.0, credits=10000):
        '''
            This mehotd creates a new user.
        '''

        url = f"{self._ip}/users"
        _json = {
            "keycloak_id": keycloak_id,
            "organization": organization,
            "username": username,
            "role": role,
            "quota": quota,
            "credits": credits
        }

        ret = self.session.post(url, json=_json, headers=self._headers)

        if self._check_status_code(ret, 201) == 1:
            ret = self.session.post(url, json=_json, headers=self._headers)

        return ret.status_code


    def delete_user(self, user_to_delete):
        '''
            This mehotd deletes user.
        '''

        url = f"{self._ip}/users/{user_to_delete}"

        ret = self.session.delete(url, headers=self._headers)

        if self._check_status_code(ret, 204) == 1:
            ret = self.session.delete(url, headers=self._headers)

        return ret.status_code
    

    def modify_role(self, user, role):
        '''
            This method updates the role of the user.
        '''

        url = f"{self._ip}/users/{user}/update/role"
        _json = {
            "role": role
        }

        ret = self.session.post(url, json=_json, headers=self._headers)

        if self._check_status_code(ret, 201) == 1:
            ret = self.session.post(url, json=_json, headers=self._headers)

        return ret.json()


    ###------------------------###
    ###----- manage quota -----###
    def modify_quota(self, organization, quota):
        '''
            This method updates the quota of the organization.
        '''

        url = f"{self._ip}/organization/{organization}/update/quota"
        _json = {
            "quota": quota
        }
        
        ret = self.session.post(url, json=_json, headers=self._headers)

        if self._check_status_code(ret, 201) == 1:
            ret = self.session.put(url, json=_json, headers=self._headers)

        jsonret = ret.json()

        return jsonret
    

    ###--------------------------###
    ###----- manage credits -----###
    def modify_credits(self, organization, credits):
        '''
            This method updates the credits of the organization.
        '''

        url = f"{self._ip}/organization/{organization}/update/credits"
        params = {
            "credits": credits
        }

        ret = self.session.post(url, params=params, headers=self._headers)

        if self._check_status_code(ret, 201) == 1:
            ret = self.session.post(url, params=params, headers=self._headers)

        jsonret = ret.json()

        return jsonret
    