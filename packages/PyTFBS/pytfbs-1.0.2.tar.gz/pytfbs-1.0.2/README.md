# PyTFBS

A Python package for dpredicting transcription factor binding sites.

## Installation

```bash
pip install torch numpy PyTFBS
```

## Usage

```python
from PyTFBS import motif, predict

# download PyTFBS data, only need to run once!!!
motif.download_data()

# list available models
motif.list_models(species='Homo sapiens', accuracy=0.9, sensitivity=0.9)

# get avaiable motifs
motifs = motif.get_motifs(species='Homo sapiens', accuracy=0.9, sensitivity=0.9)
print(motifs)

# get models based on motif name
models = motif.get_models('RFX2_HUMAN.H11MO.0.A')
print(models)

# predict one model
predict.script('CEBPB_HUMAN.H11MO.0.A', 'CEBPB_HUMAN.H11MO.0.A_1231', 'input_seq_file.fasta', 'out_file.txt')

# speed up using mutil-threading (for Windows OS only)
predict.win_bin('CEBPB_HUMAN.H11MO.0.A', 'CEBPB_HUMAN.H11MO.0.A_1231', 'input_seq_file.fasta', 64, 'out_file.txt')

# run prediction with user motif data
# the my_motif_dir should be organized as [[motif], [trace], [par]]
predict.script('CEBPB_HUMAN.H11MO.0.A', 'CEBPB_HUMAN.H11MO.0.A_1231', 'input_seq_file.fasta', data_dir='my_motif_dir')
predict.win_bin('CEBPB_HUMAN.H11MO.0.A', 'CEBPB_HUMAN.H11MO.0.A_1231', 'input_seq_file.fasta', 64, data_dir='my_motif_dir')
```