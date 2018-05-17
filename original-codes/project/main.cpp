
// main.cpp

#include "header.h"
#include <iostream>
#include <fstream>
#include <string>
#include <cmath>

#define DATA_READ 0
#define DATA_WRITE 1
#define INS_READ 2

#define L1_HIT_PENALTY 4
#define L1_READ_MISS_PENALTY 16
#define L1_INS_MISS_PENALTY 16
#define L1_WRITE_MISS_PENALTY 16

#define L2_HIT_PENALTY 16
#define L2_READ_MISS_PENALTY 32
#define L2_INS_MISS_PENALTY 32
#define L2_WRITE_MISS_PENALTY 32

//#define L2_HIT_PENALTY 16
//#define L2_READ_MISS_PENALTY 120  
//#define L2_INS_MISS_PENALTY 120
//#define L2_WRITE_MISS_PENALTY 120

#define L3_HIT_TIME 32
#define L3_READ_MISS_PENALTY 120  
#define L3_INS_MISS_PENALTY 120
#define L3_WRITE_MISS_PENALTY 120

#define WORDS_PER_LINE 16
#define WORD_SIZE 4	
#define ADDR_BIT 32

void run_cache(char* tracename, int L1_size, int L2_size, int L3_size);
cache* make_cache(string name, int K, int size, int block);

void run_cache(char* tracename, int L1_size, int L2_size, int L3_size) {

	cache* L1_inst_cache = make_cache("L1 instruction cache", 2, L1_size, 1);
	L1_inst_cache->set_hit_time(L1_HIT_PENALTY);
	L1_inst_cache->level = 1;
	L1_inst_cache->set_penalty_time(L1_READ_MISS_PENALTY, L1_INS_MISS_PENALTY, L1_WRITE_MISS_PENALTY);

	cache* L1_data_cache = make_cache("L1 data cache", 2, L1_size, 1);
	L1_data_cache->set_hit_time(L1_HIT_PENALTY);
	L1_data_cache->level = 1;
	L1_data_cache->set_penalty_time(L1_READ_MISS_PENALTY, L1_INS_MISS_PENALTY, L1_WRITE_MISS_PENALTY);

	cache* L2_cache = make_cache("L2 unified cache", 8, L2_size, 1);
	L2_cache->set_hit_time(L2_HIT_PENALTY);
	L2_cache->level = 2;
	L2_cache->set_penalty_time(L2_READ_MISS_PENALTY, L2_INS_MISS_PENALTY, L2_WRITE_MISS_PENALTY);

	cache* L3_cache = make_cache("L3 unified cache", 1, L3_size, 1);
	L3_cache->set_hit_time(L3_HIT_TIME);
	L3_cache->level = 3;
	L3_cache->set_penalty_time(L3_READ_MISS_PENALTY, L3_INS_MISS_PENALTY, L3_WRITE_MISS_PENALTY);

	L1_inst_cache->set_lower_cache(L2_cache);
	L1_data_cache->set_lower_cache(L2_cache);
	L2_cache->set_lower_cache(L3_cache);

	int type;
	long long addr;
	ifstream input(tracename);
	if (!input.is_open()) {
		cout << "file open error" << endl;
		return;
	}

	while (!input.eof()) {
		input >> std::dec;
		input >> type;
		input >> std::hex;
		input >> addr;
		if (type == INS_READ)
			L1_inst_cache->access(type, addr);
		else
			L1_data_cache->access(type, addr);
	}
	input.close();

	L1_inst_cache->return_performance();
	L1_data_cache->return_performance();

	delete L1_inst_cache;
	delete L1_data_cache;
	delete L2_cache;
	delete L3_cache;
}

cache* make_cache(string name, int K, int size, int block) {
	cache* a_cache;
	int tag_bit, index_bit, offset_bit, tmp, number_of_sets, number_of_blocks;
	int block_size = WORDS_PER_LINE * WORD_SIZE * block;
	ofstream fout("result.txt", ios::app);

	offset_bit = 0;
	for (tmp = WORDS_PER_LINE; tmp > 1; tmp /= 2)
		offset_bit++;

	size *= 1024;

	cout << "Size of a block = " << block_size << " bytes" << endl;
	cout << name << " cache size = " << size << " bytes" << endl;

	fout << "Size of a block = " << block_size << " bytes" << endl;
	fout << name << " cache size = " << size << " bytes" << endl;

	number_of_blocks = size / block_size;
	number_of_sets = number_of_blocks / K;

	cout << "  number of blocks = " << number_of_blocks << endl;
	cout << "  K = " << K << " (-way associated)" << endl;
	cout << "  number of sets = " << number_of_sets << endl;

	fout << "  number of blocks = " << number_of_blocks << endl;
	fout << "  K = " << K << " (-way associated)" << endl;
	fout << "  number of sets = " << number_of_sets << endl;

	index_bit = 0;
	for (tmp = number_of_sets; tmp > 1; tmp /= 2)
		index_bit++;

	tag_bit = ADDR_BIT - index_bit - offset_bit;

	cout << "  tag size = " << tag_bit << " bits" << endl;
	cout << "  index size = " << index_bit << " bits" << endl;
	cout << "  offset size = " << offset_bit << " bits" << endl;

	fout << "  tag size = " << tag_bit << " bits" << endl;
	fout << "  index size = " << index_bit << " bits" << endl;
	fout << "  offset size = " << offset_bit << " bits" << endl;

	fout.close();

	a_cache = new cache(tag_bit, index_bit, offset_bit, WORDS_PER_LINE, K, number_of_sets);
	a_cache->name = name;

	return a_cache;
}


int main() {

	//run_cache("astar", 32, 256, 1024);
	run_cache("bzip2", 32, 256, 1024);
	return 0;
}