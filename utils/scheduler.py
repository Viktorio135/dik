from utils.dump import dump_dict, backup_bd

def start_schedule(scheduler, carts, word_list):
    scheduler.add_job(dump_dict, 'interval', minutes=10, args=(carts,word_list, ))
    scheduler.add_job(backup_bd, 'interval', minutes=30)
