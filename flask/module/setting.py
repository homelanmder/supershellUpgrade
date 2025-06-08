from flask import current_app
from category.redisclient import RedisClient, connect_redis


def clearUselessGroupMark():
    '''
        清除冗余分组备注记录
    '''
    try:
        client = RedisClient(0)
        history = connect_redis(1)
        num = 0

        hostname_list = [client.conn.hget(sessid.decode(), "hostname").decode() for sessid in client.conn.keys()]
        current_app.logger.info('Recorded Hostname List: ' + str(hostname_list))
        for hostname in history.keys():
            if hostname.decode() not in hostname_list:
                history.delete(hostname.decode())
                num = num + 1
                current_app.logger.info('Delete Useless Group And Mark History For Hostname: ' + hostname.decode())
        history.close()
        return {"stat": "success", "result": str(num)}
    except Exception as e:
        current_app.logger.exception(e)
        return {"stat": "failed", "result": str(e)}
