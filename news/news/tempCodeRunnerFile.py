    try:
        client = MongoClient('mongodb://localhost:27017/')
        db = client['local']
        collection = db['news']
        collection.insert_many(messages_data)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)