from typing import List
from sirio.event import ObjEvent
import requests
import json
            
class Message:
    role: str
    content: str

class RequestAiBatch:
    key: str
    idSync: str = None
    sirioDomain: str = None
    application: str
    messages: List[Message]

class SirioAiBatch:
    
    def __init__(self, hostOpenAiBatchRequest: str):
        self.hostOpenAiBatchRequest = hostOpenAiBatchRequest

        def requestAi(self, requestAi: RequestAiBatch) -> str:
            
            url = f'{self.hostOpenAiBatchRequest}/batch/request'
            print(f'URL: {url}')
            response = requests.post(url=url, json=requestAi)
            if response.status_code == 200:
                print(f'Invovazione per openai-batch-request, domain: {requestAi.domain} - idSync: {requestAi.idSync}: response: {response.text}')
                id_openai_batch_request = response.text.replace('"', '')
                print(f'id_openai_batch_request: {id_openai_batch_request}')
                return id_openai_batch_request
            else:
                print(f'Problemi con invocazione openai-batch-request, domain: {requestAi.domain} - idSync: {requestAi.idSync} - status: {response.status_code}: {response.text}')
                raise Exception(f'Problema di invocazione objEvent.domain --> status: {response.status_code}: {response.text}')
        
