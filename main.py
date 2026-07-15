from fastapi import FastAPI,Path,HTTPException,Query
import json
from pydantic import BaseModel,Field, computed_field
from typing import Annotated,Literal,Optional
from fastapi.responses import JSONResponse
app = FastAPI()

class PatientInfo(BaseModel):
   id:Annotated[str,Field(...,description='ID of the patient', examples=['P001'])]
   name:Annotated[str,Field(..., description='Name of the patient')]
   city:Annotated[str, Field(..., description='City where the patient is living')]
   age:Annotated[int,Field(..., gt=0, lt=120, description='Age of the patient')]
   gender:Annotated[Literal['male','female','others'],Field(...,description='gender of the patient')]
   height: Annotated[float, Field(..., gt=0, description='Height of the patient in mtrs')]
   weight: Annotated[float, Field(..., gt=0, description='Weight of the patient in kgs')]
   
   @computed_field
   @property
   def bmi(self):
      bmi = round(self.weight/(self.height**2),2)
      return bmi
   
   @computed_field
   @property
   def verdict(self) -> str:

        if self.bmi < 18.5:
            return 'Underweight'
        elif self.bmi < 25:
            return 'Normal'
        elif self.bmi < 30:
            return 'Normal'
        else:
            return 'Obese'

class PatientUpdate(BaseModel):
   name: Annotated[Optional[str], Field(default=None)]
   city: Annotated[Optional[str], Field(default=None)]
   age:Annotated[Optional[str],Field(default=None)]
   gender:Annotated[Optional[Literal['male','female','others']],Field(default=None)]
   height: Annotated[Optional[float], Field(default=None, gt=0)]
   weight: Annotated[Optional[float], Field(default=None, gt=0)]



def load_data():
 with open("patient.json","r") as f:
    data = json.load(f)
 return data

def save_data(data):
   with open("patient.json",'w') as f:
      json.dump(data,f)

@app.get("/")
def hello():
    return {"message":"Patient management system API"}

@app.get("/about")
def about():
    return {"message":"functional api to manage your patient records"}

@app.get("/view")
def view():
   data = load_data()
   return data

@app.get("/patient/{patient_id}")
def patient_details(patient_id:str = Path(...,description="Id of the patient in the dB",example="P001")):
   data = load_data()

   if patient_id in data:
      return data[patient_id]
   raise HTTPException(status_code=404,detail="Patient ID not found")

@app.get("/sort")
def sort_patients(sort_by:str = Query(...,description="sort on the basis of height,weight or bmi"),order:str=Query('asc',description="sort is asc or des order")):
   
   valid_fields = ["height","weight","bmi"]

   if sort_by not in valid_fields:
      raise HTTPException(status_code=400,detail=f"Invalid field ,select from {valid_fields}")
   
   if order not in ["asc","des"]:
      raise HTTPException(status_code=400,detail="invalid order select from asc or des")
   
   data = load_data()

   sort_order = True if order=='des' else False

   sorted_data = sorted(data.values(), key=lambda x: x.get(sort_by, 0), reverse=sort_order)

   return sorted_data

@app.post("/create")
def create_patient(patient:PatientInfo):
   data = load_data()
   if patient.id in data:
        raise HTTPException(status_code=400, detail='Patient already exists')
   data[patient.id] = patient.model_dump(exclude=['id'])
   save_data(data)
   return JSONResponse(status_code=201, content={'message':'patient created successfully'})

@app.put('/edit/{patient_id}')
def update_patient(patient_id: str, patient_update: PatientUpdate):

    data = load_data()

    if patient_id not in data:
        raise HTTPException(status_code=404, detail='Patient not found')
    
    existing_patient_info = data[patient_id]

    updated_patient_info = patient_update.model_dump(exclude_unset=True)

    for key, value in updated_patient_info.items():
        existing_patient_info[key] = value

    #existing_patient_info -> pydantic object -> updated bmi + verdict
    existing_patient_info['id'] = patient_id
    patient_pydandic_obj = PatientInfo(**existing_patient_info)
    #-> pydantic object -> dict
    existing_patient_info = patient_pydandic_obj.model_dump(exclude='id')

    # add this dict to data
    data[patient_id] = existing_patient_info

    # save data
    save_data(data)

    return JSONResponse(status_code=200, content={'message':'patient updated'})
# Load JSON.
# Find patient P001.
# Extract only the provided fields (weight, city).
# Merge them into the existing record.
# Add id temporarily.
# Create a PatientInfo object to validate data and recompute bmi and verdict.
# Convert it back to a dictionary (excluding id).
# Save the updated dictionary to patient.json.
# Return 200 OK.

@app.delete('/delete/{patient_id}')
def delete_patient(patient_id: str):

    # load data
    data = load_data()

    if patient_id not in data:
        raise HTTPException(status_code=404, detail='Patient not found')
    
    del data[patient_id]

    save_data(data)

    return JSONResponse(status_code=200, content={'message':'patient deleted'})

