from django.http import JsonResponse
from pymongo import MongoClient

def get_headers(request):
    try:
        client = MongoClient('mongodb://localhost:27017/')
        db = client['local']
        collection = db['news']
        news_items = list(collection.find().sort('timestamp', -1))
        for news in news_items:
            news['_id'] = str(news['_id'])
        return JsonResponse({'news': news_items})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
