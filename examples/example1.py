#%%

import numpy as np
import matplotlib.pyplot as plt

import sys
sys.path.append(r'C:\Cloud\OD_OWP\Work\Python\Github\plotops')

import plotops

#%% Test plot row (single)

plt.close('all')

x1 = np.linspace(0, 10, 100)
x2 = np.linspace(0, 10, 400)

y1 = 20*np.cos(x1)+40
y2 = 20*np.sin(x2)+50

fig_layout=plotops.figure.layout(1,1)

fig_out = plotops.plot.plotxy(
    [x1, x2],
    [y1, y2],
    labels=['Case A','Case B'])

# plotops.print.savefig(fig_out['fig'],'plot_example_1','.',figsize=fig_layout['figsize'],formats=['pdf' , 'png'])

#%% Test plot row (multiple)

plt.close('all')

x1 = np.linspace(0, 10, 100)
x2 = np.linspace(0, 10, 400)
x3 = np.linspace(0, 10, 200)

y1 = np.vstack((2*np.cos(x1),3*np.cos(x1)**4))
y2 = np.vstack((2*np.sin(x2)+5,3*np.sin(x2)**4))
y3 = np.vstack((np.sin(2*x3)-5,2*np.sin(2*x3)))

fig_layout = plotops.figure.layout(2,1)

fig_out= plotops.plot.plotxy(
    [x1, x2, x3],
    [y1, y2, y3],
    labels=['Case A','Case B','Case C'],
    xlabel='t [s]',
    ylabel=[f'$Y_{i+1}$ [kN]' for i in range(2)],
    ncols=1,
    layout_kwargs=fig_layout)

plotops.print.savefig(fig_out['fig'],'plot_example_2','.',figsize=fig_layout['figsize'],formats=['pdf' , 'png'])

#%% Test plot row (multiple, with restack)

plt.close('all')

x = np.linspace(0, 10, 100)

y1 = 20*np.random.randn(6, 100)
y2 = 20*np.random.rand(6, 100)+10

fig_layout = plotops.figure.layout(2,3)

fig_out=  plotops.plot.plotxy(
    x_list=[x],
    y_list=[y1, y2],
    ncols=3,
    suptitle='Main title',
    legend=False,
    layout_kwargs=fig_layout
)

plotops.print.savefig(fig_out['fig'],'plot_example_3','.',figsize=fig_layout['figsize'],formats=['pdf' , 'png'])

#%% Test plot 3D

plt.close('all')

x=np.linspace(0,2,100)
A=np.zeros([2,3,100])

A[0,0,:]=1e1*np.exp(-x)
A[0,1,:]=1e2*np.exp(-2*x)
A[0,2,:]=1e3*np.exp(-3*x)
A[1,0,:]=1e1*np.exp(-x)
A[1,1,:]=1e1*np.exp(-2*x)
A[1,2,:]=1e1*np.exp(-3*x)

B=A+2.0

x2=np.linspace(0,2,200)

C=np.zeros([2,3,200])

C[0,0,:]=1e1*np.exp(-x2**2)
C[0,1,:]=1e2*np.exp(-x2-x2**2)
C[0,2,:]=1e3*np.exp(-x2-x2**2)
C[1,0,:]=1e1*np.exp(-x2**0.5)
C[1,1,:]=1e1*np.exp(-2*x2**0.5)
C[1,2,:]=1e1*np.exp(-3*x2**0.5)

fig_layout=plotops.figure.layout(2,3)

fig_out=plotops.plot.plot3d([x,x,x2],[A,B,C],
                    xlabel='f [Hz]',
                    linewidth=[1,2,1],
                    labels=['Data','Num','Test series'],
                    linestyle=['-','--','-'],
                    ylog=True,
                    layout_kwargs=fig_layout)

# plotops.figure.size(fig)

plotops.print.savefig(fig_out['fig'],'plot_example_4','.',figsize=fig_layout['figsize'],formats=['pdf' , 'png'])


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
