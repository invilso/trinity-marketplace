from celery import shared_task
import products.bot as b


@shared_task
def start_bot():  
    return b.main()