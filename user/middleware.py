import logging
from .models import UserLog

logging.basicConfig(filename='book_store.log', encoding='utf-8', level=logging.DEBUG,
                    format='%(asctime)s %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p')
logger = logging.getLogger()


class UserLogMiddleware:

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        self.log(request)
        return self.get_response(request)

    def log(self, request):
        try:
            user_log = UserLog.objects.filter(method=request.method, url=request.path)
            if not user_log.exists():
                UserLog.objects.create(method=request.method, url=request.path)
            else:
                log = user_log.first()
                log.count += 1
                log.save()
        except Exception as ex:
            logger.exception(ex)
        