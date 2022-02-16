# File location: C:\ProgramData\Anaconda3\envs\gpu\Lib\site-packages\Toolchain\DataTools.py
# This class is used for data manipulation for ML on datasets

import numpy
import pandas

from time                               import time
import os
# GPU RELATED IMPORTS
import tensorflow as tf
from .terminal import *
import torch


def read_from_file(file,matrix,docwords,lines=None):
    line_n = 0
    next_percent = .02
    top_str = ''.join(['=' for _ in range(49)])
    top_str = f"{top_str[:20]}PERCENT{top_str[27:]}"
    printc(f"\t[{top_str}]",CYAN)
    printc("\t[",CYAN,endl='')
    for line in file:
        doc, word, count = line.split(' ')
        matrix[int(doc),int(word)] = int(count)
        try:
            docwords[int(doc)].append(count)
        except KeyError:
            docwords[int(doc)] = [int(count)]
        if not lines is None and (float(line_n) / lines) > next_percent:
            printc("=",CYAN,endl='')
            next_percent += .02
        line_n += 1
    printc("]\n",CYAN)

def load_data(vocab_file="vocab.nytimes.txt",dataset_file='docword.nytimes.txt',read_npz=False,npz_name="preSVD.npz",saving_npz=False,gpuMode=False):
    printc(f"Starting: Data Read",BLUE)
    times = {'start':time()}
    vocab = {}
    docwords = {}


    # READ THE VOCABULARY
    printc(f"\treading vocab from '{RED}{vocab_file}{TAN}'",TAN)
    with open(vocab_file,'r') as file:
        for i, word in enumerate(file.readlines()):
            vocab[i] = word
    printc(f"\tread {len(vocab)} words in {(time()-times['start']):.3f} seconds\n",TAN)


    # READING FROM preSVD.npz
    if read_npz:
        # READ THE FULL DATASET
        times['read'] = time()
        fname = f"'{TAN}{npz_name}{TAN}'"
        printc(f"\treading data from {fname} - precomputed",TAN)
        matrix = load_npz(str(npz_name))
        printc(f"\tread {fname} in {(time()-times['read']):.3f}\n",TAN)

        printc(f"\tFinished: Data Read in {(time() - times['start']):.3f} seconds",GREEN)
        printc(f"\tReturning: matrix: {matrix.shape} - size {matrix.data.size/(1024**2):.2f} MB", GREEN)
        printc(f"\t           vocab: {len(vocab)}\n\n",GREEN)



    # READING DIRECT
    else:
        with open(dataset_file,'r') as file:
            n_articles      = int(file.readline())
            n_words         = int(file.readline())
            n_words_total   = int(file.readline())

            # define the size of the dataset we will build
            rows = n_articles	+	1
            cols = n_words		+	1

            # initialize an lil matrix (faster to fill)
            matrix = scipy.sparse.lil_matrix( (rows,cols), dtype = cupy.float64)

            # Step through each article and see which word appeared in it
            times['read'] = time()
            printc(f"\treading data from {dataset_file} - from base file",TAN)

            read_from_file(file,matrix,docwords,lines=n_words_total)
            printc(f"\tread {dataset_file} in {(time()-times['read']):.3f} seconds\n",TAN)

        times['convert'] = time()
        printc(f"\tconverting lil_matrix to csr_matrix",TAN)
        matrix = matrix.tocsr()
        printc(f"\tconverted matrix in {(time()-times['convert']):.3f} seconds\n",TAN)

        if saving_npz:
            times['saving'] = time()
            printc(f"\tsaving matrix to preSVD.npz",TAN)
            save_npz("preSVD.npz",matrix)
            printc(f"\twrote matrix to preSVD.npz in {(time()-times['saving']):.3f}\n",TAN)

        printc(f"\tFinished: Data Read in {(time() - times['start']):.3f} seconds",GREEN)
        printc(f"\tReturning: matrix: {matrix.shape} - size {matrix.data.size/(1024**2):.2f} MB", GREEN)
        printc(f"\t           vocab: {len(vocab)}\n\n",GREEN)

    if gpuMode:
        matrix = cupy.sparse.csr_matrix(matrix)
    return matrix, docwords


def svd_decomp(matrix_type='sparse',n=10,matrix=None):
    printc(f"Starting: Data Decomposition",BLUE)
    times = {'start' : time()}
    printc(f"\tdecomposing matrix {matrix_type} of shape {matrix.shape} of type {type(matrix)}",TAN)
    if matrix_type == 'sparse':
        U, S, Vt = svds(matrix,k=50,return_singular_vectors=True,maxiter=10000,ncv=1000)
        printc(f"{Vt}",TAN)
        printc(f"\tOperands:",TAN)
        printc(f"\t\tU:{U.shape}",TAN)
        printc(f"\t\tS:{cupy.diag(S).shape}",TAN)
        printc(f"\t\tVt:{Vt.shape}",TAN)
        print(type(U.get()))
        U = csr_matrix(U)
        S = csr_matrix(cupy.diag(S))
        Vt = csr_matrix(Vt)
        matrix_reduced = U.multiply(S).multiply(Vt)
        printc(f"\t\toutput:{matrix_reduced.shape}",TAN)
    else:
        model = SVD(n_components=n)
    printc(f"\treduced in {(time()-times['start']):.3f} seconds\n",TAN)

    return matrix_reduced, time()-times['start']


def PCA_decomp(matrix_type='sparse',n=10,matrix=None):
    printc(f"Starting: Data Decomposition",BLUE)
    times = {'start' : time()}
    printc(f"\tbuilding model of type {matrix_type}",TAN)
    if matrix_type == 'sparse':
        model = PCA(n_components=n)
    else:
        model = SVD(n_components=n)
    printc(f"\tmodel built in {(time()-times['start']):.3f} seconds\n",TAN)

    if not input is None:
        times['fit'] = time()
        printc(f"\tfitting matrix shape: {matrix.shape} - to {n} vectors",TAN)
        fitted_data = model.fit_transform(matrix)
        printc(f"\treduced matrix shape: {fitted_data.shape}\n",TAN)
        printc(f"\treduced matrix var  : {model.explained_variance_ratio_.sum():.3f}", TAN)
        printc(f"\tmatrix reduced in {(time()-times['fit']):.3f} seconds",TAN)
        return fitted_data,model, time()-times['fit']
    else:
        return None, model


def run_kmeans_verbose(matrix,move):
    t1 = time()
    bSize = 10000
    printc(f"Starting KMeans",BLUE)
    a = matrix
    models = {}
    for k in [50,100,500,1000,5000,10000]:
        models[k] = {'centers': None, 'd_to_c' : None, 'inertia' : 0}
        t2 = time()
        printc(f"\tStarting k={k} on {a.shape}:",BLUE)
        model = MiniBatchKMeans(n_clusters=k, batch_size = bSize,n_init=3)
        model.fit(a)
        printc(f"\t\tcomputed model k={k} in {time()-t2} seconds:",TAN)
        printc(f"\t\tk={k} inertia: {model.inertia_}",TAN)
        models[k]['inertia'] = model.inertia_
        models[k]["centers"] = model.cluster_centers_
        models[k]['d_to_c'] = model.predict(a)
        printc(f"\t\tpredict finished - writing files",TAN)
        np.save(f"data/{k}_centers",models[k]['centers'])
        np.save(f"data/{k}_d_to_clusters",models[k]['d_to_c'])
        printc(f"\t\tFinished model in {time()-t2} seconds",GREEN)

    return models


def rmse(A,B):
    printc(f"A: {A.shape}, B: {B.shape}",RED)
    input()
    sub   = A - B
    sub = csr_matrix(sub)
    sub   = sub.multiply(sub) #elementwise multiplication
    (n,m) = sub.shape
    mse   = csr_matrix((sub.sum()/(n*m)).sum())
    return mse.sqrt()
