import time

start_time = time.time()
end_time = start_time + 5
i = 1
while (time.time() < start_time + 5):
    print("Time is " + str(round(time.time() - start_time, 2)), end="\r")
    if (time.time() - start_time) > i:
        print(str(i), end="\033[K\n")
        i += 1
print("Time is " + str(round(time.time() - start_time, 2)))