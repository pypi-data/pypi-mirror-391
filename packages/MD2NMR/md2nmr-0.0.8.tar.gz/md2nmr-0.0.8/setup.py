from setuptools import setup, find_packages

setup(
    name="MD2NMR",
    version="0.0.8",
    author="Tiejun Wei and Houfang Zhang",
    description="Tools for calculating NMR relaxation observables (R1/R2/NOE/T1/T2/Tau_c) directly from MD trajectories. Initially written for calculations regarding nucleosome simulations but can be extended for other proteins/complexes.",
    url="https://github.com/CCNU-COMPBIO/MD2NMR",
    packages=find_packages(),
    install_requires=["numpy>=1.21,<3.0",
                      "pandas>=1.3,<3.0",
                      "scikit-learn>=1.0,<2.0",
                      "scipy>=1.7,<2.0",
                      "MDAnalysis>=2.8,<3.0",
                      "matplotlib>=3.4,<4.0",
                      "setuptools>=61.0"],
)
