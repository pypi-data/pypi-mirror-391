'''
QKMeans (Quantum K-Means) is a quantum algorithm that is used for clustering data into k clusters,
where k is a user-specified parameter. It is an extension of the classical K-Means algorithm,
which is widely used in machine learning and data analysis.
QKMeans has the potential to provide speedup over classical K-Means when processing large datasets.
'''


from .QuantumKmeans import QuantumKmeans

__all__ = ['QuantumKmeans']