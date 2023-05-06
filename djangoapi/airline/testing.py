import random
import time
from datetime import timedelta

def str_time_prop(start, end, time_format, prop):
	"""Get a time at a proportion of a range of two formatted times.

	start and end should be strings specifying times formatted in the
	given format (strftime-style), giving an interval [start, end].
	prop specifies how a proportion of the interval to be taken after
	start.  The returned time will be in the specified format.
	"""

	stime = time.mktime(time.strptime(start, time_format))
	etime = time.mktime(time.strptime(end, time_format))
	ptime = stime + prop * (etime - stime)

	length_of_flight = random.randint(60,720)
	later_time = ptime + 60*length_of_flight
	return time.strftime(time_format, time.localtime(ptime)), time.strftime(time_format, time.localtime(later_time))


def random_date(start, end, prop):
	return str_time_prop(start, end, "%Y-%m-%d %H:%M:%S", prop)

new_date, later_time = random_date("2023-07-05 01:01:01", "2023-12-31 01:01:01", random.random())
print(new_date)
print(later_time)
