import numpy as np 
import pandas as pd 
from matplotlib import pyplot as plt 
import seaborn as sns 
from tqdm import tqdm
import sympy as sp

def newton_raphson(max_iter=50, x0=None, function=None, tol=0, function_plot=False,analysis_range=None, derivative=None, dataframe=False, graph=False, final_row=False, result=True, verbose=True, learning_rate=1):

    if function is None:
        raise ValueError("Provide a function.")

    if x0 is None:
        raise ValueError("Provide an initial guess x0.")

    if analysis_range is not None and not function_plot:
        raise ValueError("analysis_range is invalid when function_plot=False.")

    if analysis_range is None:
        analysis_range = [-100, 100]

    

    a = x0
    array_list = []

    for i in range(max_iter):
        f_a = function(a)
        f_a_prime = derivative(a)
        if f_a_prime == 0:
            raise ZeroDivisionError(f"Derivative is zero at iteration {i}, x={a}.")
        c = a - learning_rate*(f_a/f_a_prime)
        f_c = function(c)

        if abs(f_c) < tol:
            a = c
            break

        array_list.append(np.array([a, f_a, f_a_prime, c, f_c]))
        a = c

    if verbose:
        iterator = tqdm(range(max_iter), desc="Newton-Raphson", unit="iter", dynamic_ncols=True)
        for i in iterator:
            iterator.set_postfix({"x": a, "f(x)": f_a, "f'(x)": f_a_prime, "next x": c, "converge": f_c})

    df = pd.DataFrame(array_list, columns=['x', 'f(x)', "f'(x)", 'next_x', 'converge'])

    results = []

    if result:
        results.append(df.iloc[-1, 4])  

    if function_plot:
        x_vals = np.arange(analysis_range[0], analysis_range[1], 0.001)
        y_vals = function(x_vals)
        sns.lineplot(x=x_vals, y=y_vals)
        plt.title('Function Plot')
        plt.grid(True)
        plt.show()

    if final_row:
        results.append(df.iloc[-1, :])

    if dataframe:
        results.append(df)

    if graph:
        sns.lineplot(data=df[['x', 'next_x']])
        plt.xlabel('Iteration')
        plt.ylabel('Value')
        plt.title('Iteration vs x and next_x')
        plt.grid(True)
        plt.show()

    if not results:
        return df.iloc[-1, :]
    elif len(results) == 1:
        return results[0]
    else:
        return tuple(results)
    

def regula_falsi(max_iter=50, a=None,b=None,function=None, tol=0, function_plot=False, analysis_range=None, dataframe=False, graph=False, final_row=False, result=True, verbose=True):

    if function is None:
        raise ValueError("Provide a function.")

    if a is None or b is None:
        raise ValueError("Provide a and b. a and b must be in the continuous portion of the graph.")

    if function(a) * function(b) > 0:
        raise ValueError("f(a)*f(b) > 0. Provide a and b such that f(a)*f(b) < 0")

    if analysis_range is not None and not function_plot:
        raise ValueError("analysis_range is invalid when function_plot=False.")

    if analysis_range is None:
        analysis_range = [-100, 100]

    array_list = []
    for i in range(max_iter):
        f_a = function(a)
        f_b = function(b)

        c = (a*f_b - b*f_a) / (f_b - f_a)
        f_c = function(c)

        array_list.append(np.array([a, b, f_a, f_b, c, f_c]))

        if abs(f_c) < tol:     
            a = b = c
            break
        if f_a * f_c < 0:
            b = c
        elif f_b * f_c < 0:
            a = c

        if abs(b-a) <= tol:
            break

    if verbose:
        iterator = tqdm(range(max_iter), desc="Regula-Falsi", unit="iter", dynamic_ncols=True)
        for i in iterator:
            iterator.set_postfix({"a": a, "b": b, "f(a)": f_a, "f(b)": f_b, "c": c, "converge": f_c})

    df = pd.DataFrame(array_list, columns=(['a','b','f(a)','f(b)','c','converge']))

    results = []

    if result:
        results.append(df.iloc[-1,4])

    if function_plot:
        x = np.arange(analysis_range[0],analysis_range[1],0.001)
        y = function(x)
        sns.lineplot(x=x, y=y)
        plt.title('Function Plot')
        plt.grid(True)
        plt.show()

    if final_row:
        results.append(df.iloc[-1,:])

    if dataframe:
        results.append(df)

    if graph:
        sns.lineplot(data=df[['a', 'b', 'c']])
        plt.xlabel('Iteration')
        plt.ylabel('Value')
        plt.title('Iteration vs a,b,c')
        plt.grid(True)
        plt.show()

    if not results:
        return df.iloc[-1,:]

    if len(results) == 1:
        return results[0]
    else:
        return tuple(results)
    

def bisection_method(max_iter=50, a=None,b=None,function=None, tol=0, function_plot=False, analysis_range=None, dataframe=False, graph=False, final_row=False, result=True, verbose=True):

    if function is None:
        raise ValueError("Provide a function.")

    if a is None or b is None:
        raise ValueError("Provide a and b. a and b must be in the continuous portion of the graph.")

    if function(a) * function(b) > 0:
        raise ValueError("f(a)*f(b) > 0. Provide a and b such that f(a)*f(b) < 0")

    if analysis_range is not None and not function_plot:
        raise ValueError("analysis_range is invalid when function_plot=False.")

    if analysis_range is None:
        analysis_range = [-100, 100]

    array_list = []
    for i in range(max_iter):

        mean = (a + b) / 2
        f_mean = function(mean)
        f_a = function(a)

        array_list.append(np.array([a,b,mean,function(a),function(b),f_mean]))

        if f_mean == 0:
            a = mean
            b = mean
        elif f_a * f_mean < 0:
            a = array_list[-1][0]
            b = mean
        else:  
            a = mean
            b = array_list[-1][1]

        if abs(b-a) <= tol:
            break


    if verbose:
        iterator = tqdm(range(max_iter), desc="Bisection", unit="iter", dynamic_ncols=True)
        for i in iterator:
            iterator.set_postfix({"a": a, "b": b, "mean": mean, "f(a)": function(a), "f(b)": function(b), "converge": f_mean})

    
    df = pd.DataFrame(array_list, columns=(['a','b','mean','f(a)','f(b)','converge']))

    results = []


    if result:
        results.append(df.iloc[-1,2])

    if function_plot:
        x = np.arange(analysis_range[0],analysis_range[1],0.001)
        y = function(x)
        sns.lineplot(x=x, y=y)
        plt.title('Function Plot')
        plt.grid(True)
        plt.show()

    if final_row:
        results.append(df.iloc[-1,:])

    if dataframe:
        results.append(df)

    if graph:
        sns.lineplot(data=df[['a', 'b']])
        plt.xlabel('Iteration')
        plt.ylabel('Value')
        plt.title('Iteration vs a and b')
        plt.grid(True)
        plt.show()

    if not results:
        return df.iloc[-1,:]

    if len(results) == 1:
        return results[0]
    else:
        return tuple(results)