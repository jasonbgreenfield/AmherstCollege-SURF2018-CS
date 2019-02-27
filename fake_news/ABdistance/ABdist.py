import pickle
from multiprocessing import Pool
from functools import partial
import time

def ABdist(my_to_co, my_bow, target_1425):
    # common = 0
    # for word1 in my_to_co:
    #     for word2 in target_1425[0]:
    #         if (word1 == word2) and (my_bow[word1] == target_1425[1][word2]):
    #             common += 1

    # so it worked when doing the sets, ran in like 5 minutes. Only used like 3-5 processes at any point in time, weird. But it worked so...

    common = 0
    intersect = set(my_to_co).intersection(set(target_1425[0]))
    for word in intersect:
        if my_bow[word] == target_1425[1][word]:
            common += 1
    return int(10000-common)

def procedure(index, all_1425):
    my_14 = all_1425[index][0]
    my_25 = all_1425[index][1]
    size = len(all_1425)

    print(f"Started on the {index}th article")
    start_time = time.time()

    distances = [None]*(size-1-index)
    articles = [None]*(size-1-index)
    counter = 0
    for i in range(index+1, size):
        their_1425 = all_1425[i]
        distances[counter] = ABdist(my_14, my_25, their_1425)
        articles[counter] = (index, i)
        counter += 1
    end_time = time.time()

    # if index%100==0:
    print(f"Finished Procedure on the {index}th article in {end_time-start_time} seconds")

    to_return = (distances, articles)

    return to_return


if __name__ == "__main__":
    time1 = time.time()
    pickle_in = open('./data/5k_random_processed_and_labels.pkl', 'rb')
    data, desc = pickle.load(pickle_in)
    processed = data[0]
    labels = data[1]

    size = len(processed)
    print(f"size is {size}")


    all_14_and_25 = []
    for i in range(size):
        all_14_and_25.append((processed[i][14], processed[i][25]))


    time2 = time.time()
    print(f"Starting pool, pickle took: {time2-time1} seconds")
    start = time.time()
    p = Pool(processes=64) # how many?
    foo = partial(procedure, all_1425=all_14_and_25)
    ABdistances = p.map(foo, range(size-1))
    p.close()
    end = time.time()
    print(f"Ended pool in {end-start} seconds")

    desc = "List of tuples and also labels. Labels is the same list from 5k_random_processed_and_labels.py. First item in tuple is distances of each article from all others where dist = 10000 - the number of words that have the same word count for both articles, and second is list of tuples which are the derivatives for each distance"
    pickle_out = open('./data/ABdistances_5k_random.pkl', 'wb')
    pickle.dump((ABdistances, labels, desc), pickle_out)
    pickle_out.close()
