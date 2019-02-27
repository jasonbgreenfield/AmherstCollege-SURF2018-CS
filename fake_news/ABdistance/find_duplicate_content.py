import pickle
from multiprocessing import Pool
from functools import partial
import time

def one_article(index, articles):
    start = time.time()
    dupes = []
    for i in range(len(articles)):
        if (index != i) and (articles[i][1] == articles[index][1]):
            dupes.append(articles[i][0])
            dupes.append(articles[index][0])
    end = time.time()
    if index%1000 == 0:
        print(f"finished {index}th article in {end-start} seconds")
    return set(dupes)


if __name__ == "__main__":
    start_index = 0
    end_index = 129819
    finn = "./data/FakeNewsData.pkl"
    fin = open(finn, "rb")  # read, byte format
    (X, Y), desc = pickle.load(fin)  # de-serialize a data stream; to serialize, call dumps()

    only_1and4 = [None]*len(X)
    for i in range(len(X)):
        only_1and4[i] = (X[i][1], X[i][4]) # make this (X[i][1], X[i][2]) to do titles

    print("Starting pool")
    start = time.time()
    p = Pool(processes=36)  # how many?
    foo = partial(one_article, articles = only_1and4)
    duplicates = p.map(foo, range(start_index, end_index))
    # p.close()
    end = time.time()
    print(f"Ended pool at article {start_index} in {end-start} seconds")

    desc = f"For titles {start_index}-{end_index-1}, a list of every title's UID from FakeNewsData.pkl that has a duplicate title in the data set."
    pickle_out = open(f'./data/dc/dc_byUID_{start_index}-{end_index-1}.pkl', 'wb')
    pickle.dump((duplicates, desc), pickle_out)
    pickle_out.close()
    print(f"Dumped articles {start_index}-{end_index-1}")



