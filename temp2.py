import matplotlib.pyplot as plt
import numpy as np

a = np.array([[1, 2], [3, 4]])
b = np.array([[5, 6]])

z = np.concatenate((b.T, a.T), axis=1)
print(z)