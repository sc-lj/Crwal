# coding:utf-8

from hashlib import md5, sha1
class SimpleHash(object):
    def __init__(self, cap, seed):
        self.cap = cap
        self.seed = seed

    def hash(self, value):
        ret = 0
        for i in range(len(value)):
            ret += self.seed * ret + ord(value[i])
        return (self.cap - 1) & ret


class BloomFilter1(object):
    def __init__(self, server, key, blockNum=5):
        self.bit_size = 1 << 31  # Redis的String类型最大容量为512M，现使用256M;1 << 31,左移;2 <<2 得到8。——2按比特表示10
        # self.seeds = [5, 7, 11, 13, 31]
        self.seeds = [5, 7, 11, 13, 31, 37, 61]
        self.server = server
        self.key = key
        self.blockNum = blockNum
        self.hashfunc = []
        for seed in self.seeds:
            self.hashfunc.append(SimpleHash(self.bit_size, seed))

    def isContains(self, str_input):
        if not str_input:
            return False
        m5 = md5()
        m5.update(str_input)
        str_input = m5.hexdigest()
        ret = True

        name = self.key + str(int(str_input[0:6], 16) % self.blockNum)
        for f in self.hashfunc:
            loc = f.hash(str_input)
            ret = ret & self.server.getbit(name, loc)
        return ret

    def insert(self, str_input):
        m5 = md5()
        m5.update(str_input)
        str_input = m5.hexdigest()
        name = self.key + str(int(str_input[0:6], 16) % self.blockNum)
        for f in self.hashfunc:
            loc = f.hash(str_input)
            self.server.setbit(name, loc, 1)



import mmh3
import BitVector
import redis
import math
import time


class BloomFilter():
    #内置100个随机种子
    SEEDS = [543, 460, 171, 876, 796, 607, 650, 81, 837, 545, 591, 946, 846, 521, 913, 636, 878, 735, 414, 372,
             344, 324, 223, 180, 327, 891, 798, 933, 493, 293, 836, 10, 6, 544, 924, 849, 438, 41, 862, 648, 338,
             465, 562, 693, 979, 52, 763, 103, 387, 374, 349, 94, 384, 680, 574, 480, 307, 580, 71, 535, 300, 53,
             481, 519, 644, 219, 686, 236, 424, 326, 244, 212, 909, 202, 951, 56, 812, 901, 926, 250, 507, 739, 371,
             63, 584, 154, 7, 284, 617, 332, 472, 140, 605, 262, 355, 526, 647, 923, 199, 518]

    #capacity是预先估计要去重的数量
    #error_rate表示错误率
    #conn表示redis的连接客户端
    #key表示在redis中的键的名字前缀
    def __init__(self, capacity=1000000000, error_rate=0.00000001, conn=None, key='BloomFilter'):
        self.m = math.ceil(capacity*math.log(math.e,2)*math.log(1/error_rate,2))      #需要的总bit位数
        self.k = int(math.ceil(math.log1p(2)*self.m/capacity))                         #需要最少的hash次数
        self.mem = math.ceil(self.m/8/1024/1024)                                    #需要的多少M内存,1b=8字节，1kb=1024b，
        self.blocknum = math.ceil(self.mem/512)                                     #需要多少个512M的内存块,value的第一个字符必须是ascii码，所有最多有256个内存块
        self.seeds = self.SEEDS[0:self.k]
        self.key = key
        self.N = 2**31-1
        self.redis = conn
        if not self.redis:
            #默认如果没有redis连接，在内存中使用1G的内存块去重
            self.bitset = BitVector.BitVector(size=1<<30)
        # print(self.mem)
        # print(self.k)

    def add(self, value):
        name = self.key + "_" + str(ord(value[0])%self.blocknum)
        hashs = self.get_hashs(value)
        for hash in hashs:
            if self.redis:
                self.redis.setbit(name, hash, 1)
            else:
                self.bitset[hash] = 1

    def is_exist(self, value):
        name = self.key + "_" + str(ord(value[0])%self.blocknum)
        hashs = self.get_hashs(value)
        exist = True
        for hash in hashs:
            if self.redis:
                exist = exist & self.redis.getbit(name, hash)
            else:
                exist = exist & self.bitset[hash]
        return exist

    def get_hashs(self, value):
        hashs = list()
        for seed in self.seeds:
            hash = mmh3.hash(value, seed)
            if hash >= 0:
                hashs.append(hash)
            else:
                hashs.append(self.N - hash)
        return hashs




if __name__ == '__main__':
    import redis

    server = redis.Redis()
    fp = sha1()
    fp.update('排队进去，主要是太热，人太多。以后有机会凉快的时候再去。然后到门口打了个卡！')
    fp = fp.hexdigest()
    pool = redis.ConnectionPool(host='127.0.0.1', port=6379, db=0)
    conn = redis.StrictRedis(connection_pool=pool)

    bf = BloomFilter(conn=conn)
    # bf.add('主要是太热，人太多。以后有机会凉快的时候再去。然后到门口打了个卡！')
    # bf.add('青涩')
    print(bf.is_exist('主要是太热，人太多。以后有机会凉快的时候再去。然后到门口打了个卡！'))
    print(bf.is_exist('青山'))


