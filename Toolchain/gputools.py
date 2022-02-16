################################################################################
#                           IMPORTS
################################################################################
import tensorflow as tf
from .terminal import *

# Computes the euclidean distance of tensors A and B
@tf.function
def euclidean_distance(A,B):
    # 4 - return the squareroot of the sumMatrix
    return tf.math.reciprocal(tf.norm(A-B,ord='euclidean'))

def euclidean_distance_noF(A,B):
    # 4 - return the squareroot of the sumMatrix
    return tf.math.reciprocal(tf.norm(A-B,ord='euclidean'))

def slice_col(matrix,index):
    if isinstance(matrix,tf.sparse.SparseTensor):
        column_matrix_sparse    =   tf.sparse.slice(    matrix,     [0,index],     [matrix.shape[0],1])
        return                      tf.sparse.to_dense(column_matrix_sparse)
    elif isinstance(matrix,tf.Tensor):
        a  = tf.gather(matrix,indices=index,axis=1)
        return a

def slice_row(matrix,index):
    if isinstance(matrix,tf.sparse.SparseTensor):
        row_matrix_sparse       =  tf.sparse.reorder( tf.sparse.slice(    matrix,     [index,0],     [1,matrix.shape[1]]))
        return                     tf.sparse.to_dense(row_matrix_sparse,dtype=tf.dtypes.float64)
    elif isinstance(matrix,tf.Tensor):
        a = tf.gather(matrix,indices=index,axis=0)
        return a

@tf.function
def map_func(fun,input):
    return      tf.map_fn(      self.euclidean_caller,
                                self.matrix)
def map_func_noF(fun,input):
    return      tf.map_fn(      self.euclidean_caller,
                                self.matrix)
