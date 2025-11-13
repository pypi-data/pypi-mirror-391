from sirio.business_object import BusinessObject, Object
import requests


class SirioReport:
    
    def __init__(self, hostSirio: str, separatorBindId: str = '%'):
        self.hostSirio = hostSirio
        self.separatorBindId = separatorBindId
        self.presignedUrlReport = None

        def RenderReport(self, templateName:str, domain: str, businessObject: BusinessObject) -> bool:
            esito = False
            url = f'{self.hostSirio}/pdf/{domain}/report'
            urlParams = f'{self.hostSirio}/pdf/{domain}/template/{templateName}/params'
            responseParams = requests.get(urlParams)
            if responseParams.status_code == 200:
                params = responseParams.json()  # Supponiamo che sia una lista di stringhe
                dizionario = {}

                for bindId in params:
                    parti = bindId.split(self.separatorBindId, 1)
                    valore = businessObject.getValue(bind=parti[0], id=parti[1])
                    dizionario[bindId] = valore

                requestReport = {
                        "templateName": templateName,
                        "data": dizionario
                }
                response = requests.post(url=url, json=requestReport)
                if response.status_code == 200:
                    self.presignedUrlReport = response.text
                    
                    print(f'RenderReport: {response.text}')
                    esito = True
            else:
                print(f"Errore nella richiesta: {responseParams.status_code}")
            return esito
        
        def getPresignedUrlReport(self) -> str:
            """
            Restituisce la presigned URL del report generato.

            :return: La presigned URL del report.
            :raises Exception: Se il report non è stato generato o se la presigned URL non è disponibile.
            """
            if self.presignedUrlReport is None:
                raise Exception("Il report non è stato generato o la presigned URL non è disponibile.")
            return self.presignedUrlReport
        
        def getReportStream(self):
            """
            Restituisce uno stream del report generato.

            :return: Uno stream (BytesIO) contenente il report.
            :raises Exception: Se il report non è stato generato o se la presigned URL non è disponibile.
            """
            if self.presignedUrlReport is None:
                raise Exception("Il report non è stato generato o la presigned URL non è disponibile.")
            
            return self.__get_stream_from_presigned_url(self.presignedUrlReport)

        def __get_stream_from_presigned_url(self, presigned_url):
            """
            Scarica un file da una presigned URL e lo restituisce come stream (BytesIO).

            :param presigned_url: La presigned URL da cui scaricare il file.
            :return: Uno stream (BytesIO) contenente il contenuto del file.
            :raises Exception: Se la richiesta fallisce.
            """
            response = requests.get(presigned_url, stream=True)

            if response.status_code == 200:
                # Carica tutto il contenuto in memoria in uno stream
                file_stream = io.BytesIO(response.content)
                file_stream.seek(0)  # Si assicura che lo stream parta dall'inizio
                return file_stream
            else:
                raise Exception(f"Errore nel download: {response.status_code}")