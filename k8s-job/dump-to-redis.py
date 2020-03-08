#!/usr/bin/env python

import time
import rediswq
import redis
import sys


host="redis"

# Uncomment next two lines if you do not have Kube-DNS working.
# import os
# host = os.getenv("REDIS_SERVICE_HOST")

def generate_session_traffic(listname):
	q = rediswq.RedisWQ(name=listname, host="redis")
	print("Worker with sessionID: " +  q.sessionID())
	print("Initial queue state: empty=" + str(q.empty()))
	while not q.empty():
		item = q.lease(lease_secs=10, block=True, timeout=2) 
		if item is not None:
			itemstr = item.decode("utf-8")
			print("Working on " + itemstr)
			print("Working on " + str(itemstr.split(':')))
			domain_value,account_value,max_sess =itemstr.split(':')# Put your actual work here instead of sleep.
			print("domain_value ==> %s"%(domain_value))
			print("account_value ==> %s"%(account_value))
			print("max_sessions==> %s"%(max_sess))
			# insert_data(instance,database,domain_value,account_value,max_sess)
			# update_data(instance,database,domain_value,testNo) 
            # Put your actual work here instead of 
			time.sleep(10)
			q.complete(item)
		else:
			print("Waiting for work")
	print("Queue empty, exiting")




def push_to_redis(record,listname):
	# print("Connecting to the redis")
	r = redis.Redis(host='redis', port=6379, db=0)
	# print("record to be inserted: ",record)
	# print(':'.join(record))
	r.rpush(listname, ':'.join(record))
	# print("New to added: ",r.keys())








limit=int(sys.argv[1])

for num in range(1,limit+1):
	print("-------------------------------------------------------------------------")
	print("Calling the redis push funtion for record "+str(num))
	push_to_redis(["accountid"+str(num),"dommainid"+str(num),"sessioninfo"+str(num)],"joblist")


start_time = time.time()
get_sets_from_redis("joblist")
print("--- %s seconds ---" % (time.time() - start_time))















