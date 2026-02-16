# -*- coding: utf-8 -*-
"""
Created on Sat Dec 20 12:20:03 2025

@author: oyvinpet
"""
#%%

import numpy as np
import matplotlib.pyplot as plt

import sys
sys.path.append(r'C:\Cloud\OD_OWP\Work\Python\Github\plotops')

import plotops

#%% Test plot 2D

plt.close('all')

x1 = np.linspace(0, 10, 100)
x2 = np.linspace(0, 10, 400)

y1 = 20*np.cos(x1)+40
y2 = 20*np.sin(x2)+50

fig_layout=plotops.figure.layout(1,1)

fig_out = plotops.plot.plotxy(
    [x1, x2],
    [y1, y2],
    labels=['case A','case B'])

plotops.print.savefig(fig_out['fig'],'plot_test_1c','.',figsize=fig_layout['figsize'])

#%% Test plot 2D

plt.close('all')

x1 = np.linspace(0, 10, 100)
x2 = np.linspace(0, 10, 400)
x3 = np.linspace(0, 10, 200)

y1 = np.vstack((20*np.cos(x1),30*np.cos(x1)**4))
y2 = np.vstack((20*np.sin(x2),30*np.sin(x2)**4))
y3 = np.vstack((-10*np.sin(3*x3)+50,20*np.sin(2*x3)))

fig_layout = plotops.figure.layout(1,2)
#fig_layout = plotops.figure.layout(2,1)

fig_out= plotops.plot.plotxy(
    [x1, x2, x3],
    [y1, y2, y3],
    labels=['Case A','Case B','Case C'],
    xlabel='t [s]',
    ylabel=[f'$Y_{i+1}$ [kN]' for i in range(2)],
    legend=True,
    cursor=True,
    ncols=2,
    layout_kwargs=fig_layout)

plotops.print.savefig(fig_out['fig'],'plot_test_2c','.',figsize=fig_layout['figsize'])

#%% Layout from 1 column to multiple

plt.close('all')

x = np.linspace(0, 10, 100)

y1 = 20*np.random.randn(6, 100)
y2 = 20*np.random.rand(6, 100)+10

fig_layout = plotops.figure.layout(2,3)

fig_out=  plotops.plot.plotxy(
    x_list=[x],
    y_list=[y1, y2],
    ncols=3,
    layout_kwargs=fig_layout
)

plotops.print.savefig(fig_out['fig'],'plot_test_3c','.',figsize=fig_layout['figsize'])

#%% Test plot 3D rectangular

plt.close('all')

x=np.linspace(0,2,10)
A=np.zeros([2,3,10])

A[0,0,:]=10*np.exp(-x)
A[0,1,:]=np.exp(-x)
A[0,2,:]=20*np.exp(-x)
A[1,0,:]=np.exp(-0.1*x**2)
A[1,1,:]=20*np.exp(-x)
A[1,2,:]=30*np.exp(-x)

B=A+2

x2=np.linspace(0,2,20)

C=np.zeros([2,3,20])

C[0,0,:]=10*np.exp(-x2*2)
C[0,1,:]=np.exp(-x2*2)
C[0,2,:]=20*np.exp(-x2*2)
C[1,0,:]=np.exp(-x2**2)
C[1,1,:]=20*np.exp(-x2*2)
C[1,2,:]=30*np.exp(-x2*2)


fig_layout=plotops.figure.layout(2,3)

fig_out=plotops.plot.plot3d([x,x,x2],[A,B,C],
                    xlabel='f [Hz]',
                    linewidth=[1,2,1],
                    labels=['Data','Num','Test series'],
                    linestyle=['-','--','-'],
                    ylog=True,
                    suptitle='Main title',
                    layout_kwargs=fig_layout)

# plotops.figure.size(fig)

plotops.print.savefig(fig_out['fig'],'plot_test_4c','.',figsize=fig_layout['figsize'])


#%%

C=np.random.randn(6,6)
C=C@C.T+np.eye(6)

plotops.plot.corr(
    C,
    labels=None,
    ax=None,
    cmap='coolwarm',
    show_values=True,
    value_fmt='{:.2f}',
    colorbar=True,
    title='Correlation matrix',
)

#%% Multiple figures

plt.close('all')

x = np.linspace(0, 10, 100)

y1 = 20*np.random.randn(14, 100)+100
y2 = 20*np.random.rand(14, 100)+110

fig_layout=plotops.figure.layout(2,3)

fig_out=plotops.plot.plotxy(
    x_list=[x],
    y_list=[y1, y2],
    legend=True,
    ncols=1
)

