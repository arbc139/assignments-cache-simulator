#include "header.h"

using namespace std;

//Constructor
cache::cache(int tag_size, int index_size, int offset_size, int L, int K, int N) {
	int i, j;

	this->addr = new long long*[N];
	this->LRU_cnt = new int*[N];
	this->L = L;
	this->K = K;
	this->N = N;
	this->lower_level = NULL;
	this->hit_cnt = 0;
	this->data_miss_cnt = 0;
	this->instr_miss_cnt = 0;
	this->write_cnt = 0;

	for (i = 0; i < N; i++) {
		this->addr[i] = new long long[K];
		this->LRU_cnt[i] = new int[K];
		for (j = 0; j < K; j++) {
			this->addr[i][j] = -1;
			this->LRU_cnt[i][j] = 0;
		}
	}

	this->tag_mask = 0;
	for (i = 0; i < tag_size; i++) {
		this->tag_mask *= 2;
		this->tag_mask += 1;
	}
	this->tag_mask = this->tag_mask << index_size;
	this->tag_mask = this->tag_mask << offset_size;
											
	this->index_mask = 0;
	for (i = 0; i < index_size; i++) {
		this->index_mask *= 2;
		this->index_mask += 1;
	}
	this->index_mask = this->index_mask << offset_size;

	this->offset_mask = 0;
	for (i = 0; i < L; i++) {
		this->offset_mask *= 2;
		this->offset_mask += 1;
	}
}

cache::~cache() {
	int i;
	for (i = 0; i < this->N; i++) {
		delete this->addr[i];
		delete this->LRU_cnt[i];
	}

	delete this->addr;
	delete this->LRU_cnt;
}

void cache::set_hit_time(int new_time) {
	this->hit_time = new_time;
}
void cache::set_penalty_time(int data, int instr, int write) {
	this->data_miss_penalty = data;
	this->ins_miss_penalty = instr;
	this->write_penalty = write;
}


void cache::set_lower_cache(cache* new_low_cache) {
	this->lower_level = new_low_cache;
}
bool cache::access(int type, long long addr) {
	int set_number, i, j, max_cnt = 0, max_i, max_j;
	set_number = addr & this->index_mask;
	set_number = set_number >> this->offset_mask;

	if (set_number >= N || set_number < 0) {
		cout << "Error occur : set number = " << set_number << endl;
		getchar();
	}

	for (i = 0; i < this->N; i++) {
		for (j = 0; j < this->K; j++) {
			this->LRU_cnt[i][j]++;

			if (i == set_number && LRU_cnt[i][j] > max_cnt) {
				max_cnt = LRU_cnt[i][j];
				max_i = i;
				max_j = j;
			}
		}
	}

	for (i = 0; i < this->K; i++) {
		if ((this->addr[set_number][i] & this->tag_mask) == (addr & this->tag_mask)) {
			this->hit_cnt++;
			this->LRU_cnt[set_number][i] = 0;
			return true;
		}
	}

	if (type == INS_READ) {
		this->instr_miss_cnt++;
	}
	if (type == DATA_READ) {
		this->data_miss_cnt++;
	}

	this->LRU_cnt[max_i][max_j] = 0;
	this->addr[max_i][max_j] = addr;

	if (type == DATA_WRITE)
		this->write_cnt++;

	if (this->lower_level != NULL)
		if (this->lower_level->access(type, addr))
			return true;

	return false;
}

void cache::return_performance() {
	double cnt_all = this->hit_cnt + this->data_miss_cnt + this->instr_miss_cnt + this->write_cnt;
	double data_miss_rate = (double)this->data_miss_cnt / cnt_all;
	double inst_miss_rate = (double)this->instr_miss_cnt / cnt_all;
	double data_write_rate = (double)this->write_cnt / cnt_all;
	double all_mis_rate = (data_miss_rate * inst_miss_rate + data_write_rate);
	ofstream fout("result.txt", ios::app);

	cout << this->name << " simulation result" << endl;
	cout << "\thit count = " << this->hit_cnt << " (hit time = " << this->hit_time << ")" << endl;
	cout << "\tdata read miss count = " << this->data_miss_cnt << endl;
	cout << "\tdata read miss rate = " << data_miss_rate << " (miss penalty = " << this->data_miss_penalty << ")" << endl;
	cout << "\tdata write miss count = " << this->write_cnt << endl;
	cout << "\tdata write miss rate = " << data_write_rate << " (miss penalty = " << this->write_penalty << ")" << endl;
	cout << "\tinstruction miss count = " << this->instr_miss_cnt << endl;
	cout << "\tinstruction miss rate = " << inst_miss_rate << " (miss penalty = " << this->ins_miss_penalty << ")" << endl;
	cout << "\ttotal miss count = " << (this->data_miss_cnt + this->instr_miss_cnt + this->write_cnt) << endl;
	cout << "\ttotal miss rate = " << (data_miss_rate + data_write_rate + inst_miss_rate) << endl;

	cout << "Average Memory Access Time = ";

	fout << this->name << " simulation result" << endl;
	fout << "\thit count = " << this->hit_cnt << " (hit time = " << this->hit_time << ")" << endl;
	fout << "\tdata read miss count = " << this->data_miss_cnt << endl;
	fout << "\tdata read miss rate = " << data_miss_rate << " (miss penalty = " << this->data_miss_penalty << ")" << endl;
	fout << "\tdata write miss count = " << this->write_cnt << endl;
	fout << "\tdata write miss rate = " << data_write_rate << " (miss penalty = " << this->write_penalty << ")" << endl;
	fout << "\tinstruction miss count = " << this->instr_miss_cnt << endl;
	fout << "\tinstruction miss rate = " << inst_miss_rate << " (miss penalty = " << this->ins_miss_penalty << ")" << endl;
	fout << "\ttotal miss count = " << (this->data_miss_cnt + this->instr_miss_cnt + this->write_cnt) << endl;
	fout << "\ttotal miss rate = " << (data_miss_rate + data_write_rate + inst_miss_rate) << endl;

	fout << "Average Memory Access Time = ";

	double amat = this->hit_time;
	if (this->lower_level != NULL) {
		amat += (all_mis_rate * this->lower_level ->get_miss_penalty());
	}
	else {
		amat += (data_miss_rate * this->data_miss_penalty);
		amat += (data_write_rate * this->write_penalty);
		amat += (inst_miss_rate * this->ins_miss_penalty);
	}
	cout << amat << endl;
	fout << amat << endl << endl << endl;
	fout.close();

	if (this->lower_level != NULL)
		this->lower_level->return_performance();
}

double cache::get_miss_penalty() {
	double cnt_all = this->hit_cnt + this->data_miss_cnt + this->instr_miss_cnt + this->write_cnt;
	double data_miss_rate = (double)this->data_miss_cnt / cnt_all;
	double inst_miss_rate = (double)this->instr_miss_cnt / cnt_all;
	double data_write_rate = (double)this->write_cnt / cnt_all;

	double penalty = this->hit_time;

	if (this->lower_level != NULL) {
		penalty += ((data_miss_rate * inst_miss_rate + data_write_rate) * this->lower_level->get_miss_penalty());
	}

	else {
		penalty += (data_miss_rate * this->data_miss_penalty);
		penalty += (data_write_rate * this->write_penalty);
		penalty += (inst_miss_rate * this->ins_miss_penalty);
	}

	return penalty;
}