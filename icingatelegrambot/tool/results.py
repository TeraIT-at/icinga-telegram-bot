

class ResultPrinter():
    @staticmethod
    def printResultsFromResponse(response):
        retval = ""
        if not "error" in response:
            for result in response["results"]:
                if not 200 <= result["code"] <= 299:
                    retval += "Error: "+result["status"]+"\n"
                else:
                    retval += "Success: "+result["status"]+"\n"
        else:
            retval = "API-Error: "+response["status"]
        return retval

