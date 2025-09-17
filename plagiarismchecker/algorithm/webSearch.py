import requests
from plagiarismchecker.algorithm import ConsineSim

serper_api_key = '***REMOVED***'  # Replace with your actual API key
serper_url = 'https://google.serper.dev/search'

headers = {
    "X-API-KEY": serper_api_key,
    "Content-Type": "application/json"
}

def searchWeb(text, output, c):
    try:
        payload = {
            "q": text
        }
        response = requests.post(serper_url, headers=headers, json=payload)
        response.raise_for_status()
        result = response.json()

        if "organic" in result and len(result["organic"]) > 0:
            maxSim = 0
            itemLink = ''
            numList = len(result["organic"])
            if numList >= 5:
                numList = 5
            for i in range(0, numList):
                item = result["organic"][i]
                content = item.get("snippet", "")
                simValue, plagiarised_words = ConsineSim.cosineSim(text, content)
                if simValue > maxSim:
                    maxSim = simValue
                    itemLink = item.get("link", "")
                    plagiarised_content = content
                if itemLink in output:
                    break

            if itemLink in output:
                print('if', maxSim)
                output[itemLink] += 1
                c[itemLink] = ((c[itemLink] * (output[itemLink] - 1) + maxSim) / output[itemLink])
            else:
                print('else', maxSim)
                output[itemLink] = 1
                c[itemLink] = maxSim
                c[itemLink + "_content"] = plagiarised_content
    except Exception as e:
        print(text)
        print(e)
        print('error')
        return output, c, 1

    return output, c, 0

