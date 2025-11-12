from one_interfaces import apierror_pb2 as apiError
from one_interfaces import apiresponse_pb2 as apiResponse
import google
import logging


def DeserializeResponse(response):
    try:
        pbResponse = apiResponse.ApiResponse()
        if response.status_code == 404:
            pbResponse.statusCode = 404
            error = apiError.ApiError()
            error.statusCode =404
            error.detail="Not found"            
            pbResponse.errors.append(error)            
            return pbResponse
        if response.status_code == 401:
            pbResponse.statusCode = 401            
            error = apiError.ApiError()
            error.statusCode =401
            error.detail="Not authenticated"            
            pbResponse.errors.append(error)            
            return pbResponse
        if response.status_code == 403:
            pbResponse.statusCode = 403
            error = apiError.ApiError()
            error.statusCode =403
            error.detail="Not authorized for this resource"  
            pbResponse.errors.add(error)
            return pbResponse
        pbResponse.ParseFromString(response.content)
        return pbResponse
    except Exception as Argument:
        logging.exception("Error occured in deserialization process", Argument)
        
