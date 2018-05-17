#include <iostream>
#include <fstream>
#include <string>
#include <cmath>

using namespace std;

#define DATA_READ 0
#define DATA_WRITE 1
#define INS_READ 2

class cache {
public:
	string name;
	int L, K, N, level,	
		instr_miss_cnt, data_miss_cnt, hit_cnt, write_cnt;

	cache(int tag_size, int index_size, int offset_size, int L, int K, int N);
	~cache();
	void set_hit_time(int new_time);
	void set_penalty_time(int data, int instr, int write);
	bool access(int type, long long addr);
	void return_performance();
	double get_miss_penalty();
	void set_lower_cache(cache* low_cache);

private:
	int hit_time, data_miss_penalty, ins_miss_penalty, write_penalty;
	long long tag_mask, index_mask, offset_mask;
	long long** addr;
	int** LRU_cnt;
	int** data;
	cache* lower_level;
};