#!/usr/bin/env python
import os
from importlib import resources
from collections import defaultdict
from importlib import resources
import math
import torch
import torch.nn as nn
from torch.nn import functional as F

PyTFBS_data_dir = './PyTFBS_data'

def has_non_acgtn_upper(sequence):
	"""只检查大写ACGT字符"""
	valid_chars = {'A', 'C', 'G', 'T', 'N'}
	return any(char.upper() not in valid_chars for char in sequence)

def sequence_to_numbers(sequence, mapping=None):
	# 将ACGT序列转换为数字列表
	if mapping is None:
		mapping = {'A': 0, 'C': 1, 'G': 2, 'T': 3, 'N': 4}
	return [mapping.get(base.upper(), -1) for base in sequence]

def to_base(line_str):
	seq_base = 'ACGT'
	line_blocks = line_str.split('\t')
	line_data = [float(bi) for bi in line_blocks]
	max_index = line_data.index(max(line_data))
	# print(max_index)
	base = seq_base[max_index]
	return base

def read_motif(fasta_file):
	motifs_all = {}
	#fasta = {}
	#motifs = []
	#motif_names = []
	fp = open(fasta_file, 'r')
	header = ''
	seq = ''
	motif = []
	for line in fp:
		line_str = line.rstrip()
		if line_str[0] == '>':
			if header != '':
				#fasta[header] = seq
				#motifs.append(motif)
				#motif_names.append(header)
				motifs_all[header] = (motif, seq)
			header = line_str[1:len(line_str)]
			seq = ''
			motif = []
		else:
			seq += to_base(line_str)
			motif.append(to_mdata_n_frq(line_str))
	else:
		if header != '':
			# fasta[header] = seq
			# motifs.append(motif)
			# motif_names.append(header)
			motifs_all[header] = (motif, seq)
	fp.close()
	return motifs_all

def cal_base_freq(fasta_seqs):
	base_sum = [0.25, 0.25, 0.25, 0.25, 0.25]
	for seq_name in fasta_seqs.keys():
		for base in fasta_seqs[seq_name]:
			if base == 'A' or base == 'a':
				base_sum[0] += 1
			elif base == 'C' or base == 'c':
				base_sum[1] += 1
			elif base == 'G' or base == 'g':
				base_sum[2] += 1
			elif base == 'T' or base == 't':
				base_sum[3] += 1
			elif base == 'N' or base == 'n':
				base_sum[4] += 1
	bsum = sum(base_sum)
	base_freq1 = [bs / bsum for bs in base_sum]
	return base_freq1

def read_motif_single(fasta_file):
	motif_name = ''
	motif = []
	for line in open(fasta_file, 'r'):
		line_str = line.rstrip()
		if line_str == '':
			continue
		if line_str[0] == '>':
			motif_name = line_str[1:len(line_str)]
		else:
			motif.append(to_mdata_n_frq(line_str))
	return motif_name, motif

def cal_base_freq(fasta_seqs):
	base_sum = [0.25, 0.25, 0.25, 0.25, 0.25]
	for seq_name in fasta_seqs.keys():
		for base in fasta_seqs[seq_name]:
			if base == 'A' or base == 'a':
				base_sum[0] += 1
			elif base == 'C' or base == 'c':
				base_sum[1] += 1
			elif base == 'G' or base == 'g':
				base_sum[2] += 1
			elif base == 'T' or base == 't':
				base_sum[3] += 1
			elif base == 'N' or base == 'n':
				base_sum[4] += 1
	bsum = sum(base_sum)
	base_freq1 = [bs / bsum for bs in base_sum]
	return base_freq1

def read_fasta(file):
	fasta = {}
	header = ''
	seq = ''
	seq_id = 0
	for line in open(file, 'r'):
		line_str = line.rstrip()
		if line_str[0] == '>':
			if header != '':
				seq_id += 1
				fasta[header] = seq
			header = line_str[1:len(line_str)]
			seq = ''
		else:
			seq += line_str
	else:
		if header != '':
			seq_id += 1
			fasta[header] = seq
	seq_freq = cal_base_freq(fasta)
	return fasta, seq_freq

def to_mdata_n(line_str):
	seq_base = 'ACGT'
	line_blocks = line_str.split('\t')
	line_data = [float(bi) + 0.25 for bi in line_blocks]
	line_data.append(0.25)
	return line_data

def to_mdata_n_frq(line_str):
	seq_base = 'ACGT'
	line_blocks = line_str.split('\t')
	line_data = [float(bi) + 0.25 for bi in line_blocks]
	line_data.append(0.25)
	sum_base = sum(line_data)
	line_data_frq = [da / sum_base for da in line_data]
	return line_data_frq

'''
def forward(x, params):
	# global parameters
	w1, b1, w2, b2, w3, b3 = params
	x = x @ w1.t() + b1
	x = torch.tanh(x)
	x = x @ w2.t() + b2
	x = torch.tanh(x)
	x = x @ w3.t() + b3
	x = torch.tanh(x)
	return x
'''

def forward(x, params):
	# global parameters
	w1, b1, w2, b2, w3, b3 = params
	x = x @ w1.t() + b1
	x = F.relu(x)
	x = x @ w2.t() + b2
	x = F.relu(x)
	x = x @ w3.t() + b3
	x = F.relu(x)
	return x

def predict_llrs(seq, motif, header, motif_name):
	global parameters
	base_freq, j_mean = parameters['jpar']
	# print('base_freq, j_mean: ', base_freq, j_mean)
	model_pars = parameters['model']
	dseq = sequence_to_numbers(seq)
	seq_len = len(seq)
	motif_len = len(motif)
	j_best = -10.0
	best_pos = 0
	best_llrs = []
	llr_matrix = []
	j_tmps = []
	for si in range(seq_len - motif_len + 1):
		llr_sum = 0.0
		llrs = []
		for mi in range(motif_len):
			base = dseq[si + mi]
			if base == 4:
				llr = 0.0
			else:
				llr = math.log(motif[mi][base] / base_freq[base]);
			llr_sum += llr
			# print(motif[mi][base], base_freq[base])
			llrs.append(llr)
		# llrs_norm = [llr - j_mean for llr in llrs]
		llrs_norm = llrs
		# print('llrs_norm: ', llrs_norm)
		j_tmp = llr_sum / motif_len
		if j_tmp > 0.0:
			llr_matrix.append(llrs_norm)
			j_tmps.append(j_tmp)
	data = torch.tensor(llr_matrix)
	data = data.view(-1, motif_len)
	logits = forward(data, model_pars)
	predict = torch.sigmoid(logits * 4.0)
	# print('predict.shape:', predict.shape)
	col_index = 1
	#indices = torch.nonzero(predict[:, col_index] >= 0.5, as_tuple=False)
	indices = torch.nonzero((predict[:, 1] > 0.75) & (predict[:, 0] < 0.25), as_tuple=False)
	for value in indices:
		match_seq = seq[value.item(): value.item() + motif_len]
		print(header, motif_name, value.item(), match_seq, j_tmps[value.item()], predict[value, 0].item(), predict[value, 1].item())

def predict_seq():
	motifs_all = read_motif('motif_data.txt')
	# fasta, seq_freq = read_fasta('GCF_000001405.40_GRCh38.p14_promoter_1.1k.txt')
	fasta, seq_freq = read_fasta('GCF_000001405.40_GRCh38.p14_promoter_1.1k_rdm1000.txt')
	# print(len(fasta))
	for seq_name in fasta.keys():
		seq = fasta[seq_name].upper()
		if has_non_acgtn_upper(seq):
			continue
		for motif_name in motifs_all.keys():
			if motif_name != 'ANDR_HUMAN.H11MO.0.A':
				continue
			motif = motifs_all[motif_name][0]
			predict_llrs(seq, motif, seq_name, motif_name)

def seq2onehot(seq_in, motif_len, motif, base_freq):
	datas = []
	poss = []
	j_tmps = []
	seq_len = len(seq_in)
	for si in range(seq_len - motif_len + 1):
		seq = seq_in[si: si + motif_len]
		j_tmp = jindex(seq, motif, base_freq)
		# print(j_tmp)
		if j_tmp <= 0.0:
			continue
		poss.append(si)
		j_tmps.append(j_tmp)
		seq_onehot = []
		dseq = sequence_to_numbers(seq.upper())
		for si in dseq:
			sonehot = [0.0, 0.0, 0.0, 0.0, 0.0]
			sonehot[si] = 1.0
			seq_onehot += sonehot
		datas.append(seq_onehot)
	return datas, poss, j_tmps

def jindex(seq, motif, base_freq):
	dseq = sequence_to_numbers(seq)
	motif_len = len(motif)
	llr_sum = 0.0
	for mi in range(motif_len):
		base = dseq[mi]
		if base == 4:
			llr = 0.0
		else:
			llr = math.log(motif[mi][base] / base_freq[base]);
		llr_sum += llr
	j_tmp = llr_sum / motif_len
	return j_tmp

def predict_tfbs(file, motif_name, motif, data_dim, model, base_freq, out_file):
	fasta, seq_freq = read_fasta(file)
	# print(len(fasta))
	motif_len = int(data_dim[0] / 5)
	fp = open(out_file, 'w')
	for seq_name in fasta.keys():
		seq = fasta[seq_name].upper()
		if has_non_acgtn_upper(seq):
			continue
		data_onehot, poss, j_tmps = seq2onehot(seq, motif_len, motif, base_freq)
		data = torch.tensor(data_onehot)
		data = data.view(-1, data_dim[0])
		logits = model(data).flatten().tolist()
		#indices = torch.nonzero(logits > 0.5, as_tuple=False).squeeze().tolist()
		#indices = torch.nonzero(logits[:, 1] > logits[:, 0], as_tuple=False)
		#indices = [i for i, value in enumerate(logits) if value > 0.5]
		for vi in range(len(logits)):
			if logits[vi] > 0.5:
				value = vi
				match_seq = seq[poss[value]: poss[value] + motif_len]
				fp.write('\t'.join([seq_name, str(poss[value]), match_seq, str(j_tmps[value]), str(logits[value])]) + '\n')
	fp.close()

def load_module(file):
	saved_data = torch.load(file)
	base_freq = saved_data['base_freq']
	data_dim = saved_data['data_dim']
	w1 = saved_data['w1']
	b1 = saved_data['b1']
	w2 = saved_data['w2']
	b2 = saved_data['b2']
	w3 = saved_data['w3']
	b3 = saved_data['b3']
	parameters = {'jpar': [base_freq, data_dim], 'model': [w1, b1, w2, b2, w3, b3]}
	return parameters

def read_motif_cmp(file):
	motif_cmp = {}
	for line in open(file, 'r'):
		if line[0: 3] != 'Cmp':
			continue
		lblocks = line.rstrip().split(' ')
		motif_cmp[lblocks[1]] = lblocks[2]
	return motif_cmp

def loade_model_pars(model_file, data_dim):
	# 加载模型参数
	# 首先需要创建相同结构的模型
	global x_dimention
	global optimizer
	model_pars = torch.load(model_file)
	#seq_freq = model_pars['base_freq']
	#data_dim = model_pars['data_dim']
	#del model_pars['base_freq']
	#del model_pars['data_dim']
	x_dimention = data_dim[0]
	y_dimention = data_dim[1]
	# 1. 定义模型
	model = nn.Sequential(
		nn.Linear(x_dimention, 64),
		nn.ReLU(),
		nn.Linear(64, 32),
		nn.ReLU(), 
		nn.Linear(32, 1),
		nn.Sigmoid()
	)
	model.load_state_dict(model_pars)
	#new_model.eval()
	return model

def script(motif_id, model_id, seq_file, out_file, data_dir=None):
	if data_dir == None:
		data_dir = PyTFBS_data_dir
	if not (os.path.exists(data_dir) and os.path.isdir(data_dir)):
		print("PyTFBS_data folder can not found!")
		exit(1)
	motif_file = data_dir + '/motif/' + motif_id + '.pwm'
	model_file = data_dir + '/par/' + model_id + '_par.pth'
	if not os.path.exists(motif_file):
		print(motif_file, 'not exist!')
		exit(1)
	if not os.path.exists(model_file):
		print(model_file, 'not exist!')
		exit(1)
	if not os.path.exists(seq_file):
		print(seq_file, 'not exist!')
		exit(1)
	motif_name, motif = read_motif_single(motif_file)
	data_dim = [len(motif) * 5, 1]
	model = loade_model_pars(model_file, data_dim)
	# run predict
	fasta, seq_freq = read_fasta(seq_file)
	# seq_freq = [0.22698189046475983, 0.2685381453335145, 0.2744548727333858, 0.22957776564437835, 0.00044732582396156444]
	motif_len = len(motif)
	fp = open(out_file, 'w')
	seq_n = len(fasta)
	finished_n = 0
	for seq_name in fasta.keys():
		seq = fasta[seq_name].upper()
		if has_non_acgtn_upper(seq):
			continue
		data_onehot, poss, j_tmps = seq2onehot(seq, motif_len, motif, seq_freq)
		data = torch.tensor(data_onehot)
		data = data.view(-1, data_dim[0])
		logits = model(data).flatten().tolist()
		#indices = torch.nonzero(logits > 0.5, as_tuple=False).squeeze().tolist()
		#indices = torch.nonzero(logits[:, 1] > logits[:, 0], as_tuple=False)
		#indices = [i for i, value in enumerate(logits) if value > 0.5]
		for vi in range(len(logits)):
			if logits[vi] > 0.5:
				value = vi
				match_seq = seq[poss[value]: poss[value] + motif_len]
				fp.write('\t'.join([seq_name, str(poss[value]), match_seq, str(j_tmps[value]), str(logits[value])]) + '\n')
		finished_n += 1
		if finished_n % 100 == 0 or finished_n == seq_n:
			print(str(finished_n) + '/' + str(seq_n))
	fp.close()

def win_bin(motif_id, model_id, seq_file, thread_n, out_file, data_dir=None):
	if data_dir == None:
		data_dir = PyTFBS_data_dir
	if not (os.path.exists(data_dir) and os.path.isdir(data_dir)):
		print("PyTFBS_data folder can not found!")
		exit(1)
	motif_file = data_dir + '/motif/' + motif_id + '.pwm'
	model_file = data_dir + '/trace/' + model_id + '_trace.pth'
	PyTFBS_exe = data_dir + '/PyTFBS_bin/PyTFBS.exe'
	if not os.path.exists(motif_file):
		print(motif_file, 'not exist!')
		exit(1)
	if not os.path.exists(model_file):
		print(model_file, 'not exist!')
		exit(1)
	if not os.path.exists(seq_file):
		print(seq_file, 'not exist!')
		exit(1)
	cmd = '\"' + PyTFBS_exe + '\" -m ' + motif_file + ' -z ' + model_file + ' -i ' + seq_file + ' -t ' + str(thread_n) + ' -o ' + out_file + ''
	cmd = cmd.replace('/', '\\')
	print(cmd)
	os.system(cmd)

if __name__ == '__main__':
	script('CEBPB_HUMAN.H11MO.0.A', 'CEBPB_HUMAN.H11MO.0.A_1231', 'GCF_000001405.40_GRCh38.p14_promoter_1.1k.txt', 'out_file.txt')
