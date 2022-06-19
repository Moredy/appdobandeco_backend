from array import array
from multiprocessing.dummy import Array
from warnings import catch_warnings
from firebase_admin import db
from fastapi import APIRouter, Depends, HTTPException, Response, status
from pydantic import BaseModel
from fastapi.encoders import jsonable_encoder

router = APIRouter()


class DefaultResponseModel(BaseModel):
    statusCode: int
    message:str

class CreateResponseModel(BaseModel):
    statusCode: int
    uid:str

class GetResponseModel(BaseModel):
    statusCode: int
    dataObj: dict


#Create Report - POST
class ReportBody(BaseModel):
    user_uid: str
    date: str
    vegan : bool
    message: str
    likes : int


@router.post("/reportService/createReport/", response_model=CreateResponseModel)
async def create_report(reportBody: ReportBody, response: Response):
    reportRef = db.reference('reports/');
    json_compatible_item_data = jsonable_encoder(reportBody)
    #print(json_compatible_item_data)
    newReportRef = reportRef.push(json_compatible_item_data);

    response.status_code = status.HTTP_201_CREATED
    return {"statusCode": response.status_code, "uid": newReportRef.key};

#Get all reports
@router.get("/reportService/getAllReportsData/", response_model=GetResponseModel)
async def get_all_reports(response: Response):
    reportRef = db.reference( 'reports/');
    reportData = reportRef.get()
    reportData_array = []
    
    for item in reportData:
        report = reportRef.child(item);
        reportObj = report.get()
        reportData_array.append({
            "id_report": report.key,
            "user_uid": reportObj['user_uid'],
            "date": reportObj['date'],
            "vegan": reportObj['vegan'],
            "message" : reportObj['message'],
            "likes": reportObj['likes'],
        })

    Dict = {"reportsArray": reportData_array}

    response.status_code = status.HTTP_200_OK
    return {"statusCode": response.status_code, "dataObj": Dict};

#Get report by id
@router.get("/reportService/getReportById/{report_id}", response_model=GetResponseModel)
async def get_report_by_id(report_id, response: Response):
    reportRef = db.reference( 'reports/');
    reportData = reportRef.child(report_id).get()

    response.status_code = status.HTTP_200_OK
    return {"statusCode": response.status_code, "dataObj": reportData};

@router.get("/reportService/getReportByDateAndType/{date}/{vegan}", response_model=GetResponseModel)
async def get_report_by_date_type(date, vegan, response: Response):
    
    allReports = await get_all_reports(response)
    allReports = allReports['dataObj']['reportsArray']

    selectedReports = []

    if vegan == 'vegan':
        veganBool = True
    else:
        veganBool = False


    for report in allReports:
        if report['date'] == date and report['vegan'] == veganBool:
            selectedReports.append(report)


    response.status_code = status.HTTP_200_OK
    return {"statusCode": response.status_code, "dataObj": {}};


