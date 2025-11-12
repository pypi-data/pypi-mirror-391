# from importlib import resources
import urllib.request
import zipfile
import os
from pathlib import Path

PyTFBS_data_dir = './PyTFBS_data'

def download_with_progress(url, filename=None):
	"""
	带进度显示的下载函数
	"""
	def progress_callback(block_num, block_size, total_size):
		"""
		进度回调函数
		
		Args:
			block_num: 当前已下载的块数量
			block_size: 每个块的大小（字节）
			total_size: 文件总大小（字节）
		"""
		downloaded = block_num * block_size
		percent = downloaded / total_size * 100 if total_size > 0 else 0
		
		# 限制显示频率，避免刷新太快
		if block_num % 100 == 0 or downloaded >= total_size:
			print(f"\rProgress: {percent:.1f}% ({downloaded}/{total_size} bytes)", end='', flush=True)
	
	# 如果没有指定文件名，从URL中提取
	if filename is None:
		filename = os.path.basename(url)
	
	print(f"start download: {url}")
	print(f"save as: {filename}")
	
	try:
		urllib.request.urlretrieve(url, filename, progress_callback)
		print("donwload sucessful")
	except Exception as e:
		print(f"donwload failed: {e}")
		exit(1)

# 使用示例
# download_with_progress("https://example.com/largefile.zip", "downloaded_file.zip")

def extractall_individual_files(zip_path, extract_path):
	"""
	使用 extract() 方法逐个解压文件，确保覆盖
	"""
	os.makedirs(extract_path, exist_ok=True)
	
	with zipfile.ZipFile(zip_path, 'r') as zip_ref:
		# 获取所有成员信息
		members = zip_ref.infolist()
		
		print(f"extracting {len(members)} file...")
		
		for i, member in enumerate(members, 1):
			try:
				# 直接使用 extract() 方法，它会处理覆盖
				zip_ref.extract(member, extract_path)
				
				if i % 10 == 0 or i == len(members):
					print(f"progress: {i}/{len(members)}")
					
			except Exception as e:
				print(f"extracting failed {member.filename}: {e}")
				exit(1)
	
	print("extracting finished")

# 使用示例
# extractall_individual_files("example.zip", "extracted_files")

def download_and_extract_zip(url, extract_to):
	"""
	下载ZIP文件并解压到指定目录
	
	Args:
		url: ZIP文件的URL
		extract_to: 解压目标目录
	"""
	# 创建目标目录
	Path(extract_to).mkdir(parents=True, exist_ok=True)
	
	# 临时ZIP文件路径
	zip_path = os.path.join(extract_to, "temp.zip")
	
	try:
		# 下载文件
		# print(f"downloading: {url}")
		# urllib.request.urlretrieve(url, zip_path)
		download_with_progress(url, zip_path)
		# print("donwload finished")
		
		# 解压文件
		# print(f"extracting: {extract_to}")
		# with zipfile.ZipFile(zip_path, 'r') as zip_ref:
		# 	zip_ref.extractall(extract_to, overwrite=True)
		extractall_individual_files(zip_path, extract_to)
		# print("extract finished")
		
	except Exception as e:
		print(f"错误: {e}")
		return False
	finally:
		# 清理临时ZIP文件
		if os.path.exists(zip_path):
			os.remove(zip_path)
			print("clearing temp files")
	
	return True

def download_data(data_dir=None):
	if data_dir == None:
		data_dir = PyTFBS_data_dir
	if not (os.path.exists(data_dir) and os.path.isdir(data_dir)):
		print(data_dir, 'not exist, creating...')
		folder_path = Path(data_dir)
		folder_path.mkdir(exist_ok=True)
	url = "http://www.thua45.cn/PyTFBS/PyTFBS_data.zip"
	extract_dir = data_dir
	# extract_dir = "./downloaded_content"
	success = download_and_extract_zip(url, extract_dir)
	if success:
		print("models installed successful")

def list_models(motif_name=None, species=None, accuracy=None, sensitivity=None, data_dir=None):
	if data_dir == None:
		data_dir = PyTFBS_data_dir
	index_file = data_dir + '/motif_index.txt'
	if not os.path.exists(index_file):
		print('motif_index.txt not exist, you may need to run download_data() first')
		exit(1)
	header = ''
	result = []
	for line in open(index_file, 'r'):
		if line[0] == "#":
			header = line.rstrip()
			continue
		lblocks = line.rstrip().split('\t')
		if motif_name != None and lblocks[0] != motif_name:
			continue
		if species != None and lblocks[1] != species:
			continue
		if accuracy != None and float(lblocks[3]) < accuracy:
			continue
		if sensitivity != None and float(lblocks[4]) < sensitivity:
			continue
		result.append(lblocks)
	print(header)
	for rline in result:
		print('\t'.join(rline))

def get_motifs(motif_name=None, species=None, accuracy=None, sensitivity=None, data_dir=None):
	if data_dir == None:
		data_dir = PyTFBS_data_dir
	index_file = data_dir + '/motif_index.txt'
	if not os.path.exists(index_file):
		print('motif_index.txt not exist, you may need to run download_data() first')
		exit(1)
	header = ''
	result = []
	for line in open(index_file, 'r'):
		if line[0] == "#":
			header = line.rstrip()
			continue
		lblocks = line.rstrip().split('\t')
		if motif_name != None and lblocks[0] != motif_name:
			continue
		if species != None and lblocks[1] != species:
			continue
		if accuracy != None and float(lblocks[3]) < accuracy:
			continue
		if sensitivity != None and float(lblocks[4]) < sensitivity:
			continue
		result.append(lblocks[0])
	return result

def get_models(motif_name, data_dir=None):
	if data_dir == None:
		data_dir = PyTFBS_data_dir
	index_file = data_dir + '/motif_index.txt'
	if not os.path.exists(index_file):
		print('motif_index.txt not exist, you may need to run download_data() first')
		exit(1)
	models = []
	for line in open(index_file, 'r'):
		if line[0] == "#":
			header = line.rstrip()
			continue
		lblocks = line.rstrip().split('\t')
		if lblocks[0] != motif_name:
			continue
		models.append(lblocks[2])
	return {'motif_name': motif_name, 'models': models}
