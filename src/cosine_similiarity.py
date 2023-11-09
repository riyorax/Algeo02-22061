import numpy as np

def cosine_similiarity(v1,v2):
    dot_prod = np.dot(v1,v2)
    norm_v1 = np.linalg.norm(v1)
    norm_v2 = np.linalg.norm(v2)
    if norm_v1 == 0 or norm_v2 == 0:
        return 0
    else:
        return (dot_prod/(norm_v1*norm_v2))